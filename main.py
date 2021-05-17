import time
import pyupbit
import datetime
import copy
import requests
from agent import Agent
from strategy import kRangeStrategy
from account import Account

access = ""
secret = ""
myToken = ""
myChannel = "#crypto"
g_fee = 0.0005 # Fee 0.05% for each buy/sell

# Upbit Login
acc = Account(access=access, secret=secret, fee=g_fee)

# Coin lists
g_coin_list = ["XRP", "BTC", "ETC", "EOS", "DOGE"]

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

def post_message_info(coin_list, budget):
    post_message_time()
    budget_str = '%.0f'%budget
    post_message("* Cur budget: " + budget_str)
    krw_bal = acc.get_balance("KRW")
    krw_bal_str = '%.0f'%krw_bal
    post_message("* KRW bal: " + krw_bal_str)
    for coin in coin_list:
        strategy = kRangeStrategy(coin, g_fee)
        coin_bal = acc.get_balance(coin)
        coin_price = acc.get_current_price(coin)
        coin_bal_tot_str = '%.0f'%(coin_bal * coin_price)
        post_message("* " + coin + " bal:  " + str(coin_bal) + " = " + coin_bal_tot_str + " KRW")
        post_message("Cur price: " + str(coin_price) + ", Buy price: " + str(strategy.get_buy_price()) +", Sell price: " + str(strategy.get_sell_price()))


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

if __name__ == "__main__" :
    n_agents = 3 
    seed_budget = 300000

    budget_day_start = seed_budget
    budget_day_end = seed_budget 

    # Main Algorithm Start
    agent_list = []
    strategy_list = []
    day = 1
    ror_cum = 1.0
    day_start = True
    check_running = True

    while True:
        try:
            now = datetime.datetime.now()
            start_time = get_start_time("KRW-"+g_coin_list[0]) # 9:00 AM same for every coin
            end_time = start_time + datetime.timedelta(days=1) # 9:00 AM + 1day

            if (now.minute==35 and check_running == True):
                post_message("=== Check Status ===")
                post_message_info(g_coin_list, budget_day_end)
                check_running = False
        
            if(now.minute==36 and check_running == False):
                check_running = True

            if start_time < now < end_time - datetime.timedelta(seconds=50):
                if(day_start == True):
                    post_message("=== Day " + str(day) + " start === ")
                    post_message_info(g_coin_list, budget_day_end)

                    # Initializae agents
                    # krw_balance = acc.get_balance("KRW")
                    budget_day_start = budget_day_end 
                    agent_list.clear()
                    for i in range(n_agents):
                        agent_list.append(Agent(budget_day_start/n_agents))
                        
                    # Reset coin list
                    strategy_list.clear()
                    for coin in g_coin_list:
                        strategy = kRangeStrategy(coin, g_fee)
                        strategy_list.append(strategy)

                    day_start = False
                
                # Check Buy
                for agent in agent_list:
                    if agent.get_is_bought() == True:
                        continue                    
                    for strategy in strategy_list:
                        coin = strategy.get_coin()
                        if(strategy.check_buy() and agent.get_budget() > 5000):
                            krw_before = acc.get_balance("KRW")
                            agent.set_strategy(strategy)
                            strategy_list.remove(strategy)
                            buy_result = acc.buy(coin, agent.get_budget())
                            post_message("=== " + coin + " BUY !!! ===")
                            time.sleep(1)
                            agent.set_is_bought(True)
                            krw_after = acc.get_balance("KRW")
                            budget_day_end += (krw_after - krw_before)
                            post_message_info(g_coin_list, budget_day_end)
                            break
                            
                # Check Sell
                for agent in agent_list:
                    if (agent.get_is_bought() == False) or (agent.get_is_sold() == True):
                        continue
        
                    coin = agent.get_strategy().get_coin()
                    coin_balance = acc.get_balance(coin)
                    
                    if(agent.get_strategy().check_sell() and acc.get_current_price(coin)*coin_balance > 1000):
                        krw_before = acc.get_balance("KRW")
                        sell_result = acc.sell(coin, coin_balance)
                        post_message("=== " + coin + " SELL !!! ===")
                        time.sleep(1)
                        agent.set_is_sold(True)
                        krw_after = acc.get_balance("KRW")
                        budget_day_end += (krw_after - krw_before)
                        post_message_info(g_coin_list, budget_day_end)

            else: 
                # Sell all remaining
                for agent in agent_list:
                    if (agent.get_is_bought() == False) or (agent.get_is_sold() == True):
                        continue

                    coin = agent.get_strategy().get_coin()
                    coin_balance = acc.get_balance(coin)
                    if(acc.get_current_price(coin)*coin_balance > 1000):
                        krw_before = acc.get_balance("KRW")
                        sell_result = acc.sell(coin, coin_balance)
                        post_message("=== " + coin + " SELL !!! ===")
                        time.sleep(1)
                        agent.set_is_sold(True)
                        krw_after = acc.get_balance("KRW")
                        budget_day_end += (krw_after - krw_before)
                
                if(day_start == False):
                    ror = budget_day_end / budget_day_start
                    ror_cum *= ror
                    post_message("=== Day  " + str(day) + " end === ")
                    post_message_info(g_coin_list, budget_day_end)

                    budget_day_start_str = '%.0f'%budget_day_start
                    budget_day_end_str = '%.0f'%budget_day_end
                    post_message("Budget day start: " + budget_day_start_str
                                + ", Budget day end: " + budget_day_end_str
                                + ", ROR: " + str(round(ror,3)) 
                                + ", CROR: " + str(round(ror_cum,3)))
                    day_start = True
                    day += 1

            time.sleep(1)
        except Exception as e:
            print(e)
            post_message(e)
            time.sleep(1)