import pyupbit

class Account:
    def __init__(self, access, secret, fee):
        self.upbit_ = pyupbit.Upbit(access, secret)
        self.fee_ = fee

    def get_balance(self, coin):
        balances = self.upbit_.get_balances()
        balance_ret =0        
        for b in balances:
            if b['currency'] == coin:
                if b['balance'] is not None:
                    balance_ret = float(b['balance'])
                else:
                    balance_ret = 0
        return balance_ret

    def get_current_price(self, coin):
        ticker = "KRW-"+coin
        price =  pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]
        return price

    def buy(self, coin, krw_bal):
        result = self.upbit_.buy_market_order("KRW-"+coin, krw_bal*(1-self.fee_))
        return result 

    def sell(self, coin, coin_bal):
        result = self.upbit_.sell_market_order("KRW-"+coin, coin_bal*(1-self.fee_))
        return result

    def get_fee(self):
        return self.fee_
    
