---
name: safe-skill
description: A safe example skill with pure Python. No network, no shell, no env.
metadata: {}
---

# Safe Skill

This skill demonstrates a safe pattern: pure computation only.

## Usage

```python
def add(a: int, b: int) -> int:
    return a + b
```

No external calls.
