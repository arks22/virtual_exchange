class BalanceManager:
    def __init__(self, initial_cash_balance, initial_btc_balance):
        self.initial_margin_rate = 0.1
        self.maintenance_margin_rate = 0.05
        self.cash_balance = initial_cash_balance
        self.btc_balance = initial_btc_balance
        self.position = initial_btc_balance

    def evaluate_initial_margin(self, order_size, order_price, current_price):
        # 要求される初期証拠金
        required_margin = order_size * order_price * self.initial_margin_rate
        return self._is_sufficient(required_margin, current_price)
    
    def evaluate_maintenance_margin(self, net_position_size, current_price):
        # 要求される維持証拠金
        required_margin = abs(net_position_size) * current_price * self.maintenance_margin_rate 
        return self._is_sufficient(required_margin, current_price)

    def _is_sufficient(self, required_margin, btc_price):
        # BTCバランスを現金価値に変換
        btc_value = self.btc_balance * btc_price
        # 利用可能な証拠金の合計
        total_margin_available = self.cash_balance + btc_value
        return total_margin_available >= required_margin and self.cash_balance >= 0 and self.btc_balance >= 0
    
    # 注文後に残高がマイナスにならないかチェック
    def evaluate_initial_balance(self, order_cash_change, order_btc_change, side):
        if side == 'long':
            order_cash_change *= -1
        elif side == 'short':
            order_btc_change *= -1
        post_order_cash_balance = self.cash_balance + order_cash_change
        post_order_btc_balance = self.btc_balance + order_btc_change
        return post_order_cash_balance >= 0 and post_order_btc_balance >= 0
        

    def update_balance(self, cash_change, btc_change):
        self.cash_balance += cash_change
        self.btc_balance += btc_change
        if self.cash_balance < 0 or self.btc_balance < 0:
            raise Exception(f'Negative balance{self.cash_balance}, {self.btc_balance}')
    
    def update_position(self, position_change):
        self.position += position_change  # ネットポジションの更新

    def get_cash_balance(self):
        return self.cash_balance
    
    def get_btc_balance(self):
        return self.btc_balance 

    def get_position(self):
        return self.position 