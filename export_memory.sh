#!/bin/bash
curl -s -X POST 'http://localhost:6333/collections/rhiz_memories/points/scroll' \
  -H 'Content-Type: application/json' \
  -d @/mnt/c/Users/dread/Documents/Rhiz_LocalDev/scroll_request.json \
  > /mnt/c/Users/dread/Documents/Rhiz_LocalDev/memory_export.json
echo "Export complete"
