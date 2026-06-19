# Day 58 — CSV & Large File Handling

**Phase 4 | Python + Excel Automation Roadmap**

## What I Built

A memory-efficient data processing pipeline that reads a 5,000-row NSE transaction CSV in chunks, aggregates BUY/SELL summaries per stock and sector, and demonstrates multiple pandas memory optimization techniques.

## File Structure

```
day58/
├── day58_csv_large_file_handling.py   # Main script
└── nse_transactions_large.csv         # Practice dataset (5,000 rows, 14 columns)
```

## Key Concepts Covered

| Technique | Purpose |
|---|---|
| `chunksize` in `pd.read_csv()` | Process large files without loading all rows into RAM |
| `usecols` | Load only required columns — 62% memory saving demonstrated |
| `dtype` specification | Manually set column types upfront — 68% memory saving demonstrated |
| `nrows` | Sample N rows during development/testing |
| `memory_usage(deep=True)` | Profile per-column RAM consumption |
| `pd.concat()` on chunk results | Combine aggregated outputs from each chunk |

## Output

- BUY/SELL net value summary per NSE stock
- Sector-wise total BUY investment (in Crores)
- Memory comparison: default load (2371 KB) vs optimised pipeline (754 KB)

## Tech Stack

- Python 3.x
- pandas

## Dataset

Synthetic NSE transaction log — 5,000 rows covering RELIANCE, TCS, INFY, HDFCBANK, WIPRO, ICICIBANK, BAJFINANCE, SBIN, TATAMOTORS, MARUTI across NSE from Jan 2023 to Jun 2024.

---

*Part of 84-Day Python & Excel Automation Roadmap | github.com/bhanupratap05683-netizen*
