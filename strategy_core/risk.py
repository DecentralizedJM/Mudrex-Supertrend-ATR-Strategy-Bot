"""Risk and position sizing."""

from typing import Tuple


def position_size(
    balance: float,
    margin_pct: float,
    entry_price: float,
    leverage: int,
    min_qty: float,
    quantity_step: float,
) -> Tuple[float, int]:
    """
    Compute position size and leverage.
    Margin = balance * margin_pct. Quantity = (margin * leverage) / entry_price.
    Leverage clamped to leverage_min, leverage_max.
    Returns (quantity, leverage). Quantity rounded down to quantity_step, >= min_qty or 0.
    """
    if balance <= 0 or entry_price <= 0 or margin_pct <= 0:
        return 0.0, leverage

    margin = balance * margin_pct
    raw_qty = (margin * leverage) / entry_price

    if quantity_step > 0:
        steps = int(raw_qty / quantity_step)
        quantity = steps * quantity_step
    else:
        quantity = raw_qty

    if quantity < min_qty:
        return 0.0, leverage

    return quantity, leverage


def compute_leverage(base_leverage: int, leverage_min: int, leverage_max: int) -> int:
    """Clamp leverage to [leverage_min, leverage_max]."""
    return max(leverage_min, min(leverage_max, base_leverage))
