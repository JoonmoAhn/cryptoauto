import pyupbit
import datetime
import time
import numpy as np
import copy
from account import Account
import matplotlib.pyplot as plt

class kRangeStrategy:
    def __init__(self, account, coin):
        self.acc_ = account
        self.coin_ = coin
        self.k_buy_ = 0.5
        self.k_sell_ = 1.8
    
    def optimize_k_values(self, opt_days, ref_date, is_plot=False):
        df = pyupbit.get_ohlcv("KRW-"+self.coin_, interval="day", count=opt_days+1, to=ref_date)
        fee = self.acc_.get_fee()

        # find ror (rate of revenue)
        k_buy_range = np.arange(0.1, 1.0, 0.1)
        k_sell_range = np.arange(0.1, 3.0, 0.1) 
        k_buy_mesh, k_sell_mesh = np.meshgrid(k_buy_range, k_sell_range)
        ror_mesh = np.zeros_like(k_buy_mesh)

        ror_max = 0.0
        mesh_col = 0
        for k_buy in k_buy_range:
            df['range'] = df['high'] - df['low']
            df['buy'] = df['open'] + (df['range']*k_buy).shift(1)
            mesh_row = 0
            for k_sell in k_sell_range:
                if(k_sell <= k_buy+0.1):
                    mesh_row += 1  
                    continue
                df['sell'] = df['open'] + (df['range']*k_sell).shift(1)    
                df['sell_actual'] = np.where(df['high'] >= df['sell'], df['sell'], df['close'])
                # df['sell_actual'] = df['close']
 
                df['ror'] = np.where(df['high'] >= df['buy'],
                                    (df['sell_actual'] - (df['buy'] + df['sell_actual'])*fee) / df['buy'],
                                    1)

                ror = df['ror'].cumprod()[-2] # cumulate until 1-day before
                if(ror > ror_max):
                    ror_max = ror
                    self.k_buy_ = k_buy
                    self.k_sell_ = k_sell
                # For plotting
                ror_mesh[mesh_row, mesh_col] = ror
                mesh_row += 1  
                # print("(%.1f, %.1f) : %f"%(k_buy, k_sell, ror))
            mesh_col += 1
            # print("%.1f : %f"%(k_buy, ror))
        print("%s, max ror : %.4f, k_buy : %.1f, k_sell : %.1f"%(self.coin_, ror_max, self.k_buy_, self.k_sell_))

        if(is_plot==True):
            plot = plt.axes(projection='3d')
            plot.set_xlabel('k_buy')
            plot.set_ylabel('k_sell')
            plot.set_zlabel('ror')
            plot.plot_surface(k_buy_mesh, k_sell_mesh, ror_mesh)
            
            plt.title('ror for %d days'%opt_days)
            plt.show()

    def get_buy_price(self):
        # get buy price of kRangeStrategy
        df = pyupbit.get_ohlcv("KRW-"+self.coin_, interval="day", count=2)
        buy_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * self.k_buy_
        return buy_price

    def get_sell_price(self):
        # get sell price of kRangeStrategy
        df = pyupbit.get_ohlcv("KRW-"+self.coin_, interval="day", count=2)
        sell_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * self.k_sell_
        return sell_price

    def check_buy(self):
        buy_price = self.get_buy_price()
        cur_price = self.acc_.get_current_price("KRW-"+self.coin_)
        if(buy_price <= cur_price):
            return True
        else:
            return False

    def check_sell(self):
        sell_price = self.get_sell_price()
        cur_price = self.acc_.get_current_price("KRW-"+self.coin_)
        if(sell_price <= cur_price):
            return True
        else:
            return False

    def get_k_buy(self):
        return self.k_buy_

    def get_k_sell(self):
        return self.k_sell_

    def get_coin(self):
        return self.coin_


if __name__ == "__main__" :  
    access = ""
    secret = "" 
    fee = 0.0005
    acc = Account(access, secret, fee)

    strategy = kRangeStrategy(acc, "XRP")
    strategy.optimize_k_values(opt_days = 200, ref_date = datetime.datetime.now()-datetime.timedelta(days=0))