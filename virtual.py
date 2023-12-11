from .managers.market_manager import MarketManager
from .managers.order_manager import OrderManager
from .managers.balance_manager import BalanceManager

# Todo
# - 両建て
# - レバレッジ
# - 現物、マージンの切り替え
class VirtualExchange:
    def __init__(self, market_data, clock, initial_cash_balance=0, initial_btc_balance=0, maker_fee=0, taker_fee=0):
        self.market_manager   = MarketManager(market_data, clock)
        self.order_manager    = OrderManager(maker_fee=maker_fee, taker_fee=taker_fee)
        self.balance_manager  = BalanceManager(initial_cash_balance, initial_btc_balance)
    
    def set_clock(self, clock):
        self.market_manager.set_clock(clock)
    
    def set_balances(self, cash_balance=None, btc_balance=None, position=None):
        if cash_balance != None:
            self.balance_manager.set_cash_balance(cash_balance)
        if btc_balance != None:
            self.balance_manager.set_btc_balance(btc_balance)
        if position != None:
            self.balance_manager.set_position(position)
        
    # オーダーを受け取る
    def receive_order(self, order):
        # オーダー作成
        order_id = self.order_manager.create_order(order, self.market_manager.clock)

        current_price = self.market_manager.get_price()
        # 初期証拠金レベルのチェック
        if not self.balance_manager.evaluate_initial_margin(order['size'], current_price, current_price):
            self.order_manager.close_order(order_id, type="reject")

        # 成行注文
        if order["type"] == "market":
            position_change, cash_change = self.order_manager.execute_market_order(order_id, current_price)
            self.update_position(position_change)
            self.update_balance(cash_change, position_change)
    
    # オーダーをキャンセル
    def cancel_order(self, order_id):
        self.order_manager.close_order(order_id, type="cancel")

    # 状態の更新処理
    def update_state(self):
        # 市場データの更新
        self.market_manager.update_market_data()
        # 現在の市場価格を取得
        current_price = self.market_manager.get_price()

        # 約定可能なオーダーを処理するループ
        for order_id, order in list(self.order_manager.get_open_orders().items()):
            self.process_executable_orders(order_id, order)

        # 維持証拠金レベルのチェック
        position = self.balance_manager.get_position()
        if not self.balance_manager.evaluate_maintenance_margin(position, current_price):
            #self.execute_liquidation() # ロスカット
            pass
    
    # 約定可能なオーダーの処理
    def process_executable_orders(self, order_id, order):
        current_price = self.market_manager.get_price()
        position_change, cash_change = 0, 0
        # 注文タイプに応じて約定処理
        # 指値注文
        if order["type"] == "limit" and ((order['side'] == 'long' and order['price'] >= current_price) or
                                        (order['side'] == 'short' and order['price'] <= current_price)):
            # 初期証拠金レベルのチェック
            if self.balance_manager.evaluate_initial_balance(order['size'] * order['price'], order['size'], order['side']):
                position_change, cash_change = self.order_manager.execute_limit_order(order_id)
            else:
                self.order_manager.close_order(order_id, type="reject") #  約定条件を達成しても、証拠金条件を満たさない場合削除
        # ストップ注文
        elif order["type"] == "stop" and ((order['side'] == 'long' and order['price'] <= current_price) or
                                          (order['side'] == 'short' and order['price'] >= current_price)):
            # 初期証拠金レベルのチェック
            if self.balance_manager.evaluate_initial_balance(order['size'] * order['price'], order['size'], order['side']):
                position_change, cash_change = self.order_manager.execute_stop_order(order_id, current_price)
            else:
                self.order_manager.close_order(order_id, type="reject")# 約定条件を達成しても、証拠金条件を満たさない場合削除

        if position_change != 0:
            # 約定した場合、ポジションとキャッシュを更新
            self.update_position(position_change)
            self.update_balance(cash_change, position_change)

    # キャッシュバランスの更新
    def update_balance(self, cash_change, btc_change):
        if cash_change != 0:
            self.balance_manager.update_cash_balance(cash_change)
        if btc_change != 0:
            self.balance_manager.update_btc_balance(btc_change)
    
    # ポジションの更新
    def update_position(self, position_change):
        self.balance_manager.update_position(position_change)
    
    # ロスカット
    def execute_liquidation(self):
        print('liquidation')
        # 現在の市場価格を取得
        position = self.balance_manager.get_position()

        # ネットポジションが0でない場合、清算を行う
        if position != 0:
            # 清算するポジションのサイズを設定（ロングは負の値、ショートは正の値）
            liquidation_size = -position
            # マーケットオーダーを作成して実行
            liquidation_order = {
                "type": "market",
                "size": abs(liquidation_size),
                "side": "long" if liquidation_size < 0 else "short",
                "price": None,
            }
            self.receive_order(liquidation_order)


    def get_market_data(self, donot_update=False):
        if not donot_update:
            self.update_state()

        return self.market_manager.get_ohlcv()

    def get_current_price(self):
        return self.market_manager.get_price()
    
    def get_future_data(self):
        return self.market_manager.get_future_ohlcv()
    
    def get_open_orders(self):
        return self.order_manager.get_open_orders()
    
    def get_closed_orders(self):
        return self.order_manager.get_closed_orders()

    def get_canceled_orders(self):
        return self.order_manager.get_canceled_orders()
    
    def get_rejected_orders(self):
        return self.order_manager.get_rejected_orders()

    def get_status(self):
        return {
            "clock" : self.market_manager.clock,
            "asset" : self.balance_manager.get_cash_balance() + self.balance_manager.get_btc_balance() * self.market_manager.get_price(),
            "position": self.balance_manager.get_position(),
            "cash_balance": self.balance_manager.get_cash_balance(),
            "btc_balance": self.balance_manager.get_btc_balance(),
            "open_orders_num": len(self.order_manager.get_open_orders()),
            "closed_orders_num": len(self.order_manager.get_closed_orders()),
            "canceled_orders_num": len(self.order_manager.get_canceled_orders()),
            "rejected_orders_num": len(self.order_manager.get_rejected_orders()),
        }
    