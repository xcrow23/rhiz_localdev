#!/usr/bin/env python3
"""
Quick balance test using stdlib only (no httpx needed).
"""

import sys
import os
import json
import urllib.request
import urllib.parse

# Add src to path
sys.path.insert(0, 'src')

# Load .env
env_path = '/mnt/c/Users/dread/Documents/Rhiz_LocalDev/.env'
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key] = value

from auth import CredentialManager

def test_balance():
    """Test Kraken account balance endpoint."""
    print("=" * 60)
    print("FATHOM BALANCE TEST")
    print("=" * 60)

    # Initialize auth
    print("\n→ Loading credentials...")
    auth = CredentialManager()
    print(f"✓ API Key: {auth.api_key[:20]}...")

    # Prepare request
    url = "https://api.kraken.com/0/private/Balance"
    data = {"nonce": auth.generate_nonce()}
    url_path = "/0/private/Balance"

    print(f"\n→ Generating signature...")
    headers = auth.get_headers(url_path, data)
    print(f"✓ Signature generated")

    # Make request
    print(f"\n→ Requesting balance from Kraken...")
    print(f"  URL: {url}")
    print(f"  Nonce: {data['nonce']}")

    post_data = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=post_data, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())

            print(f"✓ Response received")
            print("\n" + "=" * 60)
            print("RESULT")
            print("=" * 60)

            if result.get("error"):
                print(f"✗ API Error: {result['error']}")
                return False

            balances = result.get("result", {})

            if not balances:
                print("✓ Account authenticated successfully!")
                print("✓ Balance: $0.00 (awaiting verification)")
                print("\nNo assets yet - this is expected during verification.")
            else:
                print("✓ Account authenticated successfully!")
                print("\nBalances:")
                for asset, amount in balances.items():
                    print(f"  {asset}: {amount}")

            print("=" * 60)
            print("\n🎉 FATHOM PHASE 1 AUTH WORKING!")
            print("=" * 60)
            return True

    except urllib.error.HTTPError as e:
        print(f"✗ HTTP Error: {e.code} {e.reason}")
        print(f"  Response: {e.read().decode()}")
        return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_balance()
    sys.exit(0 if success else 1)
