# ============================================================
# DAY 58: CSV & Large File Handling
# Topic: Read large CSVs in chunks, process efficiently
# Dataset: NSE Stock Transactions Log (5,000 rows)
# ============================================================

import pandas as pd
import os
import time

CSV_FILE = "nse_transactions_large.csv"

# ============================================================
# SECTION 1: WHY CHUNKING? — Memory comparison
# ============================================================
# When you load a CSV normally, ALL rows load into RAM at once.
# For 1M+ row files, this can crash your script.
# Solution: read in "chunks" — N rows at a time — process, discard, repeat.

print("=" * 60)
print("SECTION 1: Normal Load vs Chunk Load — Memory Comparison")
print("=" * 60)

# Normal load (fine for small files)
start = time.time()
df_full = pd.read_csv(CSV_FILE)
normal_time = round(time.time() - start, 4)
normal_memory = round(df_full.memory_usage(deep=True).sum() / 1024, 1)

print(f"Normal Load  → {len(df_full)} rows | {normal_memory} KB | {normal_time}s")
del df_full  # Free RAM after comparison


# ============================================================
# SECTION 2: pd.read_csv() with chunksize
# ============================================================
# chunksize=N returns a TextFileReader iterator.
# Each iteration gives you a DataFrame of N rows.
# You process each chunk and throw it away — RAM stays low.

print("\n" + "=" * 60)
print("SECTION 2: Reading in Chunks (chunksize=1000)")
print("=" * 60)

chunk_iterator = pd.read_csv(CSV_FILE, chunksize=1000)
# chunk_iterator is NOT a DataFrame — it's a lazy iterator.
# Nothing is loaded yet. Data loads only when you loop.

print(f"Type of chunk_iterator: {type(chunk_iterator)}")
print("Iterating through chunks...\n")

chunk_count = 0
total_rows = 0

for chunk in chunk_iterator:
    chunk_count += 1
    total_rows += len(chunk)
    chunk_memory = round(chunk.memory_usage(deep=True).sum() / 1024, 1)
    print(f"  Chunk {chunk_count}: rows {chunk.index[0]+1}-{chunk.index[-1]+1} "
          f"| shape {chunk.shape} | {chunk_memory} KB in RAM")

print(f"\nTotal chunks: {chunk_count} | Total rows processed: {total_rows}")


# ============================================================
# SECTION 3: Processing each chunk — Stock Summary
# ============================================================
# Real use case: You have 1M transaction rows.
# Goal: Calculate total BUY and SELL value per stock.
# Process each chunk, store aggregated results, combine at end.

print("\n" + "=" * 60)
print("SECTION 3: Chunk Processing — BUY/SELL Summary per Stock")
print("=" * 60)

results_list = []  # Collect aggregated results from each chunk

for chunk in pd.read_csv(CSV_FILE, chunksize=1000):

    # Step 1: Drop rows with missing Price_Per_Share in this chunk
    chunk = chunk.dropna(subset=["Price_Per_Share"])

    # Step 2: Aggregate: sum Net_Value grouped by Stock + Transaction_Type
    chunk_summary = (
        chunk.groupby(["Stock_Symbol", "Transaction_Type"])["Net_Value"]
        .agg(["sum", "count"])
        .reset_index()
    )
    chunk_summary.columns = ["Stock", "Type", "Total_Value", "Txn_Count"]

    results_list.append(chunk_summary)  # Store result, discard chunk

# Step 3: Combine all chunk results with pd.concat()
combined = pd.concat(results_list, ignore_index=True)

# Step 4: Final aggregation across chunks (same stocks appeared in multiple chunks)
final_summary = (
    combined.groupby(["Stock", "Type"])
    .agg(Total_Value=("Total_Value", "sum"), Txn_Count=("Txn_Count", "sum"))
    .reset_index()
)

print(final_summary.to_string(index=False))


# ============================================================
# SECTION 4: usecols — Load Only Needed Columns
# ============================================================
# If your CSV has 50 columns and you need only 5,
# usecols skips the rest entirely — never loaded into RAM.

print("\n" + "=" * 60)
print("SECTION 4: usecols — Load Only Required Columns")
print("=" * 60)

needed_columns = ["Date", "Stock_Symbol", "Transaction_Type", "Quantity", "Net_Value"]

df_slim = pd.read_csv(CSV_FILE, usecols=needed_columns)

full_mem   = pd.read_csv(CSV_FILE).memory_usage(deep=True).sum()
slim_mem   = df_slim.memory_usage(deep=True).sum()
saving_pct = round((1 - slim_mem / full_mem) * 100, 1)

print(f"Full CSV   → {round(full_mem/1024,1)} KB (all 14 columns)")
print(f"usecols    → {round(slim_mem/1024,1)} KB (5 columns)")
print(f"Memory saved: {saving_pct}%")
print(f"\nSlim DataFrame shape: {df_slim.shape}")
print(df_slim.head(3).to_string(index=False))


# ============================================================
# SECTION 5: dtype — Specify Data Types Upfront
# ============================================================
# pandas auto-detects dtypes by scanning the entire file first.
# For large files, this scanning itself wastes time and memory.
# Telling pandas the dtypes explicitly: faster load + less RAM.

print("\n" + "=" * 60)
print("SECTION 5: dtype — Manual Type Specification")
print("=" * 60)

dtype_map = {
    "Transaction_ID":   "string",
    "Stock_Symbol":     "category",   # category uses far less RAM than object for repetitive strings
    "Sector":           "category",
    "Transaction_Type": "category",
    "Quantity":         "int32",      # default is int64; int32 saves 50% for smaller numbers
    "Price_Per_Share":  "float32",    # float32 vs float64 saves 50%
    "Gross_Value":      "float32",
    "Net_Value":        "float32",
    "Broker":           "category",
    "Exchange":         "category",
    "Currency":         "category",
}

df_typed = pd.read_csv(CSV_FILE, dtype=dtype_map)

default_mem = pd.read_csv(CSV_FILE).memory_usage(deep=True).sum()
typed_mem   = df_typed.memory_usage(deep=True).sum()
saving_pct2 = round((1 - typed_mem / default_mem) * 100, 1)

print(f"Default dtypes → {round(default_mem/1024,1)} KB")
print(f"Custom dtypes  → {round(typed_mem/1024,1)} KB")
print(f"Memory saved: {saving_pct2}%")
print("\nData types after dtype specification:")
print(df_typed.dtypes)


# ============================================================
# SECTION 6: nrows — Sample First N Rows for Testing
# ============================================================
# When your script is under development, don't load all 1M rows.
# Use nrows to load just a sample to test your logic fast.
# Once logic is confirmed correct, remove nrows for full run.

print("\n" + "=" * 60)
print("SECTION 6: nrows — Quick Sampling for Script Testing")
print("=" * 60)

df_sample = pd.read_csv(CSV_FILE, nrows=50)
print(f"Sample shape: {df_sample.shape}  ← test your code on 50 rows first")
print(df_sample[["Transaction_ID", "Stock_Symbol", "Transaction_Type", "Net_Value"]].head(5).to_string(index=False))


# ============================================================
# SECTION 7: memory_usage(deep=True) — Profiling RAM Usage
# ============================================================
# df.memory_usage() shows bytes per column.
# deep=True counts actual string content (not just pointers).
# Use this to identify which columns eat the most RAM.

print("\n" + "=" * 60)
print("SECTION 7: Memory Profiling — Column-Level RAM Usage")
print("=" * 60)

df_check = pd.read_csv(CSV_FILE)
mem_by_col = (
    df_check.memory_usage(deep=True)
    .reset_index()
)
mem_by_col.columns = ["Column", "Bytes"]
mem_by_col = mem_by_col[mem_by_col["Column"] != "Index"]
mem_by_col["KB"] = (mem_by_col["Bytes"] / 1024).round(2)
mem_by_col = mem_by_col.sort_values("KB", ascending=False)

print(mem_by_col[["Column", "KB"]].to_string(index=False))
print(f"\nTotal: {round(mem_by_col['KB'].sum(), 1)} KB")


# ============================================================
# SECTION 8: COMPLETE PIPELINE — Chunked + Optimized
# ============================================================
# Best practice for production:
# usecols + dtype + chunksize all together

print("\n" + "=" * 60)
print("SECTION 8: Production-Grade Pipeline — All Optimizations Combined")
print("=" * 60)

sector_totals = []

for chunk in pd.read_csv(
    CSV_FILE,
    usecols=["Date", "Sector", "Transaction_Type", "Net_Value", "Quantity"],
    dtype={"Sector": "category", "Transaction_Type": "category",
           "Net_Value": "float32", "Quantity": "int32"},
    chunksize=1000,
):
    # Filter only BUY transactions
    chunk_buy = chunk[chunk["Transaction_Type"] == "BUY"]

    # Aggregate Net_Value by Sector
    agg = chunk_buy.groupby("Sector")["Net_Value"].sum().reset_index()
    agg.columns = ["Sector", "Total_Invested"]
    sector_totals.append(agg)

# Combine and finalize
sector_final = (
    pd.concat(sector_totals, ignore_index=True)
    .groupby("Sector")["Total_Invested"]
    .sum()
    .reset_index()
    .sort_values("Total_Invested", ascending=False)
)

sector_final["Total_Invested_Cr"] = (sector_final["Total_Invested"] / 1e7).round(2)

print("Sector-wise Total BUY Investment:")
print(sector_final[["Sector", "Total_Invested_Cr"]].rename(
    columns={"Total_Invested_Cr": "Invested (Cr)"}).to_string(index=False))

print("\n✅ Day 58 Complete — CSV & Large File Handling")
