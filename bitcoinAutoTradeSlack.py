import time
import pyupbit
import datetime
import requests

access = ""
secret = ""
myToken = ""

myChannel = "#crypto"
g_coin_name = "XRP"
g_krw_coin_name = "KRW-"+g_coin_name
g_k_range = 0.5
g_fee = 0.0005 # 수수료 

def post_message(text, token = myToken, channel = myChannel):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(coin):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == coin:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


def k_range_strategy(krw_coin, k):
    target_price = get_target_price(krw_coin, k)
    current_price = get_current_price(krw_coin)
    if(target_price < current_price):
        return True
    else:
        return False

def k_range_strategy_ma15(krw_coin, k):
    target_price = get_target_price(krw_coin, k)
    ma15 = get_ma15(krw_coin)
    current_price = get_current_price(krw_coin)
    if(target_price < current_price and ma15 < current_price):
        return True
    else:
        return False


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message("autotrade start")

day_start = True
krw_day_start = 0.0
krw_day_end = 0.0

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(g_krw_coin_name) # 9:00 AM
        end_time = start_time + datetime.timedelta(days=1) # 9:00 AM + 1day

        if (now.minute==30 and now.second < 2):
            post_message("=== Checking if algorithm is running!! ===")
            post_message("KRW balance: " + str(get_balance("KRW")))
            post_message(g_coin_name + " balance:  " + str(get_balance(g_coin_name)))
            time.sleep(2)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            if(day_start == True):
                krw_day_start = get_balance("KRW")
                post_message("=== Day start!! === ")
                post_message("KRW balance: " + str(get_balance("KRW")))
                post_message(g_coin_name + " balance:  " + str(get_balance(g_coin_name)))
                post_message("Current price: " + str(get_current_price(g_krw_coin_name))
                             + ", Target price: " + str(get_target_price(g_krw_coin_name, g_k_range)))
                day_start = False

            if k_range_strategy(g_krw_coin_name, g_k_range):
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order(g_krw_coin_name, krw*(1-g_fee))
                    post_message("=== " + g_coin_name + " buy!!! ===")
                    post_message("KRW balance: " + str(get_balance("KRW")))
                    post_message(g_coin_name + " balance:  " + str(get_balance(g_coin_name)))

        else:           
            btc = get_balance(g_coin_name)
            if btc > 0.00008:
                sell_result = upbit.sell_market_order(g_krw_coin_name, btc*(1-g_fee))
                post_message("=== " + g_coin_name + " sell!!! ===")
                post_message("KRW balance: " + str(get_balance("KRW")))
                post_message(g_coin_name + " balance:  " + str(get_balance(g_coin_name)))
            
            if(day_start == False):
                krw_day_end = get_balance("KRW")
                post_message("=== Day end!! === ")
                post_message("KRW balance: " + str(get_balance("KRW")))
                post_message(g_coin_name + " balance:  " + str(get_balance(g_coin_name)))
                post_message("KRW day start: " + str(krw_day_start)
                             + ", KRW day end: " + str(krw_day_end)
                             + ", ROR: " + str((krw_day_end - krw_day_start)/krw_day_start * 100.0) +"%")
                day_start = True
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(e)
        time.sleep(1)