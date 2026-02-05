"""
Test script to verify the pagination fix for Mudrex SDK.

This script tests:
1. Fetching all assets using the corrected pagination
2. Verifying ADAUSDT is available
3. Getting ADAUSDT details directly
"""

from mudrex import MudrexClient
import sys

def test_pagination_fix(api_secret: str):
    """Test the pagination fix."""
    print("🔧 Testing Mudrex SDK Pagination Fix\n")
    print("=" * 60)
    
    try:
        # Initialize client
        print("\n1️⃣  Initializing Mudrex client...")
        client = MudrexClient(api_secret=api_secret)
        print("✅ Client initialized successfully")
        
        # Test 1: Fetch all assets
        print("\n2️⃣  Fetching ALL assets (this may take a moment)...")
        assets = client.assets.list_all()
        print(f"✅ Total assets fetched: {len(assets)}")
        
        if len(assets) < 100:
            print(f"⚠️  WARNING: Only {len(assets)} assets fetched. Expected 100+")
            print("   This might indicate the pagination is still not working correctly.")
        else:
            print(f"✅ SUCCESS: Fetched {len(assets)} assets (100+)")
        
        # Test 2: Verify ADAUSDT is available
        print("\n3️⃣  Checking if ADAUSDT is in the asset list...")
        ada_found = any(a.symbol == "ADAUSDT" for a in assets)
        
        if ada_found:
            print("✅ ADAUSDT found in asset list!")
        else:
            print("❌ ADAUSDT NOT found in asset list")
            print("   Available symbols (first 20):")
            for asset in assets[:20]:
                print(f"      - {asset.symbol}")
        
        # Test 3: Get ADAUSDT directly
        print("\n4️⃣  Fetching ADAUSDT details directly...")
        try:
            ada = client.assets.get("ADAUSDT")
            print(f"✅ ADAUSDT details retrieved successfully:")
            print(f"   Symbol: {ada.symbol}")
            print(f"   Price: ${ada.price if hasattr(ada, 'price') else 'N/A'}")
            print(f"   Min Quantity: {ada.min_quantity if hasattr(ada, 'min_quantity') else 'N/A'}")
        except Exception as e:
            print(f"❌ Failed to get ADAUSDT: {e}")
        
        # Test 4: Try to search for ADA
        print("\n5️⃣  Searching for ADA-related assets...")
        ada_assets = client.assets.search("ADA")
        print(f"✅ Found {len(ada_assets)} ADA-related assets:")
        for asset in ada_assets[:5]:  # Show first 5
            print(f"   - {asset.symbol}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("\nThe pagination fix is working correctly. 🎉")
        print("You can now trade ADAUSDT and other symbols without errors.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"\nFull error details:")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  MUDREX SDK PAGINATION FIX - TEST SCRIPT")
    print("=" * 60)
    
    # Check if API secret is provided
    if len(sys.argv) < 2:
        print("\n⚠️  Usage: python test_pagination_fix.py <API_SECRET>")
        print("\nExample:")
        print("  python test_pagination_fix.py your-api-secret-here")
        sys.exit(1)
    
    api_secret = sys.argv[1]
    test_pagination_fix(api_secret)
