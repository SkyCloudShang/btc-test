import pandas as pd
import numpy as np, time
import requests,json, talib


short_win = 12    # 短期EMA平滑天数
long_win = 26    # 长期EMA平滑天数
macd_win = 9     # DEA线平滑天数


SIGNAL_SELL = 2   # 卖出信号
SIGNAL_BUY = 1  # 买进信号
SIGNAL_WAIT = 0   # 无动作
SIGNAL_BALANCE = -1  # 余额不足
TIME_STAMP = 14280  # 24/5 小时，当MACD一直处于买入WAIT时间超过该时间
                    # 则随机买入和卖出，保证至少5次的成交量
THRESHPLD_POS = 1  # MACD值大于该阈值则可卖出
THRESHPLD_PPASS = -1.5  # MACD值小于该阈值则买入

def get_history_data():
    """
    获取过去某个周期内的k线数据
    :return:
    """
    endpoint = 'https://min-api.cryptocompare.com/data/histoday'
    res = requests.get(endpoint + '?fsym=BTC&tsym=USD&limit=2000')
    return json.loads(res.content.decode('utf-8'))['Data']

def get_cur_price():
    """
    获取当前时刻价格
    :return:
    """
    pass


def get_cur_acount():
    """
    获取当前账户信息，主要是可用余额或者可用的币
    :return:
    """
    pass


def handle_data(price_list):
    price_list = get_history_data()
    print(price_list)
    p_list = []
    for i in price_list:
        p_list.append(i.get('close'))
    p_list = np.array(p_list)
    # talib计算MACD
    macd_tmp = talib.MACD(p_list, fastperiod=short_win, slowperiod=long_win, signalperiod=macd_win)
    macd_value = macd_tmp[2]
    # DIF = macd_tmp[0]
    # DEA = macd_tmp[1]
    # MACD = macd_tmp[2]
    # print(MACD[-1])

    # 判断MACD走向
    if macd_value[-1] > THRESHPLD_POS:
        if get_cur_acount() >= get_cur_price():
            return SIGNAL_BUY
        else:
            print("余额不足")
            return SIGNAL_BALANCE
    elif macd_value[-1] < THRESHPLD_PPASS:
        if get_cur_acount(): # 获取可卖出的比特币
            return SIGNAL_SELL
        else:
            print("账户内无币")
            return SIGNAL_BALANCE
    else:
        return SIGNAL_WAIT


def run():
    begin_time = time.time()
    while True:
        res = handle_data(get_history_data())
        if not res:  # 如果无动作
            end_time = time.time()
            if end_time - begin_time >= TIME_STAMP:
                if get_cur_acount():
                    begin_time = time.time()  # 重新计时
                    pass
                    # res = SIGNAL_SELL
                    # res = SIGNAL_BUY
                else:
                    res = SIGNAL_BALANCE
        make_deal(res)
        if res is not SIGNAL_WAIT:
            begin_time = time.time()  # 进行有效的交易后时间清零


def make_deal(signal):
    """
    交易函数
    :param signal: 交易信号
    :return:
    """
    pass

