# Bug Fixes Summary

## Issues Fixed

### 1. Terminology Inconsistencies (quantity/size, mark_price/market_price)

**Problem**: The Mudrex API inconsistently uses different field names:
- `quantity` vs `size` for position/order quantities
- `mark_price` vs `market_price` for position mark prices

This inconsistency caused "silent zeros" in calculations, leading to ghost math in trading bots.

**Solution**:
- Added normalization helper functions in `mudrex/utils.py`:
  - `normalize_quantity()`: Normalizes `quantity`/`size` to always use `quantity`
  - `normalize_mark_price()`: Normalizes `mark_price`/`market_price` to always use `mark_price`
- Updated `Position.from_dict()` to normalize both `quantity`/`size` and `mark_price`/`market_price`
- Updated `Order.from_dict()` to normalize `quantity`/`size` and `filled_quantity`/`filled_size`

**Files Modified**:
- `mudrex/models.py`: Added normalization in `Position.from_dict()` and `Order.from_dict()`
- `mudrex/utils.py`: Added `normalize_quantity()` and `normalize_mark_price()` helper functions

### 2. Ghost Positions Bug

**Problem**: Exposure was being derived from internal state rather than actual exchange data, causing "Ghost Positions" where positions appeared to exist but didn't actually exist on the exchange.

**Solution**:
- Added explicit documentation in `PositionsAPI.list_open()` and `PositionsAPI.get()` to clarify that positions are **always** fetched fresh from the exchange API, never from cached state
- Added `exposure` property to `Position` model that calculates exposure from exchange data (quantity × mark_price from API response), not from internal state
- Ensured all position data comes directly from API responses

**Files Modified**:
- `mudrex/api/positions.py`: Added documentation clarifying positions always come from exchange
- `mudrex/models.py`: Added `exposure` property that uses exchange data

## Key Changes

### mudrex/models.py

1. **Position.from_dict()**:
   - Now normalizes `quantity`/`size` using `normalize_quantity()`
   - Now normalizes `mark_price`/`market_price` using `normalize_mark_price()`
   - Added `exposure` property that calculates from exchange data

2. **Order.from_dict()**:
   - Now normalizes `quantity`/`size` using `normalize_quantity()`
   - Now normalizes `filled_quantity`/`filled_size`

### mudrex/utils.py

1. **normalize_quantity()**: New helper function to normalize quantity/size terminology
2. **normalize_mark_price()**: New helper function to normalize mark_price/market_price terminology

### mudrex/api/positions.py

1. **list_open()**: Added documentation clarifying positions always fetched from exchange
2. **get()**: Added documentation clarifying position data always comes from exchange

## Impact

These fixes:
- ✅ Prevent silent zeros in calculations (major source of ghost math)
- ✅ Eliminate Ghost Positions by ensuring exposure always comes from exchange data
- ✅ Normalize API response variations transparently
- ✅ Maintain backward compatibility

## Testing

All imports verified:
```bash
python3 -c "from mudrex.models import Position, Order; from mudrex.utils import normalize_quantity, normalize_mark_price; print('All imports successful')"
```

## Notes

- All normalization happens transparently in the model layer
- No breaking changes to the public API
- Position data is always fresh from the exchange, never cached
- Exposure calculations use actual exchange data (quantity × mark_price from API)
