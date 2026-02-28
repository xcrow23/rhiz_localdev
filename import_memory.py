#!/usr/bin/env python3
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import json
import uuid

# Connect to cloud Qdrant
client = QdrantClient(host="localhost", port=6333)

# Create collection with same config as local
client.recreate_collection(
    collection_name="rhiz_memories",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
print("Collection created")

# Load exported data
with open("/docker/rhiz/memory_export.json", "r") as f:
    data = json.load(f)

# Import points
points = []
for item in data:
    points.append(PointStruct(
        id=str(uuid.uuid4()),
        vector=item["vector"],
        payload=item["payload"]
    ))

client.upsert(collection_name="rhiz_memories", points=points)
print(f"Imported {len(points)} memory vectors to cloud Qdrant")

# Verify
info = client.get_collection("rhiz_memories")
print(f"Collection now has {info.points_count} points")
