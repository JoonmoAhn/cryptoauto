import pyupbit
import numpy as np
import datetime


def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-XRP", count = 200, to = datetime.datetime.now()-datetime.timedelta(days=0))
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0005 # 매수, 매도시 각각 0.05%
    df['ror'] = np.where(df['high'] > df['target'],
                         (df['close'] - (df['target'] + df['close'])*fee) / df['target'],
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror


for k in np.arange(0.1, 1.0, 0.1):
    ror = get_ror(k)
    print("%.1f %f" % (k, ror))