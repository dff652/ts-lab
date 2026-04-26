# Notebooks

**Exploratory analysis only. NOT production code.**

## Rules

1. Notebooks are throw-away. Anything valuable must be rewritten as a `techniques/` or `eval/` module before going into benchmarks.
2. Do **not** import notebook code from production modules.
3. Clear outputs before commit when possible (or use `nbstripout`).
4. Name notebooks with date prefix: `YYYY-MM-DD-<topic>.ipynb`

## Common Use Cases

- Inspect a specific failure case from baseline
- Try out a new prompt before turning it into a technique
- Visualize result distributions
- Manual annotation of edge-case samples

## Anti-pattern

```
# DO NOT do this in techniques/:
import sys
sys.path.append('../../notebooks')
from notebook_helper import some_function  # ❌
```

If `some_function` is useful, **rewrite it as a clean module** in `techniques/utils/` or `eval/`.
