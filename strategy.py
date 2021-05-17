import pyupbit
import datetime
import time
import numpy as np
import copy
from account import Account
import matplotlib.pyplot as plt

class kRangeStrategy:
    def __init__(self, coin, fee):
        self.fee_ = fee
        self.coin_ = coin
        self.k_buy_ = 0.5
        self.k_sell_ = 0.2
    
    def optimize_k_values(self, opt_days, ref_date, is_plot=False):
        df = pyupbit.get_ohlcv("KRW-"+self.coin_, interval="day", count=opt_days+1, to=ref_date)

        # find ror (rate of revenue)
        k_buy_range = np.arange(0.1, 1.0, 0.1)
        k_sell_range = np.arange(self.fee_, 0.5, 0.01) 
        k_buy_mesh, k_sell_mesh = np.meshgrid(k_buy_range, k_sell_range)
        ror_mesh = np.zeros_like(k_buy_mesh)

        ror_max = 0.0
        mesh_col = 0
        for k_buy in k_buy_range:
            df['range'] = df['high'] - df['low']
            df['buy'] = df['open'] + (df['range']*k_buy).shift(1)
            mesh_row = 0
            for k_sell in k_sell_range:
                df['sell'] = df['buy'] *(1.0 + k_sell)    
                df['sell_actual'] = np.where(df['high'] >= df['sell'], df['sell'], df['close'])
                # df['sell_actual'] = df['close']
 
                df['ror'] = np.where(df['high'] >= df['buy'],
                                    (df['sell_actual'] - (df['buy'] + df['sell_actual'])*self.fee_) / df['buy'],
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
        print("%s, max ror : %.4f, k_buy : %.3f, k_sell : %.3f"%(self.coin_, ror_max, self.k_buy_, self.k_sell_))

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
        time.sleep(0.1)
        buy_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * self.k_buy_
        return buy_price

    def get_sell_price(self):
        # get sell price of kRangeStrategy
        sell_price = self.get_buy_price() * (1.0+self.k_sell_)
        return sell_price

    def check_buy(self):
        buy_price = self.get_buy_price()
        cur_price = pyupbit.get_orderbook(tickers="KRW-"+self.coin_)[0]["orderbook_units"][0]["ask_price"]
        if(buy_price <= cur_price and cur_price <= buy_price*1.01):
            return True
        else:
            return False

    def check_sell(self):
        sell_price = self.get_sell_price()
        cur_price = pyupbit.get_orderbook(tickers="KRW-"+self.coin_)[0]["orderbook_units"][0]["ask_price"]
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
    print(round(1.124124124,2))
    
    fee = 0.0005
    strategy = kRangeStrategy("XRP", fee)
    strategy.optimize_k_values(opt_days = 200, ref_date = datetime.datetime.now()-datetime.timedelta(days=0))