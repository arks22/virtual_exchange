class BalanceManager:
    def __init__(self, initial_cash_balance, initial_btc_balance):
        self.cash_balance = initial_cash_balance
        self.btc_balance = initial_btc_balance
        self.position = initial_btc_balance
    
    # 注文後に残高がマイナスにならないかチェック
    def evaluate_initial_balance(self, order_cash_change, order_btc_change, side):
        if side == 'long':
            order_cash_change *= -1
        elif side == 'short':
            order_btc_change *= -1
        post_order_cash_balance = self.cash_balance + order_cash_change
        post_order_btc_balance = self.btc_balance + order_btc_change
        return post_order_cash_balance >= 0 and post_order_btc_balance >= 0

    def update_cash_balance(self, cash_change):
        self.cash_balance += cash_change
    
    def update_btc_balance(self, btc_change):
        self.btc_balance += btc_change
    
    def update_position(self, position_change):
        self.position += position_change  # ネットポジションの更新
    
    def set_cash_balance(self, cash_balance):
        self.cash_balance = cash_balance
    
    def set_btc_balance(self, btc_balance):
        self.btc_balance = btc_balance
    
    def set_position(self, position):
        self.position = position

    def get_cash_balance(self):
        return self.cash_balance
    
    def get_btc_balance(self):
        return self.btc_balance 

    def get_position(self):
        return self.position 