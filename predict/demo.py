# -*- coding: utf-8 -*-

import HuobiServices as hb
"""
说明：目前使用的是我的账户(可在Utils.py修改)
	ACCESS_KEY = "204e335a-3208ae52-75d34260-1068a"
	SECRET_KEY = "51e0753d-23e60931-1f60f52c-4fa9b"
"""

"""
    :param symbol
    :param period: 可选值：{1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
    :param size: 可选值： [1,2000]
    :return:
"""
data = hb.get_kline('btcusdt', '15min', size=2000)
data['data'].reverse() #取出来时间顺序是倒的，故需转回来
hist = pd.DataFrame(data['data'])
hist = hist.set_index('id')
hist.index = pd.to_datetime(hist.index, unit='s')
hist_t = hist[:-1]     #去掉最后一个数据
target_col = 'close'

#其他使用例程在HuobiService.py中有详细说明