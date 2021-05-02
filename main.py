import time
import pyupbit
import datetime
import copy
import requests
from account import Account
from agent import Agent
from strategy import Strategy
from slackbot import Slackbot

access = ""
secret = ""
myToken = ""

myChannel = "#crypto"
g_fee = 0.0005 # Fee 0.05% for each buy/sell

# Upbit Login
acc = Account(access=access, secret=secret, fee=g_fee)

# Coin lists
g_coin_list = ["BTC", "XRP", "DOGE", "ETC", "MED", "ETH", "BTT", "EOS"]

def post_message(text, token = myToken, channel = myChannel):
    # post slack message
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def post_message_time():
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day 
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    second = datetime.datetime.now().second
    post_message('[%d/%d/%d  %dh%dm%ds]'%(year, month, day, hour, minute, second))

def post_message_balance(coin_list):
    krw_bal = acc.get_balance("KRW")
    krw_bal_str = '%.0f'%krw_bal
    post_message("* KRW bal: " + krw_bal_str)
    for coin in coin_list:
        coin_bal = acc.get_balance(coin)
        if(coin_bal == None):
            continue
        coin_price = acc.get_current_price("KRW-"+coin)
        coin_bal_tot_str = '%.0f'%(coin_bal * coin_price)
        post_message("* " + coin + " bal:  " + str(coin_bal) + " = " + coin_bal_tot_str + " KRW")


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

if __name__ == "__main__" :
    coin_list = copy.deepcopy(g_coin_list)
    post_message_balance(coin_list)
    # coin_list.remove("XRP")

    n_agents = 2
    agent_list = []

    # Initializae agents
    krw_balance = acc.get_balance("KRW")
    for i in range(n_agents):
        agent_list.append(Agent(krw_balance/n_agents))
        
    # for agent in agent_list:
    #     agent.set_coin(coin_list[1])
    #     agent.print_coin()

    # Main Algorithm Start
    while False:
        try:
            now = datetime.datetime.now()
            start_time = get_start_time(g_coin_list[0]) # 9:00 AM same for every coin
            end_time = start_time + datetime.timedelta(days=1) # 9:00 AM + 1day

            if (now.minute==35 and check_running == True):
                slack.post_text("=== Check Status ===")
                post_message_default_info()
                check_running = False
        
            if(now.minute==36 and check_running == False):
                check_running = True

            if start_time < now < end_time - datetime.timedelta(seconds=50):
                if(day_start == True):
                    krw_day_start = get_balance("KRW")
                    post_message("=== Day start === ")
                    post_message_default_info()
                    day_start = False

                if k_range_strategy(g_krw_coin_name, g_k_range):
                    krw = get_balance("KRW")
                    if krw > 5000:
                        buy_result = upbit.buy_market_order(g_krw_coin_name, krw*(1-g_fee))
                        post_message("=== " + g_coin_name + " BUY !!! ===")
                        post_message_default_info()

            else:           
                btc = get_balance(g_coin_name)
                if btc * get_current_price(g_krw_coin_name) > 1000 :
                    sell_result = upbit.sell_market_order(g_krw_coin_name, btc*(1-g_fee))
                    post_message("=== " + g_coin_name + " SELL !!! ===")
                    post_message_default_info()
                
                if(day_start == False):
                    krw_day_end = get_balance("KRW")
                    post_message("=== Day end === ")
                    post_message_default_info()
                    post_message("KRW day start: " + str(krw_day_start)
                                + ", KRW day end: " + str(krw_day_end)
                                + ", ROR: " + str((krw_day_end - krw_day_start)/krw_day_start * 100.0) +"%")
                    day_start = True
            time.sleep(1)
        except Exception as e:
            print(e)
            post_message(e)
            time.sleep(1)