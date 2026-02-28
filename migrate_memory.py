#!/usr/bin/env python3
"""Migrate Qdrant vectors from local to cloud"""
import requests
import json

LOCAL_QDRANT = "http://localhost:6333"
CLOUD_QDRANT = "http://72.62.81.128:6333"
COLLECTION = "rhiz_memories"

def main():
    print("=== RHIZ MEMORY MIGRATION ===\n")
    
    # Step 1: Export from local
    print("1. Exporting from local Qdrant...")
    scroll_url = f"{LOCAL_QDRANT}/collections/{COLLECTION}/points/scroll"
    response = requests.post(scroll_url, json={
        "limit": 100,
        "with_payload": True,
        "with_vector": True
    })
    
    if response.status_code != 200:
        print(f"   ERROR: {response.text}")
        return
    
    data = response.json()
    points = data["result"]["points"]
    print(f"   Found {len(points)} vectors")
    
    # Step 2: Create collection on cloud
    print("\n2. Creating collection on cloud...")
    create_url = f"{CLOUD_QDRANT}/collections/{COLLECTION}"
    create_response = requests.put(create_url, json={
        "vectors": {
            "size": 384,
            "distance": "Cosine"
        }
    })
    
    if create_response.status_code == 200:
        print("   Collection created successfully")
    elif "already exists" in create_response.text:
        print("   Collection already exists")
    else:
        print(f"   Response: {create_response.text}")
    
    # Step 3: Upload points to cloud
    print("\n3. Uploading vectors to cloud...")
    upsert_url = f"{CLOUD_QDRANT}/collections/{COLLECTION}/points"
    
    # Format points for upsert
    upsert_points = []
    for p in points:
        upsert_points.append({
            "id": p["id"],
            "vector": p["vector"],
            "payload": p.get("payload", {})
        })
    
    upsert_response = requests.put(upsert_url, json={
        "points": upsert_points
    })
    
    if upsert_response.status_code == 200:
        print(f"   Successfully uploaded {len(points)} vectors!")
    else:
        print(f"   ERROR: {upsert_response.text}")
    
    # Step 4: Verify
    print("\n4. Verifying cloud collection...")
    verify_url = f"{CLOUD_QDRANT}/collections/{COLLECTION}"
    verify_response = requests.get(verify_url)
    verify_data = verify_response.json()
    cloud_count = verify_data["result"]["points_count"]
    print(f"   Cloud collection has {cloud_count} vectors")
    
    print("\n=== MIGRATION COMPLETE ===")

if __name__ == "__main__":
    main()
