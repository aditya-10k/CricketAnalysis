import pandas as pd
import numpy as np

# ===============================
# CONFIG
# ===============================
IN_CSV = "outputs/player_daily_innings_impact.csv"
OUT_CSV = "outputs/player_form_overlay.csv"

MIN_INNINGS = 5
FORM_CAP = 0.5
WINDOWS = ["5", "10", "180"]

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv(IN_CSV)
df["date"] = pd.to_datetime(df["date"])

# Use WPA only (consistent with saved models)
df = df[df["impact_type"] == "WPA"].copy()

# Total impact per innings
df["total_impact"] = (
    df["bat_value"].fillna(0) + df["bowl_value"].fillna(0)
)

df = df.sort_values(["player", "date", "innings"])

# ===============================
# ROLLING HELPERS
# ===============================
def last_n_mean(series, n):
    if len(series) < n:
        return np.nan
    return series.iloc[-n:].mean()

def last_180d_mean(df_p, col):
    cutoff = df_p["date"].max() - pd.Timedelta(days=180)
    w = df_p[df_p["date"] >= cutoff]
    if len(w) < MIN_INNINGS:
        return np.nan
    return w[col].mean()

# ===============================
# PLAYER-LEVEL ROLLING MEANS
# ===============================
rows = []

for player, g in df.groupby("player"):
    row = {
        "player": player,
        "last_match_date": g["date"].max(),
        "innings_played": len(g)
    }

    for col in ["bat_value", "bowl_value", "total_impact"]:
        row[f"{col}_5"] = last_n_mean(g[col], 5)
        row[f"{col}_10"] = last_n_mean(g[col], 10)
        row[f"{col}_180"] = last_180d_mean(g, col)

    rows.append(row)

form_raw = pd.DataFrame(rows)

# ===============================
# Z-SCORE PER WINDOW (POPULATION)
# ===============================
def zscore(series):
    mu = series.mean()
    sigma = series.std()
    if sigma == 0 or np.isnan(sigma):
        return series * 0
    return (series - mu) / sigma

for col in form_raw.columns:
    if col.endswith(("_5", "_10", "_180")):
        valid = form_raw[col].notna()
        form_raw.loc[valid, col + "_z"] = zscore(form_raw.loc[valid, col])
        form_raw.loc[~valid, col + "_z"] = np.nan

# ===============================
# GLOBAL INVERSE-VARIANCE WEIGHTS
# ===============================
window_variance = {}

for w in WINDOWS:
    cols = [c for c in form_raw.columns if c.endswith(f"_{w}_z")]
    vals = form_raw[cols].values.flatten()
    vals = vals[~np.isnan(vals)]
    window_variance[w] = np.var(vals)

inv_vars = {
    w: (1 / window_variance[w]) if window_variance[w] > 0 else 0
    for w in WINDOWS
}

total_inv = sum(inv_vars.values())

WINDOW_WEIGHTS = {
    w: inv_vars[w] / total_inv if total_inv > 0 else 0
    for w in WINDOWS
}

# ===============================
# COMBINE WINDOWS → FORM SCORE
# ===============================
output = []

for _, r in form_raw.iterrows():
    out = {
        "player": r["player"],
        "last_match_date": r["last_match_date"],
        "form_confidence": min(1.0, r["innings_played"] / 10)
    }

    for base in ["bat_value", "bowl_value", "total_impact"]:
        form = 0.0
        used = False

        for w in WINDOWS:
            z = r.get(f"{base}_{w}_z")
            if not np.isnan(z):
                form += WINDOW_WEIGHTS[w] * z
                used = True

        if not used:
            form = 0.0

        form = float(np.clip(form, -FORM_CAP, FORM_CAP))
        out[f"form_{base.split('_')[0]}_z"] = form

    output.append(out)

# ===============================
# SAVE OUTPUT
# ===============================
form_overlay = pd.DataFrame(output)
form_overlay.to_csv(OUT_CSV, index=False)

print("✅ player_form_overlay.csv created successfully (clean, no warnings)")
