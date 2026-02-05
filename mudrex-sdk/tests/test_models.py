"""
Tests for Mudrex SDK Models
===========================
"""

import pytest
from datetime import datetime
from mudrex.models import (
    WalletBalance,
    FuturesBalance,
    Asset,
    Leverage,
    Order,
    Position,
    OrderType,
    TriggerType,
    MarginType,
    OrderStatus,
    Ticker,
)


class TestWalletBalance:
    def test_from_dict(self):
        data = {
            "total": "1000.50",
            "withdrawable": "750.00",
            "invested": "200.00",
            "rewards": "10.00",
            "currency": "USDT"
        }
        balance = WalletBalance.from_dict(data)
        
        assert balance.total == "1000.50"
        assert balance.withdrawable == "750.00"
        assert balance.available == "750.00"  # Alias for withdrawable
        assert balance.invested == "200.00"
        assert balance.rewards == "10.00"
        assert balance.currency == "USDT"
    
    def test_from_dict_with_available_field(self):
        """Test backward compatibility when API returns 'available' instead of 'withdrawable'."""
        data = {
            "total": "1000.50",
            "available": "800.25",
            "currency": "USDT"
        }
        balance = WalletBalance.from_dict(data)
        
        assert balance.total == "1000.50"
        assert balance.withdrawable == "800.25"
        assert balance.available == "800.25"
        assert balance.currency == "USDT"
    
    def test_from_dict_defaults(self):
        data = {}
        balance = WalletBalance.from_dict(data)
        
        assert balance.total == "0"
        assert balance.withdrawable == "0"
        assert balance.available == "0"
        assert balance.currency == "USDT"


class TestFuturesBalance:
    def test_from_dict(self):
        data = {
            "balance": "500.00",
            "locked_amount": "100.00",
            "unrealized_pnl": "25.50",
            "first_time_user": False
        }
        balance = FuturesBalance.from_dict(data)
        
        assert balance.balance == "500.00"
        assert balance.locked_amount == "100.00"
        assert balance.unrealized_pnl == "25.50"
        assert balance.available == "400.0"
        assert balance.available_transfer == "400.0"
        assert balance.first_time_user == False
    
    def test_from_dict_defaults(self):
        data = {}
        balance = FuturesBalance.from_dict(data)
        
        assert balance.balance == "0"
        assert balance.locked_amount == "0"
        assert balance.available == "0"


class TestAsset:
    def test_from_dict(self):
        data = {
            "asset_id": "BTCUSDT",
            "symbol": "BTCUSDT",
            "base_currency": "BTC",
            "quote_currency": "USDT",
            "min_quantity": "0.001",
            "max_quantity": "100",
            "quantity_step": "0.001",
            "min_leverage": "1",
            "max_leverage": "100",
            "maker_fee": "0.02",
            "taker_fee": "0.04",
            "is_active": True
        }
        asset = Asset.from_dict(data)
        
        assert asset.asset_id == "BTCUSDT"
        assert asset.symbol == "BTCUSDT"
        assert asset.base_currency == "BTC"
        assert asset.max_leverage == "100"
    
    def test_from_dict_with_price_step(self):
        """Test that Asset correctly parses price_step from API response."""
        data = {
            "id": "01903a7b-bf65-707d-a7dc-d7b84c3c756c",
            "name": "Bitcoin",
            "symbol": "BTCUSDT",
            "min_contract": "0.001",
            "max_contract": "1190",
            "quantity_step": "0.001",
            "min_price": "0.1",
            "max_price": "1999999.8",
            "price_step": "0.1",
            "min_leverage": "1",
            "max_leverage": "100",
            "trading_fee_perc": "0.1",
            "price": "114550"
        }
        asset = Asset.from_dict(data)
        
        assert asset.price_step == "0.1"
        assert asset.min_price == "0.1"
        assert asset.max_price == "1999999.8"
        assert asset.price == "114550"
        assert asset.name == "Bitcoin"
        assert asset.min_quantity == "0.001"
        assert asset.max_quantity == "1190"


class TestTicker:
    def test_from_dict(self):
        data = {
            "symbol": "BTCUSDT",
            "price": "100000.50",
            "bid": "100000.00",
            "ask": "100001.00",
            "volume_24h": "1500000",
            "change_24h": "2.5"
        }
        ticker = Ticker.from_dict(data)
        
        assert ticker.symbol == "BTCUSDT"
        assert ticker.price == "100000.50"
        assert ticker.bid == "100000.00"
        assert ticker.ask == "100001.00"


class TestOrder:
    def test_from_dict(self):
        data = {
            "order_id": "ord_12345",
            "asset_id": "BTCUSDT",
            "symbol": "BTCUSDT",
            "order_type": "LONG",
            "trigger_type": "MARKET",
            "status": "FILLED",
            "quantity": "0.001",
            "filled_quantity": "0.001",
            "price": "100000",
            "leverage": "10",
        }
        order = Order.from_dict(data)
        
        assert order.order_id == "ord_12345"
        assert order.order_type == OrderType.LONG
        assert order.trigger_type == TriggerType.MARKET
        assert order.status == OrderStatus.FILLED
        assert order.leverage == "10"
        assert order.is_filled == True
        assert order.fill_percentage == 100.0
    
    def test_from_dict_with_size(self):
        """Test that Order correctly normalizes 'size' to 'quantity'."""
        data = {
            "order_id": "ord_12345",
            "asset_id": "BTCUSDT",
            "order_type": "SHORT",
            "trigger_type": "LIMIT",
            "status": "OPEN",
            "size": "0.5",
            "filled_size": "0.1",
            "price": "50000",
            "leverage": "5",
        }
        order = Order.from_dict(data)
        
        assert order.quantity == "0.5"
        assert order.filled_quantity == "0.1"
        assert order.is_open == True


class TestPosition:
    def test_from_dict(self):
        data = {
            "position_id": "pos_12345",
            "asset_id": "BTCUSDT",
            "symbol": "BTCUSDT",
            "side": "LONG",
            "quantity": "0.001",
            "entry_price": "100000",
            "mark_price": "101000",
            "leverage": "10",
            "margin": "10",
            "unrealized_pnl": "1.00",
            "realized_pnl": "0",
        }
        position = Position.from_dict(data)
        
        assert position.position_id == "pos_12345"
        assert position.side == OrderType.LONG
        assert position.entry_price == "100000"
        assert position.unrealized_pnl == "1.00"
        assert position.is_long == True
        assert position.is_short == False
        assert position.is_profitable == True
    
    def test_pnl_percentage(self):
        position = Position(
            position_id="pos_123",
            asset_id="BTCUSDT",
            symbol="BTCUSDT",
            side=OrderType.LONG,
            quantity="0.001",
            entry_price="100000",
            mark_price="101000",
            leverage="10",
            margin="10",
            unrealized_pnl="1.00",
            realized_pnl="0",
        )
        
        assert position.pnl_percentage == 10.0
    
    def test_exposure(self):
        """Test that exposure is calculated from quantity * mark_price."""
        position = Position(
            position_id="pos_123",
            asset_id="BTCUSDT",
            symbol="BTCUSDT",
            side=OrderType.LONG,
            quantity="0.1",
            entry_price="100000",
            mark_price="105000",
            leverage="10",
            margin="1050",
            unrealized_pnl="500",
            realized_pnl="0",
        )
        
        assert float(position.exposure) == 10500.0
    
    def test_from_dict_with_nested_stoploss(self):
        """Test that Position correctly parses nested stoploss/takeprofit."""
        data = {
            "id": "pos_12345",
            "symbol": "ETHUSDT",
            "order_type": "LONG",
            "quantity": "0.02",
            "entry_price": "4133.41",
            "mark_price": "4150.00",
            "leverage": "50",
            "margin": "10",
            "unrealized_pnl": "0.33",
            "realized_pnl": "0",
            "liquidation_price": "4071.1",
            "stoploss": {"price": "4100", "order_id": "sl_123", "order_type": "SHORT"},
            "takeprofit": {"price": "5000", "order_id": "tp_123", "order_type": "SHORT"},
            "status": "OPEN"
        }
        position = Position.from_dict(data)
        
        assert position.stoploss_price == "4100"
        assert position.takeprofit_price == "5000"
    
    def test_from_dict_with_flat_stoploss(self):
        """Test backwards compatibility with flat stoploss_price field."""
        data = {
            "id": "pos_12345",
            "symbol": "BTCUSDT",
            "order_type": "SHORT",
            "quantity": "0.001",
            "entry_price": "100000",
            "mark_price": "99000",
            "leverage": "10",
            "margin": "100",
            "unrealized_pnl": "10",
            "realized_pnl": "0",
            "stoploss_price": "101000",
            "takeprofit_price": "95000",
            "status": "OPEN"
        }
        position = Position.from_dict(data)
        
        assert position.stoploss_price == "101000"
        assert position.takeprofit_price == "95000"


class TestEnums:
    def test_order_type(self):
        assert OrderType.LONG.value == "LONG"
        assert OrderType.SHORT.value == "SHORT"
    
    def test_trigger_type(self):
        assert TriggerType.MARKET.value == "MARKET"
        assert TriggerType.LIMIT.value == "LIMIT"
    
    def test_margin_type(self):
        assert MarginType.ISOLATED.value == "ISOLATED"
    
    def test_order_status(self):
        assert OrderStatus.OPEN.value == "OPEN"
        assert OrderStatus.FILLED.value == "FILLED"
        assert OrderStatus.CANCELLED.value == "CANCELLED"
