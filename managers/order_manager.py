# オーダーの管理
class OrderManager:
    def __init__(self, maker_fee, taker_fee):
        self.order_index = 0
        self.open_orders    = {}
        self.canceled_orders = [] # 外部からのキャンセル
        self.closed_orders  = []  #  決済されたオーダー
        self.rejected_orders = [] # キャッシュ不足などで拒否されたオーダー
        self.fee_maker = maker_fee
        self.fee_taker = taker_fee

    # オーダーの作成
    def create_order(self, order, clock):
        self.order_index += 1
        order_id = str(self.order_index)
        self.open_orders[order_id] = {
            "order_id": order_id,
            "side": order["side"],
            "type": order["type"],
            "price": order["price"],
            "size": order["size"],
            "timestamp": clock,
        }
        return order_id

    # オーダーの削除
    def close_order(self, order_id, type="close"):
        if order_id in self.open_orders:
            close_order = self.open_orders[order_id]
            if type == "cancel":
                self.canceled_orders.append(close_order)
            elif type == "close":
                self.closed_orders.append(close_order)
            elif type == "reject":
                self.rejected_orders.append(close_order)

            del self.open_orders[order_id]
        
    # 成行注文の処理
    def execute_market_order(self, order_id, current_price):
        order = self.open_orders.get(order_id)
        position_change, cash_change = 0, 0
        if order:
            position_change += order['size'] * (1 if order['side'] == 'long' else -1)
            cash_change += order['size'] * current_price * (-1 if order['side'] == 'long' else 1)
            cash_change -= self.calculate_fee(order['size'], current_price, 'taker')
            self.close_order(order_id)  # オーダーの削除

        return position_change, cash_change

    # 指値注文の処理
    def execute_limit_order(self, order_id):
        order = self.open_orders.get(order_id)
        position_change, cash_change = 0, 0
        if order:
            position_change += order['size'] * (1 if order['side'] == 'long' else -1)
            cash_change += order['size'] * order['price'] * (-1 if order['side'] == 'long' else 1)
            cash_change -= self.calculate_fee(order['size'], order['price'], 'maker')
            self.close_order(order_id)  # オーダーの削除

        return position_change, cash_change
    
    #  ストップ注文の処理
    def execute_stop_order(self, order_id, current_price):
        order = self.open_orders.get(order_id)
        position_change, cash_change = 0, 0
        if order:
            position_change += order['size'] * (1 if order['side'] == 'long' else -1)
            cash_change += order['size'] * current_price * (-1 if order['side'] == 'long' else 1)
            cash_change -= self.calculate_fee(order['size'], order['price'], 'maker')
            self.close_order(order_id)  # オーダーの削除

        return position_change, cash_change

    # 手数料の計算
    def calculate_fee(self, size, price, fee_type):
        if fee_type == "maker":
            fee_rate = self.fee_maker
        elif fee_type == "taker":
            fee_rate = self.fee_taker

        return price * size * fee_rate

    def get_open_orders(self):
        return self.open_orders
        
    def get_closed_orders(self):
        return self.closed_orders

    def get_canceled_orders(self):
        return self.canceled_orders
    
    def get_rejected_orders(self):
        return self.rejected_orders
