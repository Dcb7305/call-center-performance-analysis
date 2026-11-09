from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# --- Load the data ---
# The CSV lives one folder up from this script (in the repo root)
DATA_FILE = Path(__file__).resolve().parent.parent / "Call Center Data.csv"
df = pd.read_csv(DATA_FILE)

# --- Convert percent columns: "94.01%" -> 0.9401 ---
for col in ["Answer Rate", "Service Level (20 Seconds)"]:
    df[col] = df[col].str.rstrip("%").astype(float) / 100

# --- Convert time columns: "0:02:14" -> 134 seconds ---
for col in ["Answer Speed (AVG)", "Talk Duration (AVG)", "Waiting Time (AVG)"]:
    df[col] = pd.to_timedelta(df[col]).dt.total_seconds()

# --- Step 3: 30-row rolling averages ---
WINDOW = 30
trend_cols = ["Incoming Calls", "Answer Rate", "Abandoned Calls", "Service Level (20 Seconds)"]
for col in trend_cols:
    df[f"{col} (30-row avg)"] = df[col].rolling(window=WINDOW).mean()

# Compare the first full window to the last one
first = df.iloc[WINDOW - 1]
last = df.iloc[-1]
print("\n--- Trend check: start vs. end (30-row averages) ---")
for col in trend_cols:
    start, end = first[f"{col} (30-row avg)"], last[f"{col} (30-row avg)"]
    print(f"{col:30} start: {start:8.3f}   end: {end:8.3f}   change: {end - start:+8.3f}")

# --- Step 4: Plot the trends ---
CHART_DIR = Path(__file__).resolve().parent / "charts"
CHART_DIR.mkdir(exist_ok=True)

fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharex=True)
for ax, col in zip(axes.flat, trend_cols):
    ax.plot(df["Index"], df[col], color="lightgray", linewidth=0.8, label="Raw")
    ax.plot(df["Index"], df[f"{col} (30-row avg)"], color="steelblue", linewidth=2, label="30-row avg")
    ax.set_title(col)
    ax.grid(alpha=0.3)
for ax in axes[1]:
    ax.set_xlabel("Index (row order)")
axes[0, 0].legend()
fig.suptitle("Call Center Trends (30-row rolling average)", fontsize=14)
fig.tight_layout()
fig.savefig(CHART_DIR / "trends.png", dpi=150)
print(f"\nChart saved to {CHART_DIR / 'trends.png'}")

# --- Step 5: Does call volume drive performance? ---
perf_cols = ["Answer Rate", "Service Level (20 Seconds)", "Waiting Time (AVG)", "Abandoned Calls"]
corr = df[perf_cols].corrwith(df["Incoming Calls"])
print("\n--- Correlation with Incoming Calls (-1 to +1) ---")
print(corr.round(2).to_string())

# Compare the crisis stretch (rows 690-950) to everything else
crisis = df["Index"].between(690, 950)
compare = pd.DataFrame({
    "Crisis (690-950)": df.loc[crisis, ["Incoming Calls"] + perf_cols].mean(),
    "Rest of data": df.loc[~crisis, ["Incoming Calls"] + perf_cols].mean(),
})
print("\n--- Crisis period vs. rest of data (averages) ---")
print(compare.round(3).to_string())

# --- Step 6: Export a Tableau-ready CSV ---
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

tableau_df = df.rename(columns={
    "Answer Speed (AVG)": "Answer Speed (sec)",
    "Talk Duration (AVG)": "Talk Duration (sec)",
    "Waiting Time (AVG)": "Waiting Time (sec)",
})
tableau_df["Period"] = crisis.map({True: "Crisis (690-950)", False: "Normal"})
tableau_df["Volume Band"] = pd.cut(
    tableau_df["Incoming Calls"],
    bins=[0, 150, 300, float("inf")],
    labels=["Low (<150)", "Medium (150-300)", "High (300+)"],
)
tableau_df.to_csv(OUTPUT_DIR / "call_center_tableau.csv", index=False)
print(f"\nTableau file saved to {OUTPUT_DIR / 'call_center_tableau.csv'}")