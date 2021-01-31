import pandas as pd
import talib
import numpy as np
import futures
import matplotlib.pyplot as plt

from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei']    # 指定默认字体：解决plot不能显示中文问题
mpl.rcParams['axes.unicode_minus'] = False           # 解决保存图像是负号'-'显示为方块的问题



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


class Turtle:
    ahand_num= 10  #当前品种每手数量
    stop_loss = 0.02 #每个头寸最大亏损
    A_POS_COUNT =3
    securityName = '螺纹钢'   #
    security = 'RB8888'
    ATRTIME = 20  # N=20
    __kline = pd.DataFrame()
    side = 0  # 1多 / -1空
    holding = 0  # 记录总共持有多少手
    posSize = 0  # 头寸规模，即每次开仓手数
    level = 0  # 记录第几个头寸 0表示空仓
    openTime = ''  # 开仓日期
    time = ''  # 当前K线时间
    timeIndex = 0  # 当前时间所在行
    atr = 0   #开仓日的ATR

    def __init__(self, kline: pd.DataFrame):
        self.__kline = kline
        self.timeIndex = 0
        self.time = self.__kline.index[0]
        self.add_atr()
        self.add_top()
        self.add_low()
        # print(self.__kline.tail(20))

    def next_time(self):
        self.timeIndex += 1
        if self.timeIndex < self.__kline.shape[0]:
            self.time = self.__kline.index[self.timeIndex]
            return True
        else:
            return False

    def run(self,money):
        fa = futures.Account(money)
        self.__kline['cash']=money
        for i in self.__kline.values:
            self.next_time()
            self.__kline.loc[self.time,'cash']=fa.cash()
            buy_price = self.__kline.loc[self.time, 'high20']
            sell_price = self.__kline.loc[self.time, 'low20']
            atr = self.__kline.loc[self.time, 'atr']  #保存昨天的ATR

            if np.isnan(atr):
                continue
            if self.posSize == 0:
                self.posSize = int(fa.cash() * self.stop_loss / (atr * self.ahand_num))
            print(self.time, ' 总资金:', fa.cash(), '  持仓:', self.holding, '  ATR:', atr, '头寸规模:', self.posSize,'可用资金:',fa.available(),'保证金:',fa.margin())

            fa.refresh(self.security,
                       self.__kline.loc[self.time, 'high'],
                       self.__kline.loc[self.time, 'low'],
                       self.__kline.loc[self.time, 'close'],
                       self.time)
            position = fa.get_position(self.security)
            orderList = fa.get_order()
            if position is not None:
                # 海龟系统里记录的持仓数目与账户内不同，说明有新交易
                if self.holding != position['holding']:
                    self.holding = position['holding']
                    self.side = position['side']
                    self.level = self.holding // self.posSize
                    self.atr = self.__kline.loc[position['last_time'],'atr']

                    for orderItem in orderList[::-1]:
                        # 去掉反向挂单
                        if orderItem['security'] == self.security and orderItem['side'] != self.side:
                            fa.del_order(orderItem)


                #删除止损单
                for orderItem in orderList[::-1]:
                    # 删掉止损挂单
                    if orderItem['security'] == self.security and orderItem['side'] == 0:
                        fa.del_order(orderItem)

                #设立止损单
                if self.side > 0:
                    stop_price = max(self.__kline.loc[self.time, 'low10'],
                                     position['opening_price'] + (self.level - 1) * 0.25 * self.atr - 2 * self.atr
                                     )
                    stop_price = int(round(stop_price))
                    fa.add_order(self.securityName, self.security, 0, stop_price, position['holding'], self.time)
                elif self.side < 0:
                    stop_price = min(self.__kline.loc[self.time, 'high10'],
                                     position['opening_price'] - (self.level - 1) * 0.25 * self.atr + 2 * self.atr
                                     )

                    stop_price = int(round(stop_price))
                    fa.add_order(self.securityName, self.security, 0, stop_price, position['holding'], self.time)

            elif self.side != 0:
                # 清空仓位记录
                self.side = 0
                self.holding = 0  # 记录总共持有多少手
                self.level = 0  # 记录第几个头寸 0表示空仓
                self.openTime = ''  # 开仓日期
                self.atr = 0

            if self.holding <= 0:
                fa.clear_order()
                #头寸规模 = 账户的1 % / (N * 每一点价值)
                self.posSize = int(fa.cash() *self.stop_loss /(atr * self.ahand_num))

                for j in range(self.A_POS_COUNT):
                    n = int(round(0.5 * atr * j,0))
                    buy_price=int(buy_price)
                    sell_price=int(sell_price)
                    fa.add_order(self.securityName, self.security, 1, buy_price + n, self.posSize, self.time)
                    fa.add_order(self.securityName, self.security, -1, sell_price - n, self.posSize, self.time)

        print('账户最大值:',self.__kline['cash'].max())
        print('账户最小值:',self.__kline['cash'].min())
        print('期初账户:', money)
        print('期末账户余额:', fa.cash())
        self.__kline['cash']=self.__kline['cash']/money
        self.__kline['cash'].plot(kind='line',title='资金曲线 %')
        # self.__kline.index, self.__kline['cash'].values, label="总资金", color='blue')
        plt.show()
        return fa

    def add_atr(self):
        self.__kline['atr'] =round(talib.ATR(kline['high'], kline['low'], kline['close'], timeperiod=self.ATRTIME),0)

    def add_top(self):
        self.__kline['high20'] = self.__kline['high'].rolling(window=20).max()
        self.__kline['high20'].fillna(value=pd.Series.cummax(self.__kline['high']),inplace=True)
        self.__kline['high10'] = self.__kline['high'].rolling(window=10).max()
        self.__kline['high10'].fillna(value=pd.Series.cummax(self.__kline['high']), inplace=True)

    def add_low(self):
        self.__kline['low20'] = self.__kline['low'].rolling(window=20).min()
        self.__kline['low20'].fillna(value=pd.Series.cummin(self.__kline['low']), inplace=True)
        self.__kline['low10'] = self.__kline['low'].rolling(window=10).min()
        self.__kline['low10'].fillna(value=pd.Series.cummin(self.__kline['low']), inplace=True)
    def orderSign(self, orderTime=openTime):

        buy = self.__kline.loc[orderTime]['high']
        clo_buy = self.__kline.loc[orderTime]['high'] - 2 * self.__kline.loc[orderTime]['ATR']

        sell = self.__kline.loc[orderTime]['low']




# arr= talib.ATR(np.array([8,9,10]),np.array([5,6,1]),np.array([7,6,5]), timeperiod=3)
# arr= np.array([1,23])
# print(arr)

kline = pd.read_csv('data/RB8888.csv', index_col=0)
kline= kline[['close', 'high', 'low']]
# dels = [0, 4, 5]
#
# kline.drop(kline.columns[dels], axis=1, inplace=True)
# # print(kline)
turtle = Turtle(kline)
a= turtle.run(100000)
print(a.cash())


