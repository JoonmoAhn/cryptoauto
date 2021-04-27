import pyupbit
import numpy as np

# OHLCV (open, high, low, close, volume)로 당일 시가, 고가, 저가, 중가, 거래량에 대한 데이터
# cout = 7 : 7일 동안의 데이터
df = pyupbit.get_ohlcv("KRW-BTC", count=7)

# 변동폭 * k 계산, (고가 - 저가) * k값
df['range'] = (df['high'] - df['low']) * 0.5

# target(매수가), range 컬럼을 한칸씩 밑으로 내림 (.shift(1))
df['target'] = df['open'] + df['range'].shift(1)

fee = 0.0005 # 매수, 매도시 각각 0.05%
df['ror'] = np.where(df['high'] > df['target'],
                        (df['close'] - (df['target'] + df['close'])*fee) / df['target'],
                        1)

# 누적 곲 계산 (cumprod) => 누적수익률
df['hpr'] = df['ror'].cumprod()

# Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100


# MDD 계산 
print("MDD(%): ", df['dd'].max())

print(df)
# df.to_excel("dd.xlsx")