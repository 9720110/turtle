import pandas as pd
import logging

SECURITY_INFO = {
    # '螺纹钢': dict(margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '棕榈油': dict(margin_rate=0.15, fees_rate=0.00000006, trading_unit=10),
    # '豆粕': dict(margin_rate=0.13, fees_rate=0.0001, trading_unit=10),
    # 'PTA': dict(margin_rate=0.11, fees_rate=0.00000006, trading_unit=5),
    '白银': dict(jc='AG', margin_rate=0.12, fees_rate=0.0001, trading_unit=15),
    '铝': dict(jc='AL', margin_rate=0.12, fees_rate=0.0001, trading_unit=5),
    # '黄金': dict(jc='AU', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '石油沥青': dict(jc='BU', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '铜': dict(jc='CU', margin_rate=0.12, fees_rate=0.0001, trading_unit=5),
    '燃料油': dict(jc='FU', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '热轧卷板': dict(jc='HC', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '镍': dict(jc='NI', margin_rate=0.12, fees_rate=0.0001, trading_unit=1),
    '铅': dict(jc='PB', margin_rate=0.12, fees_rate=0.0001, trading_unit=5),
    '螺纹钢': dict(jc='RB', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '天然橡胶': dict(jc='RU', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '锡': dict(jc='SN', margin_rate=0.12, fees_rate=0.0001, trading_unit=1),
    # '线材': dict(jc='WR', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '锌': dict(jc='ZN', margin_rate=0.12, fees_rate=0.0001, trading_unit=5),
    # '纸浆': dict(jc='SP', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '不锈钢': dict(jc='SS', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '苹果': dict(jc='AP', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '棉花': dict(jc='CF', margin_rate=0.12, fees_rate=0.0001, trading_unit=5),
    # '棉纱': dict(jc='CY', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '玻璃': dict(jc='FG', margin_rate=0.12, fees_rate=0.0001, trading_unit=20),
    # '绿豆': dict(jc='GN', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '粳稻谷': dict(jc='JR', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '晚籼稻': dict(jc='LR', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '甲醇': dict(jc='MA', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '普麦': dict(jc='PM', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '早籼稻': dict(jc='RI', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '菜籽粕': dict(jc='RM', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '菜籽油': dict(jc='OI', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '油菜籽': dict(jc='RS', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '硅铁': dict(jc='SF', margin_rate=0.12, fees_rate=0.0001, trading_unit=5),
    '锰硅': dict(jc='SM', margin_rate=0.12, fees_rate=0.0001, trading_unit=5),
    '白糖': dict(jc='SR', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    'PTA': dict(jc='TA', margin_rate=0.11, fees_rate=0.00000006, trading_unit=5),  # 已核对
    # '动力煤': dict(jc='ZC', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '强麦': dict(jc='WH', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '硬白小麦': dict(jc='WT', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '红枣': dict(jc='CJ', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '尿素': dict(jc='UR', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '纯碱': dict(jc='SA', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '短纤': dict(jc='PF', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '豆一': dict(jc='A', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    #  '豆二': dict(jc='B', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '胶合板': dict(jc='BB', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '玉米': dict(jc='C', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '玉米淀粉': dict(jc='CS', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '纤维板': dict(jc='FB', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '铁矿石': dict(jc='I', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '焦炭': dict(jc='J', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '鸡蛋': dict(jc='JD', margin_rate=0.12, fees_rate=0.0001, trading_unit=5),
    # '焦煤': dict(jc='JM', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    '聚乙烯': dict(jc='L', margin_rate=0.12, fees_rate=0.0001, trading_unit=5),
    '豆粕': dict(jc='M', margin_rate=0.13, fees_rate=0.0001, trading_unit=10),  # 已核对
    '棕榈油': dict(jc='P', margin_rate=0.15, fees_rate=0.00000006, trading_unit=10),  # 已核对
    '聚丙烯': dict(jc='PP', margin_rate=0.12, fees_rate=0.0001, trading_unit=5),
    '聚氯乙烯': dict(jc='V', margin_rate=0.12, fees_rate=0.0001, trading_unit=5),
    '豆油': dict(jc='Y', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '乙二醇': dict(jc='EG', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '苯乙烯': dict(jc='EB', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '液化石油气': dict(jc='PG', margin_rate=0.12, fees_rate=0.0001, trading_unit=10),
    # '生猪': dict(jc='LH', margin_rate=0.12, fees_rate=0.0001, trading_unit=10)
}

position = dict(
    securityName='螺纹钢1',
    side=1,
    holding='持仓手数',
    opening_price='开仓价格',
    current_price='现价',
    margin='保证金',
    last_time='此仓位挂单时间，注意不是成交时间'
)


class Account:
    ''' 账户类 '''
    global SECURITY_INFO
    __cash = 0  # 当前总资金
    __profit = 0  # 持仓浮盈/亏
    __available = 0  # 可用资金
    __margin = 0  # 全部持仓保证金
    __positionItem = {}  # 持仓 {'security品种代码RB1605' : {'品种名字 螺纹钢','side开仓方向 1多/-1空' , holding持仓手数 , open_price开仓价格 , new_price现价 , margin保证金}}
    __orderList = []  # 挂单列表[OrderItem()]  包括止损和加仓  ['security品种代码RB1605' , 'side 1开多/-1开空/0平仓' , amount交易手数 , price交易价格]
    max_margin = 100  # 最大保证金比例
    MAX_POS = 12

    def __init__(self, initCash):
        self.__cash = initCash
        self.__profit = 0  # 持仓浮盈/亏
        self.__available = 0  # 可用资金
        self.__margin = 0  # 全部持仓保证金
        self.__positionItem = {}  # 持仓 {'security品种代码RB1605' : {'品种名字 螺纹钢','side开仓方向 1多/-1空' , holding持仓手数 , open_price开仓价格 , new_price现价 , margin保证金}}
        self.__orderList = []  # 挂单列表[OrderItem()]  包括止损和加仓  ['security品种代码RB1605' , 'side 1开多/-1开空/0平仓' , amount交易手数 , price交易价格]
        self.max_margin = 100  # 最大保证金比例

    def _ref(self):
        # 内部刷新
        # 计算保证金总数，市值
        # 刷新保证金总数
        # 刷新总资金量
        totalMargin = 0
        totalProfit = 0
        # 遍历持仓
        for position in self.__positionItem.values():
            info = SECURITY_INFO[position['securityName']]
            totalMargin += position['margin']
            # 价差 spread
            spread = (position['current_price'] - position['opening_price']) * position['side']
            totalProfit += spread * position['holding'] * info['trading_unit']

        totalMargin = round(totalMargin, 2)
        totalProfit = round(totalProfit, 2)
        # 总资金 = 之前的总资金 + 收益（亏损为负数）
        self.__cash = round(self.__cash - self.__profit + totalProfit, 2)  # 更新总资金
        self.__profit = totalProfit  # 更新浮盈
        self.__margin = totalMargin  # 更新全部持仓保证金
        self.__available = round(self.__cash - self.__margin, 2)  # 更新可用资金

    def cash(self):
        '''返回总资金'''
        return self.__cash

    def available(self):
        '''返回可用资金'''
        return self.__available

    def margin(self):
        '''返回持仓占用资金'''
        totalMargin = 0
        for position in self.__positionItem.values():
            totalMargin += position['margin']
        self.__margin = round(totalMargin, 2)

        return self.__margin

    def position(self):
        '''返回持仓'''
        return self.__positionItem

    def profit(self):
        '''返回浮盈'''
        return self.__profit

    def get_order(self):
        '''返回挂单'''
        return self.__orderList

    def clear_order(self, security=None):
        if security is None:
            self.__orderList.clear()
        else:
            for orderItem in self.__orderList[::-1]:
                if orderItem['security'] == security:
                    self.__orderList.remove(orderItem)

    def _margin_cal(self, position):
        info = SECURITY_INFO[position['securityName']]
        margin = round(position['current_price'] * position['holding'] * info['margin_rate'] * info['trading_unit'], 2)
        return margin

    def get_position(self, security):
        if security in self.__positionItem.keys():
            position = self.__positionItem[security]
        else:
            position = None
        return position

    def _del_position(self, key):
        self.__positionItem.pop(key)

    def _add_position(self, key, position):
        self.__positionItem[key] = position

    def _ref_profit(self):
        profit = 0
        for position in self.__positionItem.values():
            profit += (position['current_price'] - position['opening_price']) * position['holding'] * position['side']
        self.__profit = round(profit, 2)

    def refresh(self, security='', high=-1, low=-1, close=-1, up_pos_count=0, down_pos_count=0, reftime=''):
        result = None
        # 遍历挂单列表比对各项参数，符合要求则交易
        self._ref()
        cash = self.__cash
        profit = self.__profit
        if security == '':
            return
        orderList = self.__orderList

        # 第一个for循环，先成交开仓挂单
        for orderItem in orderList[:]:
            if orderItem['security'] == security:
                if orderItem['side'] != 0:
                    if (low <= orderItem['price']) and (orderItem['price'] <= high):
                        if (orderItem['side']) > 0 and (up_pos_count >= self.MAX_POS):
                            continue
                        if (orderItem['side']) < 0 and (-down_pos_count >= self.MAX_POS):
                            continue
                        # 符合要求，成交,获得成交信息,用于返回
                        result = self.deal(orderItem)
                        if result == 0:
                            for o in orderList[:]:
                                if (o['security'] == security) and (o['side'] == 0):
                                    o['amount'] += orderItem['amount']

        # 第二个for循环，成交平仓挂单
        for orderItem in orderList[:]:
            if orderItem['security'] == security:
                if orderItem['side'] == 0:
                    if (low < orderItem['price']) and (orderItem['price'] < high):
                        result = self.deal(orderItem)
                    elif (self.get_position(security)['side'] > 0) and (orderItem['price'] > high):
                        orderItem['price'] = close
                        result = self.deal(orderItem)  # 持有多单的时候，跳空低开，挂单止损价格比最高价还高，无法正常止损，则以收盘价止损
                    elif (self.get_position(security)['side'] < 0) and (orderItem['price'] < low):
                        orderItem['price'] = close
                        result = self.deal(orderItem)  # 持有空单的时候，跳空高开，挂单止损价格比最低价还低，无法正常止损，则以收盘价止损

        # 如果输入的是已持仓品种，则刷新持仓的各项属性
        if security in self.__positionItem.keys():
            position = self.__positionItem[security]
            info = SECURITY_INFO[position['securityName']]
            position['current_price'] = close
            # 计算保证金
            position['margin'] = self._margin_cal(position)
            self.__positionItem[security] = position
            self._ref_profit()
            self.__cash = cash - profit + self.__profit

            self._ref()

        return result

    def deal(self, orderItem):
        # 交易函数
        # security 品种代码
        # price 交易价格
        # amount 交易手数
        # 1开平仓交易
        # 2更改挂单列表
        # 3更改账户各项属性
        # try:
        result = None
        info = SECURITY_INFO[orderItem['securityName']]
        if orderItem['side'] != 0:  # 如果不是平仓操作
            margin = orderItem['price'] * orderItem['amount'] * info['margin_rate'] * info[
                'trading_unit']  # 本次交易需要的保证金
            if (self.__available > margin) and (
                    (margin + self.__margin) / self.cash() <= self.max_margin):  # 如果可用资金大于所需保证金 则成交
                # 如果已有持仓
                if orderItem['security'] in self.__positionItem.keys():
                    position = self.__positionItem[orderItem['security']]
                    # print('$',position)
                    if position['side'] != orderItem['side']:
                        raise Exception('已有反向持仓，无法交易')
                    result = 0  # 返回值为0  表示加仓
                    # 临时保存交易后的总手数
                    temp = position['holding'] + orderItem['amount']
                    # 计算交易后的平均开仓价格
                    position['opening_price'] = round((position['opening_price'] * position['holding'] + orderItem[
                        'price'] * orderItem['amount']) / temp, 2)
                    position['holding'] = temp
                    position['current_price'] = orderItem['price']
                    position['margin'] = self._margin_cal(position)
                    self.__positionItem[orderItem['security']] = position
                    # print('加仓:', orderItem['security'], position['side'], orderItem['amount'],
                    #       orderItem['price'])
                    self.del_order(orderItem)
                    self._ref()
                else:
                    # 如果是新开仓
                    position = dict(
                        securityName=orderItem['securityName'],
                        side=orderItem['side'],
                        holding=orderItem['amount'],
                        opening_price=orderItem['price'],
                        current_price=orderItem['price'],
                        margin=0,
                        last_time=orderItem['time']
                    )
                    position['margin'] = self._margin_cal(position)
                    self._add_position(orderItem['security'], position)
                    # print('新开仓:', orderItem['security'], position['side'], position['holding'],
                    #       position['opening_price'])
                    self.del_order(orderItem)
                    self._ref()
                    # logging.info('新开仓 : ', position[''])


            else:
                # 可用资金不足，返回None
                return None
        else:

            # 如果是平仓交易
            if orderItem['security'] not in self.__positionItem.keys():
                raise Exception('没有持有该合约，无法平仓')
            elif orderItem['amount'] > self.__positionItem[orderItem['security']]['holding']:
                raise Exception('平仓手数大于持仓手数，无法平仓')
            # 取出一条持仓信息 key=即将交易的品种
            position = self.__positionItem[orderItem['security']]

            # 修改这条持仓信息的当前价格为交易价格
            position['current_price'] = orderItem['price']

            # 计算保证金
            position['margin'] = self._margin_cal(position)

            # 将修改好的持仓信息赋值回去
            self.__positionItem[orderItem['security']] = position

            # 刷新
            self._ref()

            # 计算价差 spread
            spread = (position['current_price'] - position['opening_price']) * position['side']
            # print(position['current_price'])
            # print(position['opening_price'])
            # print(position['side'])
            # print(spread)
            # #总资产=总资产 - 平仓部分浮盈 + 平仓收益
            # self.__cash = round(self.__cash -  + spread * orderItem['amount'], 2)

            # 把交易部分的浮盈去掉，并赋值给总浮盈
            # print(self.profit())
            self.__profit = round(self.__profit - spread * orderItem['amount'] * info['trading_unit'], 2)
            result = round(spread * orderItem['amount'] * info['trading_unit'], 2)
            # print(self.profit())
            if position['holding'] <= orderItem['amount']:
                self._del_position(orderItem['security'])
            else:
                temp = position['holding'] - orderItem['amount']
                position['opening_price'] = round((position['opening_price'] * position['holding'] - orderItem[
                    'price'] * orderItem['amount']) / temp, 2)
                position['holding'] = temp
                position['margin'] = self._margin_cal(position)
                self.__positionItem[orderItem['security']] = position
            # print('平仓:', orderItem['security'], orderItem['side'], orderItem['amount'],
            #       orderItem['price'])
            self.del_order(orderItem)
            self._ref()
            # print(self.profit())
            # self.del_order(orderItem)
        return result

    def del_order(self, orderItem):
        self.__orderList.remove(orderItem)

    def add_order(self, securityName, security, side, price, amount, time=''):
        # 生成挂单信息
        try:
            orderItem = dict(
                securityName=securityName,  # 品种名称
                security=security,  # 品种代码RB1605
                side=side,  # side 1开多/-1开空/0平仓
                price=price,  # 交易价格
                amount=amount,  # 交易手数
                time=time
            )
            # orderItem = pd.Series(orderItem)
            if (security not in self.__positionItem.keys()) and side == 0:
                logging.error('下单错误，没有持有该合约')
                # raise Exception('下单错误，没有持有该合约')
            else:
                self.__orderList.append(orderItem)
        except Exception as e:
            print('add_order', e)

#
# a = Account(100000)
# # aa.add_order('螺纹钢', 'RB1910', -1, 1020, 10)
#
# #
# # a.refresh()
# # a.refresh('RB1910', 1030, 800, 900, '')
# a.add_order('螺纹钢', 'RB1910', -1, 980, 20)
# print(a.order())
# # a.refresh('RB1910', 1030, 300, 600, '')
#
# # aa.add_order('螺纹钢', 'RB1910', 1, 980, 20)
# # a.refresh('RB1910', 1030, 300, 500, '')
#
# # a.refresh('RB1910', 1930, 500, 1600, '')
#
#
# print(orderItem)
# a.del_order(orderItem)
#
#
#
# print('*' * 20, '程序结束', '*' * 20)
# print('挂单列表：', a.order())
# print('总资产：', a.cash())
# print('可用余额：', a.available())
# print('浮盈：', a.profit())
#
# print('保证金：', a.margin())
# print('持仓:', a.position())
# print('挂单列表：', a.order())
# print('*' * 49)
