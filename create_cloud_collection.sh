#!/bin/bash
# Create collection
echo "Creating collection..."
curl -s -X PUT 'http://localhost:6333/collections/rhiz_memories' \
  -H 'Content-Type: application/json' \
  -d '{"vectors":{"size":384,"distance":"Cosine"}}'

echo ""
echo "Collection created. Checking status..."
curl -s 'http://localhost:6333/collections/rhiz_memories'
