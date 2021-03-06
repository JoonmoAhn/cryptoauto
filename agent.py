import time
import pyupbit
import datetime
import time
import requests
import copy
from strategy import kRangeStrategy
from account import Account

class Agent:
    def __init__(self, budget):
        self.budget_ = budget
        self.strategy_ = None
        self.is_bought_ = False
        self.is_sold_ = False

    def set_budget(self, budget):
        self.budget_ = budget

    def set_strategy(self, strategy):
        self.strategy_ = strategy

    def set_is_bought(self, is_bought):
        self.is_bought_ = is_bought

    def set_is_sold(self, is_sold):
        self.is_sold_ = is_sold

    def get_strategy(self):
        return self.strategy_

    def get_budget(self):
        return self.budget_

    def get_is_bought(self):
        return self.is_bought_

    def get_is_sold(self):
        return self.is_sold_



if __name__ == "__main__" :
    access = ""
    secret = "" 
    fee = 0.0005
    acc = Account(access, secret, fee)

    # Backtesting kRangeStrategy
    # g_coin_list = ["BTC", "XRP", "DOGE", "ETC", "EOS"]
    # g_coin_list = ["XRP", "BTC", "ETC", "EOS", "DOGE"]
    g_coin_list = ["XRP"]
    optimize_days = 10
    backtest_days = 30
    
    krw_bal_init = 10000.0
    n_agents = 1
    
    krw_bal = krw_bal_init
    for day_back in range(backtest_days, 0, -1):
        # Reset Agents
        agent_list = []
        for i in range(n_agents):
            agent_list.append(Agent(krw_bal/n_agents))
        
        # Reset coin list
        strategy_list = []
        for coin in g_coin_list:
            strategy = kRangeStrategy(acc, coin)
            # strategy.optimize_k_values(opt_days = optimize_days, ref_date = datetime.datetime.now()-datetime.timedelta(days=day_back))
            strategy_list.append(strategy)
        
        for agent in agent_list:
            # Continue if agent has some strategy
            if agent.get_strategy() != None:
                continue

            for strategy in strategy_list:
                coin = strategy.get_coin()

                k_buy = strategy.get_k_buy()
                k_sell = strategy.get_k_sell()
                
                df = pyupbit.get_ohlcv("KRW-"+coin, interval="day", count=2, to=datetime.datetime.now()-datetime.timedelta(days=day_back))
                time.sleep(0.2)
                buy_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low'])*k_buy
                if(df.iloc[1]['high'] >= buy_price):
                    agent.set_strategy(strategy)
                     # remove strategy
                    strategy_list.remove(strategy)

                    # sell
                    sell_price = df.iloc[1]['close']
                    if(df.iloc[1]['high'] >= buy_price*(1.0 + k_sell)):
                        sell_price = buy_price*(1.0 + k_sell)

                    ror = (sell_price -(sell_price + buy_price)*fee) / buy_price
                    budget = agent.get_budget()
                    agent.set_budget(budget * ror)
                    print("Coin: %s, Buy: %.1f, Sell: %.1f, High: %.1f, Close: %.1f"%(agent.get_strategy().get_coin(), buy_price, sell_price, df.iloc[1]['high'], df.iloc[1]['close']))
                    break    

        # Sum up and rebalance
        krw_bal = 0.0
        for agent in agent_list:
            krw_bal += agent.get_budget()
        
        print("Day back : %d, ROR : %.4f"%(day_back, krw_bal/krw_bal_init))

    print("ROR Tot : %.4f"%(krw_bal/krw_bal_init))
    
    
        
    

