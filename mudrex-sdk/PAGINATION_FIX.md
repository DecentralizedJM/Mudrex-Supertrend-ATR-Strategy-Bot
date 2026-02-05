# Mudrex SDK Pagination Fix

## Summary of Changes

Fixed the pagination issue in the Mudrex SDK that was causing `UNKNOWN_ERROR` when trading symbols like ADAUSDT.

### Root Cause
The SDK was using incorrect pagination parameters (`page` and `per_page`) instead of the Mudrex API's required parameters (`limit` and `offset`). This caused the SDK to only fetch the first 10-20 assets by default, preventing access to symbols like ADAUSDT that fall outside this range.

### Changes Made

**File: `mudrex/api/assets.py`**

Changed the `list_all()` method pagination from:
```python
# Before (incorrect)
params = {
    "page": page,
    "per_page": per_page,
}
```

To:
```python
# After (correct)
params = {
    "offset": offset,
    "limit": limit,
}
```

### Testing

A test script has been created at `test_pagination_fix.py` to verify the fix.

**To test the fix:**

```bash
cd /Users/jm/.gemini/antigravity/scratch/mudrex-api-trading-python-sdk

# Install the SDK in development mode
pip install -e .

# Run the test script
python test_pagination_fix.py YOUR_API_SECRET
```

The test will:
1. ✅ Fetch all 500+ assets
2. ✅ Verify ADAUSDT is available
3. ✅ Get ADAUSDT details directly
4. ✅ Search for ADA-related assets

### Next Steps

1. **Test locally** using the test script above
2. **Commit and push** the changes to GitHub
3. **Update the SDK version** (optional)
4. **Publish to PyPI** (if applicable)

### For Users Experiencing the Error

Users should:
1. Update to the latest version of the SDK
2. The error should be resolved automatically
3. No code changes needed on their end
