import pandas as pd
import talib
import numpy as np
import os
import matplotlib.pyplot as plt
import random
from futures import Account

from pylab import mpl
from futures import SECURITY_INFO

mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 指定默认字体：解决plot不能显示中文问题
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

"""
海龟交易法则
海龟交易法则——短线(修改）

海龟交易法则属于趋势跟随系统，重点在于资金管理
该系统的核心在于每次交易用2%的风险，逐步加仓，扑捉趋势
多市场交易，降低资金回撤率

真实波动幅度 = MAX(H-L,H-PDC,PDC-L)
               H：  当日最高价
               L：  当日最低价
               PDC：前一日收盘价

           N = (19*PDN+TN)/20
               PDN：前一日的N值
               TR：当日的真实波动幅度

头寸规模 = 账户的1%/(N*每一点价值)

头寸的限制：  1.单个市场上限                 3个 (原版为4个)
            2.高度关联的多个市场            6个（取消）
            3.松散关联的多个市场           10个（取消）
            4.单个方向（多头或空头）        12个（取消）

入市策略：    1.突破20日高低点（忽略上一次是盈利的突破）
            2.突破55日高低点（无条件开仓，为20日忽略的补漏）

逐步建仓：    1.在突破点建立1个头寸
            2.按0.5N的价格间隔逐步开仓扩大头寸，直至达到上限
            3.开盘跳空越过突破点时直接建立1个头寸

止损标准：    1.最后一次建立头寸的价位减2N为止损点（跳空头寸除外）
            2.达到止损位时整体头寸止损（跳空头寸除外）
            3.不是在原定价位开仓的头寸 止损位=开仓价位-2N
            4.价格突破1.5N位置时，止损位=最后开仓价位-1.5N

备选止损：    1.每次建立头寸时 止损位=开仓价位-0.5N
            2.每个头寸有不同的止损位
            3.一个头寸止损后，价格恢复至开仓位将重新建立该头寸

退出策略：    1.多头跌破10日低点
            2.空头超过10日高点
            3.所有头寸单位都要退出

其他规则：    1.下单时采用限价单，不要用市价单
            2.市场急变的情况，待市场稳定后再下单
            3.选取主力合约，成交量大的合约
            4.信号同时出现时，在最强势的市场买多，最弱的市场卖空
            5.(当前价-3个月前价格)/N   越大越强，越小越弱
            6.除非远月合约趋势相同，否则不要滚动合约
            7.在成交量没有大幅萎缩前滚动合约
            8.选取尽可能多的不相干的市场交易
            9.选定市场后就不要轻易退出该市场

输入： 
a.add_order('螺纹钢', 'RB1910', -1, 1020, 10)
M8888.XDCE
"""


class Turtle(Account):
    # ahand_num = 10  # 当前品种每手数量
    stop_loss = 0.01  # 每个头寸最大亏损
    per_cash = 1
    # MAX_POS = 12
    # securityName = '棕榈油'  #
    # security = 'P8888'
    ATRTIME = 20  # N=20
    A_POS_COUNT = 4
    __klineList = pd.DataFrame()

    # __kline = pd.DataFrame()
    # side = 0  # 1多 / -1空
    # holding = 0  # 记录总共持有多少手
    # posSize = 0  # 头寸规模，即每次开仓手数
    # level = 0  # 记录第几个头寸 0表示空仓
    # openTime = ''  # 开仓日期
    time = ''  # 当前K线时间
    timeIndex = 0  # 当前时间所在行

    # atr = 0  # 开仓日的ATR

    def __init__(self, klineList, money):
        super(Turtle, self).__init__(money)
        self.__klineList = klineList
        # self.__kline = kline
        self.timeIndex = 0
        self.time = klineList[0][1]['kline'].index[0]
        # self.add_atr()
        # self.add_top()
        # self.add_low()
        for k in self.__klineList:
            # 加入atr
            k[1]['kline']['atr'] = round(
                talib.ATR(k[1]['kline']['high'], k[1]['kline']['low'], k[1]['kline']['close'], timeperiod=self.ATRTIME),
                0)

            # 加入20日高点，10日高点
            k[1]['kline']['high20'] = k[1]['kline']['high'].rolling(window=20).max()
            k[1]['kline']['high20'].fillna(
                value=pd.Series.cummax(k[1]['kline']['high']), inplace=True)
            k[1]['kline']['high10'] = k[1]['kline']['high'].rolling(window=10).max()
            k[1]['kline']['high10'].fillna(
                value=pd.Series.cummax(k[1]['kline']['high']), inplace=True)

            # 加入20日低点，10日低点
            k[1]['kline']['low20'] = k[1]['kline']['low'].rolling(window=20).min()
            k[1]['kline']['low20'].fillna(
                value=pd.Series.cummin(k[1]['kline']['low']), inplace=True)
            k[1]['kline']['low10'] = k[1]['kline']['low'].rolling(window=10).min()
            k[1]['kline']['low10'].fillna(
                value=pd.Series.cummin(k[1]['kline']['low']), inplace=True)

            k[1]['posSize'] = 0  # 记录该品种头寸规模，即每次开仓手数
            k[1]['holding'] = 0  # 记录该品种总共持有多少手
            k[1]['level'] = 0  # 记录该品种第几个头寸 0表示空仓
            k[1]['openTime'] = ''  # 记录该品种开仓日期
            k[1]['side'] = ''  # 1多 / -1空
            k[1]['count_loss'] = 0  # 止损次数
            k[1]['count_win'] = 0  # 盈利次数
            k[1]['loss'] = 0  # 止损了几个ATR
            k[1]['win'] = 0  # 盈利了几个ATR
            k[1]['maxATR'] = k[1]['kline']['atr'].max()

    def next_time(self):
        self.timeIndex += 1
        if self.timeIndex < self.__klineList[0][1]['kline'].shape[0]:
            self.time = self.__klineList[0][1]['kline'].index[self.timeIndex]
            return True
        else:
            return False

    def run(self):
        up_pos_count = 0
        down_pos_count = 0
        min_available = 99999999999
        money = pd.DataFrame()
        money.loc[self.time, 'cash'] = self.cash()  # 期初资金
        # self.__klineList[0][1]['cash'] = self.cash()
        # num=len(self.__klineList[0][1]['kline'].index)
        # print(self.__klineList[0][1]['kline'].loc[]['atr'])
        for i in self.__klineList[0][1]['kline'].values:
            self.next_time()
            # print('up_pos_count',up_pos_count,'down_pos_count',down_pos_count)

            for k in klineList:
                if self.cash() < 0:
                    print(k[0], '亏完')
                    return money
                money.loc[self.time, 'cash'] = self.cash()  # 记录当日总资金
                buy_price = k[1]['kline'].loc[self.time, 'high20']
                sell_price = k[1]['kline'].loc[self.time, 'low20']

                atr = k[1]['kline'].loc[self.time, 'atr']  # 暂时记录当日该品种的ATR

                if np.isnan(atr):
                    continue
                if k[1]['posSize'] == 0:
                    k[1]['posSize'] = self.per_cash * int(
                        self.cash() * self.stop_loss / (atr * SECURITY_INFO[k[0]]['trading_unit']))
                # print(self.time, ' 总资金:', self.cash(), k[0] + '持仓:', k[1]['holding'], '  ATR:', atr, '头寸规模:',
                #       k[1]['posSize'],
                #       '可用资金:', self.available(), '保证金:', self.margin())

                temp_postion = self.get_position(k[1]['security'])
                oldPos = 0
                newPos = 0
                if temp_postion is not None:
                    oldPos = temp_postion['holding'] // k[1]['posSize'] * temp_postion['side']

                profit = self.refresh(k[1]['security'],
                                      k[1]['kline'].loc[self.time, 'high'],
                                      k[1]['kline'].loc[self.time, 'low'],
                                      k[1]['kline'].loc[self.time, 'close'],
                                      up_pos_count,
                                      down_pos_count,
                                      self.time)

                temp_postion = self.get_position(k[1]['security'])
                if temp_postion is not None:
                    newPos = temp_postion['holding'] // k[1]['posSize'] * temp_postion['side']
                if newPos != oldPos:
                    if oldPos > 0:
                        up_pos_count = up_pos_count - oldPos
                    elif oldPos < 0:
                        down_pos_count = down_pos_count - oldPos

                    if newPos >0:
                        up_pos_count = up_pos_count+ newPos
                    elif newPos <0:
                        down_pos_count = down_pos_count +newPos

                if profit is not None:
                    if profit > 0:
                        k[1]['count_win'] += 1  # 盈利次数
                        k[1]['win'] = round(k[1]['win'] + profit / k[1]['posSize'] / (
                                k[1]['atr'] * SECURITY_INFO[k[0]]['trading_unit']), 3)  # 盈利了几个ATR
                        # print(k[0], '盈利', round(profit / k[1]['posSize']/ (k[1]['atr'] * SECURITY_INFO[k[0]]['trading_unit']), 3), 'N')
                    elif profit < 0:
                        k[1]['count_loss'] += 1  # 止损次数
                        k[1]['loss'] = round(k[1]['loss'] + profit / k[1]['posSize'] / (
                                k[1]['atr'] * SECURITY_INFO[k[0]]['trading_unit']), 3)  # 止损了几个ATR
                        # print(k[0], '止损', round(profit/ k[1]['posSize']/ (k[1]['atr'] * SECURITY_INFO[k[0]]['trading_unit']), 3), 'N')
                position = self.get_position(k[1]['security'])
                orderList = self.get_order()
                if position is not None:
                    # 海龟系统里记录的持仓数目与账户内不同，说明有新交易
                    if k[1]['holding'] != position['holding']:
                        k[1]['holding'] = position['holding']
                        k[1]['side'] = position['side']
                        k[1]['level'] = k[1]['holding'] // k[1]['posSize']
                        k[1]['atr'] = k[1]['kline'].loc[position['last_time'], 'atr']

                        for orderItem in orderList[::-1]:
                            # 去掉反向挂单
                            if orderItem['security'] == k[1]['security'] and orderItem['side'] != k[1]['side']:
                                self.del_order(orderItem)

                    # 删除止损单
                    for orderItem in orderList[::-1]:
                        # 删掉止损挂单
                        if orderItem['security'] == k[1]['security'] and orderItem['side'] == 0:
                            self.del_order(orderItem)

                    # 设立止损单
                    if k[1]['side'] > 0:
                        stop_price = max(k[1]['kline'].loc[self.time, 'low10'],
                                         position['opening_price'] + (k[1]['level'] - 1) * 0.25 * k[1]['atr'] - 2 *
                                         k[1]['atr']
                                         )
                        stop_price = int(round(stop_price))
                        self.add_order(k[0], k[1]['security'], 0, stop_price, position['holding'], self.time)
                    elif k[1]['side'] < 0:
                        stop_price = min(k[1]['kline'].loc[self.time, 'high10'],
                                         position['opening_price'] - (k[1]['level'] - 1) * 0.25 * k[1]['atr'] + 2 *
                                         k[1]['atr']
                                         )

                        stop_price = int(round(stop_price))
                        self.add_order(k[0], k[1]['security'], 0, stop_price, position['holding'], self.time)

                elif k[1]['side'] != 0:
                    # 清空仓位记录
                    k[1]['side'] = 0
                    k[1]['holding'] = 0  # 记录总共持有多少手
                    k[1]['level'] = 0  # 记录第几个头寸 0表示空仓
                    k[1]['openTime'] = ''  # 开仓日期
                    k[1]['atr'] = 0

                if k[1]['holding'] <= 0:

                    if money.loc[self.time, 'cash'] >= 0.9 * money['cash'].max():
                        self.per_cash = 1
                    elif money.loc[self.time, 'cash'] >= 0.8 * money['cash'].max():
                        self.per_cash = 0.5
                    elif money.loc[self.time, 'cash'] >= 0.7 * money['cash'].max():
                        self.per_cash = 0.2
                    elif money.loc[self.time, 'cash'] >= 0.6 * money['cash'].max():
                        self.per_cash = 0.1
                    elif money.loc[self.time, 'cash'] >= 0.5 * money['cash'].max():
                        self.per_cash = 0.1
                    elif money.loc[self.time, 'cash'] >= 0.4 * money['cash'].max():
                        self.per_cash = 0.1
                    elif money.loc[self.time, 'cash'] >= 0.3 * money['cash'].max():
                        self.per_cash = 0.05
                    elif money.loc[self.time, 'cash'] >= 0.2 * money['cash'].max():
                        self.per_cash = 0.05
                    elif money.loc[self.time, 'cash'] >= 0.1 * money['cash'].max():
                        self.per_cash = 0.05
                    elif money.loc[self.time, 'cash'] >= 0 * money['cash'].max():
                        self.per_cash = 0.05
                    # print('资金比例', self.per_cash)

                    self.clear_order(k[1]['security'])
                    # 头寸规模 = 账户的1 % / (N * 每一点价值)
                    k[1]['posSize'] = int(self.per_cash*self.cash() * self.stop_loss / (atr * SECURITY_INFO[k[0]]['trading_unit']))
                    # print(self.time, ' 总资金:', self.cash(), 'ATR:', atr, '头寸规模:', k[1]['posSize'])
                    if k[1]['posSize'] > 0:
                        for j in range(self.A_POS_COUNT):
                            n = int(round(0.5 * atr * j, 0))
                            buy_price = int(buy_price)
                            sell_price = int(sell_price)
                            self.add_order(k[0], k[1]['security'], 1, buy_price + n, k[1]['posSize'], self.time)
                            self.add_order(k[0], k[1]['security'], -1, sell_price - n, k[1]['posSize'], self.time)

                min_available = min(min_available, self.available())
                # if min_available < 0:
                #     print(self.time, '爆仓')
                #     return money
        #
        print('账户最大值:', money['cash'].max(), '账户最小值:', money['cash'].min(), '期末账户余额:',
              money['cash'].values[-1])
        # money['cash'] = money['cash'] / money['cash'][0]
        # money['cash'].plot(kind='line', title='资金曲线')
        # plt.show()
        win = 0
        loss = 0
        count_win = 0
        count_loss = 0
        for k in self.__klineList:
            loss = round(loss+k[1]['loss'],3)
            win = round(win+k[1]['win'],3)
            count_win = round(count_win + k[1]['count_win'], 3)
            count_loss = round(count_loss + k[1]['count_loss'], 3)

        print('止损次数', count_loss, '盈利次数', count_win, '止损', loss, '盈利', win, '最小可用资金', min_available)
        return money

    def add_top(self):
        for k in self.__klineList:
            k[1]['kline']['high20'] = k[1]['kline']['high'].rolling(window=20).max()
            k[1]['kline']['high20'].fillna(
                value=pd.Series.cummax(k[1]['kline']['high']), inplace=True)
            k[1]['kline']['high10'] = k[1]['kline']['high'].rolling(window=10).max()
            k[1]['kline']['high10'].fillna(
                value=pd.Series.cummax(k[1]['kline']['high']), inplace=True)

    def add_low(self):
        for k in self.__klineList:
            k[1]['kline']['low20'] = k[1]['kline']['low'].rolling(window=20).min()
            k[1]['kline']['low20'].fillna(
                value=pd.Series.cummin(k[1]['kline']['low']), inplace=True)
            k[1]['kline']['low10'] = k[1]['kline']['low'].rolling(window=10).min()
            k[1]['kline']['low10'].fillna(
                value=pd.Series.cummin(k[1]['kline']['low']), inplace=True)

        # self.__kline['low20'] = self.__kline['low'].rolling(window=20).min()
        # self.__kline['low20'].fillna(value=pd.Series.cummin(self.__kline['low']), inplace=True)
        # self.__kline['low10'] = self.__kline['low'].rolling(window=10).min()
        # self.__kline['low10'].fillna(value=pd.Series.cummin(self.__kline['low']), inplace=True)

    # def orderSign(self, orderTime=openTime):
    #
    #     buy = self.__kline.loc[orderTime]['high']
    #     clo_buy = self.__kline.loc[orderTime]['high'] - 2 * self.__kline.loc[orderTime]['ATR']
    #
    #     sell = self.__kline.loc[orderTime]['low']


# klineList = pd.DataFrame()
# klineList['螺纹钢']=pd.DataFrame({'security':'RB8888'})
# klineList = [
#     ['螺纹钢', {'security': 'RB8888'}],
#     ['棕榈油', {'security': 'P8888'}],
#     ['豆粕', {'security': 'M8888'}],
#     ['PTA', {'security': 'TA8888'}]
# ]
# print(klineList)
# klineList=pd.DataFrame(klineList)
i = 0
klineList = []
for info_key in SECURITY_INFO.keys():
    # klineList = []
    # info_key='白银'
    # if info_key  in ['螺纹钢','热轧卷板','棉花']:
    #       continue
    # if random.randint(0, 10) > 5:
    #     continue

    file = 'data/{}.csv'.format(SECURITY_INFO[info_key]['jc'] + '8888')
    if os.path.exists(file):
        print(info_key)
        klineList.append([info_key, {'security': SECURITY_INFO[info_key]['jc'] + '8888'}])
        kline = pd.read_csv(file, index_col=0)
        kline = kline[['close', 'high', 'low']]
        klineList[len(klineList) - 1][1]['kline'] = kline
turtle = Turtle(klineList, 1000000)
money = turtle.run()

# money['cash'] = money['cash'] / money['cash'][0]
# money['cash'].plot(kind='line', title='资金曲线')
# plt.show()
# print(info_key, '账户最大值:', money['cash'].max(), '账户最小值:', money['cash'].min(), '期末账户余额:',
#       money['cash'].values[-1])
# print(money)
# print(info_key)

# print('账户最大值:', money['cash'].max())
# print('账户最小值:', money['cash'].min())
# print('期初账户:', money['cash'].values[0])
# print('期末账户余额:', self.cash())
