# Golden Dataset

Curated time-series + ground-truth anomaly annotations for benchmark.

## Structure

```
golden_dataset/
├── manifest.json              # Dataset metadata (version, distribution, kappa)
├── samples/
│   ├── series_001.csv         # Time series data (timestamp, value)
│   ├── series_001.label.json  # Annotations: [{interval, type, confidence}]
│   └── ...
├── audit/
│   ├── data-audit-YYYY-MM-DD.md     # Initial data audit report
│   ├── kappa-report.json            # Inter-annotator agreement
│   ├── coverage-check.md            # Distribution coverage
│   └── leakage-check.md             # Public-dataset overlap risk
└── README.md
```

## Versions

| Version | Samples | Status | Date |
|---|---|---|---|
| v0-audit | - | 🔴 not run | - |
| v1-pilot | 50 (target) | 🔴 not started | TBD |

## Sample File Format

`series_NNN.csv`:
```csv
timestamp,value
0,1.234
1,1.245
...
```

`series_NNN.label.json`:
```json
{
  "data_type": "noisy",
  "source": "ts-platform.data_pool#abc123",
  "annotators": ["alice", "bob"],
  "intervals": [
    {"interval": [120, 145], "type": "spike", "confidence": 0.95},
    {"interval": [3010, 3055], "type": "drift", "confidence": 0.7}
  ]
}
```

## See Also

- Annotation rules: `../../docs/annotation-spec.md`
- Methodology: `../../docs/benchmark-methodology.md`
- Source design: `ts-platform/docs/design-vl-self-refinement.md` §15
