#!/usr/bin/env python3
"""
Rhiz Checkpoint API - Validation Script
Run after deploying to verify all endpoints work.

Usage:
    python3 test_checkpoint_api.py https://rhiz-checkpoint-api.<subdomain>.workers.dev
"""

import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

def test_endpoint(base_url: str, method: str, path: str, data: dict = None) -> dict:
    """Test an API endpoint."""
    url = f"{base_url}{path}"
    
    try:
        if data:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method=method
            )
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            body = json.loads(response.read().decode('utf-8'))
            return {"success": True, "status": response.status, "body": body}
    
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8') if e.fp else ""
        return {"success": False, "status": e.code, "error": str(e), "body": body}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_checkpoint_api.py <base_url>")
        print("Example: python3 test_checkpoint_api.py https://rhiz-checkpoint-api.yoursubdomain.workers.dev")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    print(f"\n🔍 Testing Rhiz Checkpoint API at: {base_url}\n")
    print("=" * 60)
    
    tests = []
    
    # Test 1: Health check
    print("\n[1/5] Testing health endpoint...")
    result = test_endpoint(base_url, "GET", "/api/health")
    if result["success"]:
        print(f"  ✅ Health: {result['body'].get('status', 'unknown')}")
        print(f"     Database: {result['body'].get('database', 'unknown')}")
        print(f"     Checkpoints: {result['body'].get('checkpoints_count', 0)}")
        tests.append(("Health", True))
    else:
        print(f"  ❌ Health check failed: {result.get('error', result.get('body', 'unknown'))}")
        tests.append(("Health", False))
    
    # Test 2: Create checkpoint
    print("\n[2/5] Testing checkpoint creation...")
    test_checkpoint = {
        "session_id": f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "session_date": datetime.now().isoformat(),
        "session_topic": "API Validation Test",
        "layer_identity": "Test identity layer",
        "layer_relational": "Test relational layer",
        "layer_task": "Validating API deployment",
        "session_arc": "This is a test checkpoint created by the validation script."
    }
    result = test_endpoint(base_url, "POST", "/api/checkpoint", test_checkpoint)
    checkpoint_id = None
    if result["success"]:
        checkpoint_id = result['body'].get('checkpoint_id')
        print(f"  ✅ Created checkpoint: {checkpoint_id}")
        tests.append(("Create", True))
    else:
        print(f"  ❌ Create failed: {result.get('error', result.get('body', 'unknown'))}")
        tests.append(("Create", False))
    
    # Test 3: Get latest
    print("\n[3/5] Testing get latest...")
    result = test_endpoint(base_url, "GET", "/api/checkpoint/latest")
    if result["success"]:
        latest = result['body'].get('checkpoint', {})
        print(f"  ✅ Latest: {latest.get('session_id', 'unknown')}")
        print(f"     Topic: {latest.get('session_topic', 'unknown')}")
        tests.append(("Get Latest", True))
    else:
        print(f"  ❌ Get latest failed: {result.get('error', result.get('body', 'unknown'))}")
        tests.append(("Get Latest", False))
    
    # Test 4: Get layers
    print("\n[4/5] Testing graduated layers...")
    result = test_endpoint(base_url, "GET", "/api/checkpoint/layers?layers=identity,task")
    if result["success"]:
        layers = result['body'].get('layers', {})
        print(f"  ✅ Layers retrieved: {list(layers.keys())}")
        tests.append(("Get Layers", True))
    else:
        print(f"  ❌ Get layers failed: {result.get('error', result.get('body', 'unknown'))}")
        tests.append(("Get Layers", False))
    
    # Test 5: List checkpoints
    print("\n[5/5] Testing list checkpoints...")
    result = test_endpoint(base_url, "GET", "/api/checkpoints?limit=5")
    if result["success"]:
        count = result['body'].get('meta', {}).get('count', 0)
        print(f"  ✅ Listed {count} checkpoints")
        tests.append(("List", True))
    else:
        print(f"  ❌ List failed: {result.get('error', result.get('body', 'unknown'))}")
        tests.append(("List", False))
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    if passed == total:
        print(f"\n🎉 All {total} tests passed! API is fully operational.\n")
    else:
        print(f"\n⚠️  {passed}/{total} tests passed.\n")
        for name, success in tests:
            status = "✅" if success else "❌"
            print(f"  {status} {name}")
    
    print("\n📍 API Endpoints:")
    print(f"   Health:  GET  {base_url}/api/health")
    print(f"   Latest:  GET  {base_url}/api/checkpoint/latest")
    print(f"   Layers:  GET  {base_url}/api/checkpoint/layers?layers=identity,relational,task")
    print(f"   Create:  POST {base_url}/api/checkpoint")
    print(f"   List:    GET  {base_url}/api/checkpoints")
    print()


if __name__ == "__main__":
    main()
