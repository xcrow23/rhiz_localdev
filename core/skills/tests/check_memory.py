#!/usr/bin/env python3
"""Quick script to check memory usage of router."""

import psutil
import os
from pathlib import Path
import sys

# Add project root to path
RHIZ_ROOT = Path(__file__).parent.parent.parent.parent
if str(RHIZ_ROOT) not in sys.path:
    sys.path.insert(0, str(RHIZ_ROOT))

p = psutil.Process(os.getpid())
print(f"Memory before import: {p.memory_info().rss / 1024 / 1024:.1f} MB")

from core.skills.router import SkillRouter
print(f"Memory after import: {p.memory_info().rss / 1024 / 1024:.1f} MB")

router = SkillRouter()
print(f"Memory after router init: {p.memory_info().rss / 1024 / 1024:.1f} MB")

for i in range(10):
    router.route_query("test query")

print(f"Memory after 10 queries: {p.memory_info().rss / 1024 / 1024:.1f} MB")

for i in range(100):
    router.route_query(f"test query {i}")

print(f"Memory after 110 queries: {p.memory_info().rss / 1024 / 1024:.1f} MB")
