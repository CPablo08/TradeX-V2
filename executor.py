"""
TradeX V3 - Executor Module
Executes trades via Binance API (or paper trading mode)
Handles order types (market / limit)
Confirms order execution and returns logs
"""

import logging
import uuid
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException
from config import Config

class Executor:
    def __init__(self):
        """Initialize Executor"""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Binance client
        if self.config.BINANCE_TESTNET:
            self.client = Client(
                self.config.BINANCE_API_KEY, 
                self.config.BINANCE_SECRET_KEY,
                testnet=True
            )
        else:
            self.client = Client(
                self.config.BINANCE_API_KEY, 
                self.config.BINANCE_SECRET_KEY
            )
        
        self.symbol = self.config.SYMBOL
        self.paper_trading = self.config.PAPER_TRADING
        
        # Paper trading state
        self.paper_balance = {
            'USDT': 10000.0,  # Starting balance
            'BTC': 0.0
        }
        self.paper_orders = {}
        
        self.logger.info(f"Executor initialized - Paper Trading: {self.paper_trading}")
    
    def get_account_balance(self):
        """Get current account balance"""
        try:
            if self.paper_trading:
                return self.paper_balance
            else:
                account = self.client.get_account()
                balances = {}
                for balance in account['balances']:
                    asset = balance['asset']
                    free = float(balance['free'])
                    if free > 0:
                        balances[asset] = free
                return balances
                
        except Exception as e:
            self.logger.error(f"Error getting account balance: {e}")
            return {}
    
    def get_current_price(self):
        """Get current price for the symbol"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=self.symbol)
            return float(ticker['price'])
        except Exception as e:
            self.logger.error(f"Error getting current price: {e}")
            return None
    
    def execute_buy_order(self, quantity, price=None):
        """Execute a buy order"""
        try:
            order_id = str(uuid.uuid4())
            current_price = self.get_current_price()
            
            if current_price is None:
                return None
            
            # Use current price if no specific price provided
            execution_price = price if price else current_price
            
            if self.paper_trading:
                # Paper trading execution
                required_usdt = quantity * execution_price
                
                if self.paper_balance['USDT'] >= required_usdt:
                    # Execute paper trade
                    self.paper_balance['USDT'] -= required_usdt
                    self.paper_balance['BTC'] += quantity
                    
                    order = {
                        'orderId': order_id,
                        'symbol': self.symbol,
                        'side': 'BUY',
                        'type': 'MARKET',
                        'quantity': quantity,
                        'price': execution_price,
                        'status': 'FILLED',
                        'executedQty': quantity,
                        'cummulativeQuoteQty': required_usdt,
                        'timeInForce': 'GTC',
                        'time': datetime.now().timestamp() * 1000,
                        'updateTime': datetime.now().timestamp() * 1000,
                        'isWorking': False
                    }
                    
                    self.paper_orders[order_id] = order
                    
                    self.logger.info(f"Paper BUY order executed: {quantity} BTC at {execution_price}")
                    return order
                else:
                    self.logger.error("Insufficient USDT balance for paper trading")
                    return None
            else:
                # Real trading execution
                try:
                    if price:
                        # Limit order
                        order = self.client.create_order(
                            symbol=self.symbol,
                            side=Client.SIDE_BUY,
                            type=Client.ORDER_TYPE_LIMIT,
                            timeInForce=Client.TIME_IN_FORCE_GTC,
                            quantity=quantity,
                            price=str(price)
                        )
                    else:
                        # Market order
                        order = self.client.create_order(
                            symbol=self.symbol,
                            side=Client.SIDE_BUY,
                            type=Client.ORDER_TYPE_MARKET,
                            quantity=quantity
                        )
                    
                    self.logger.info(f"Real BUY order executed: {order}")
                    return order
                    
                except BinanceAPIException as e:
                    self.logger.error(f"Binance API error: {e}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error executing buy order: {e}")
            return None
    
    def execute_sell_order(self, quantity, price=None):
        """Execute a sell order"""
        try:
            order_id = str(uuid.uuid4())
            current_price = self.get_current_price()
            
            if current_price is None:
                return None
            
            # Use current price if no specific price provided
            execution_price = price if price else current_price
            
            if self.paper_trading:
                # Paper trading execution
                if self.paper_balance['BTC'] >= quantity:
                    # Execute paper trade
                    usdt_received = quantity * execution_price
                    self.paper_balance['BTC'] -= quantity
                    self.paper_balance['USDT'] += usdt_received
                    
                    order = {
                        'orderId': order_id,
                        'symbol': self.symbol,
                        'side': 'SELL',
                        'type': 'MARKET',
                        'quantity': quantity,
                        'price': execution_price,
                        'status': 'FILLED',
                        'executedQty': quantity,
                        'cummulativeQuoteQty': usdt_received,
                        'timeInForce': 'GTC',
                        'time': datetime.now().timestamp() * 1000,
                        'updateTime': datetime.now().timestamp() * 1000,
                        'isWorking': False
                    }
                    
                    self.paper_orders[order_id] = order
                    
                    self.logger.info(f"Paper SELL order executed: {quantity} BTC at {execution_price}")
                    return order
                else:
                    self.logger.error("Insufficient BTC balance for paper trading")
                    return None
            else:
                # Real trading execution
                try:
                    if price:
                        # Limit order
                        order = self.client.create_order(
                            symbol=self.symbol,
                            side=Client.SIDE_SELL,
                            type=Client.ORDER_TYPE_LIMIT,
                            timeInForce=Client.TIME_IN_FORCE_GTC,
                            quantity=quantity,
                            price=str(price)
                        )
                    else:
                        # Market order
                        order = self.client.create_order(
                            symbol=self.symbol,
                            side=Client.SIDE_SELL,
                            type=Client.ORDER_TYPE_MARKET,
                            quantity=quantity
                        )
                    
                    self.logger.info(f"Real SELL order executed: {order}")
                    return order
                    
                except BinanceAPIException as e:
                    self.logger.error(f"Binance API error: {e}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error executing sell order: {e}")
            return None
    
    def execute_trade(self, decision, market_data):
        """Execute trade based on decision with advanced order types"""
        try:
            if not decision or decision['decision'] == 'HOLD':
                self.logger.info("No trade to execute - HOLD decision")
                return None
            
            side = decision['decision']
            confidence = decision['confidence']
            
            # Get current price
            current_price = market_data.get('current_price', 0)
            if current_price <= 0:
                current_price = self.get_current_price()
                if current_price is None:
                    return None
            
            # Get market regime for position sizing
            market_regime = decision.get('market_regime', 'UNKNOWN')
            
            # Calculate position size with performance metrics
            performance_metrics = self._get_performance_metrics()
            win_rate = performance_metrics.get('win_rate', 50)
            avg_win = performance_metrics.get('avg_win', 0.02)
            avg_loss = performance_metrics.get('avg_loss', -0.01)
            
            # Use risk module for position sizing
            position_size = self.risk_module.calculate_position_size(
                confidence, current_price, win_rate, avg_win, avg_loss
            )
            
            # Choose order type based on market conditions
            order_type = self._choose_order_type(market_data, decision)
            
            # Execute order based on side and type
            if side == 'BUY':
                order = self.execute_buy_order(position_size, current_price, order_type)
            elif side == 'SELL':
                order = self.execute_sell_order(position_size, current_price, order_type)
            else:
                self.logger.warning(f"Unknown trade side: {side}")
                return None
            
            if order:
                # Add decision info to order
                order['decision'] = decision
                order['execution_time'] = datetime.now()
                order['market_regime'] = market_regime
                order['order_type'] = order_type
                
                self.logger.info(f"Trade executed: {side} {position_size} BTC at {current_price} using {order_type} order")
                return order
            else:
                self.logger.error(f"Failed to execute {side} order")
                return None
                
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return None
    
    def _choose_order_type(self, market_data, decision):
        """Choose optimal order type based on market conditions"""
        try:
            # Get market volatility
            volatility = self._calculate_market_volatility(market_data)
            
            # Get spread information
            spread = self._get_market_spread(market_data)
            
            # Choose order type based on conditions
            if volatility > 0.03:  # High volatility
                # Use limit orders to avoid slippage
                return 'LIMIT'
            elif spread > 0.001:  # Wide spread
                # Use limit orders to get better prices
                return 'LIMIT'
            else:
                # Use market orders for tight spreads and low volatility
                return 'MARKET'
                
        except Exception as e:
            self.logger.error(f"Error choosing order type: {e}")
            return 'MARKET'  # Default to market order
    
    def _calculate_market_volatility(self, market_data):
        """Calculate current market volatility"""
        try:
            if 'dataframe' in market_data and not market_data['dataframe'].empty:
                df = market_data['dataframe']
                returns = df['close'].pct_change().dropna()
                return returns.std()
            return 0.02  # Default volatility
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility: {e}")
            return 0.02
    
    def _get_market_spread(self, market_data):
        """Get current market spread"""
        try:
            # This would typically get from order book
            # For now, return a default value
            return 0.0005  # 0.05% spread
            
        except Exception as e:
            self.logger.error(f"Error getting spread: {e}")
            return 0.0005
    
    def _get_performance_metrics(self):
        """Get recent performance metrics for Kelly Criterion"""
        try:
            # This would typically get from trade logger
            # For now, return default values
            return {
                'win_rate': 55,  # 55% win rate
                'avg_win': 0.025,  # 2.5% average win
                'avg_loss': -0.015  # -1.5% average loss
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {'win_rate': 50, 'avg_win': 0.02, 'avg_loss': -0.01}
    
    def cancel_order(self, order_id):
        """Cancel an existing order"""
        try:
            if self.paper_trading:
                if order_id in self.paper_orders:
                    order = self.paper_orders[order_id]
                    if order['status'] == 'NEW':
                        order['status'] = 'CANCELED'
                        self.logger.info(f"Paper order canceled: {order_id}")
                        return order
                    else:
                        self.logger.warning(f"Cannot cancel filled order: {order_id}")
                        return None
                else:
                    self.logger.warning(f"Order not found: {order_id}")
                    return None
            else:
                # Real order cancellation
                try:
                    result = self.client.cancel_order(
                        symbol=self.symbol,
                        orderId=order_id
                    )
                    self.logger.info(f"Real order canceled: {result}")
                    return result
                except BinanceAPIException as e:
                    self.logger.error(f"Error canceling real order: {e}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error canceling order: {e}")
            return None
    
    def get_order_status(self, order_id):
        """Get status of an order"""
        try:
            if self.paper_trading:
                return self.paper_orders.get(order_id)
            else:
                try:
                    order = self.client.get_order(
                        symbol=self.symbol,
                        orderId=order_id
                    )
                    return order
                except BinanceAPIException as e:
                    self.logger.error(f"Error getting order status: {e}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting order status: {e}")
            return None
    
    def get_open_orders(self):
        """Get all open orders"""
        try:
            if self.paper_trading:
                open_orders = [order for order in self.paper_orders.values() 
                             if order['status'] == 'NEW']
                return open_orders
            else:
                try:
                    orders = self.client.get_open_orders(symbol=self.symbol)
                    return orders
                except BinanceAPIException as e:
                    self.logger.error(f"Error getting open orders: {e}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error getting open orders: {e}")
            return []
    
    def get_trading_summary(self):
        """Get trading summary"""
        try:
            balance = self.get_account_balance()
            current_price = self.get_current_price()
            
            summary = {
                'balance': balance,
                'current_price': current_price,
                'paper_trading': self.paper_trading,
                'total_orders': len(self.paper_orders) if self.paper_trading else 'N/A'
            }
            
            if self.paper_trading and current_price:
                # Calculate paper trading PnL
                total_value = balance.get('USDT', 0) + (balance.get('BTC', 0) * current_price)
                initial_value = 10000.0  # Starting balance
                pnl = total_value - initial_value
                pnl_percentage = (pnl / initial_value) * 100
                
                summary['paper_pnl'] = pnl
                summary['paper_pnl_percentage'] = pnl_percentage
                summary['total_value'] = total_value
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting trading summary: {e}")
            return {}
