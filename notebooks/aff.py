# %% [markdown]
# # 🎯 Arena Augment Performance & Survival Analysis
#
# This notebook performs exploratory data analysis (EDA) and hypothesis testing on League of Legends: Arena mode data.
#
# **Objective:**  
# Explore how augment frequency and selection patterns relate to gameplay performance metrics such as KDA, damage output, and survival proxies.

# %%
# === Setup ===
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import requests
plt.style.use("seaborn-v0_8")

# %%
# === Load and Combine Player Data ===
# Loads Arena match data collected from multiple players and merges them into a single DataFrame.

data_path = "../data/players"
files = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith(".csv")]
df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
print(f"Loaded {len(df)} player records from {len(files)} files.")
print(df.columns.tolist())

# %%
# === Data Cleaning ===
# - Parses augment IDs from list strings
# - Maps augment IDs → names via CommunityDragon
# - Drops invalid or missing rows

import ast

if "augments" not in df.columns:
    raise KeyError("Expected column 'augments' not found. Verify that CSVs were generated with collect_data_arena.py.")

def safe_eval(x):
    if isinstance(x, str):
        try:
            val = ast.literal_eval(x)
            if isinstance(val, list):
                return val
        except Exception:
            return []
    return x if isinstance(x, list) else []

df["augments"] = df["augments"].apply(safe_eval)
df = df.explode("augments").rename(columns={"augments": "augment_id"})
df = df[df["augment_id"].notna()]
df["augment_id"] = df["augment_id"].astype(int)

try:
    aug_data = requests.get("https://raw.communitydragon.org/15.23/cdragon/arena/en_us.json").json()
    augment_map = {int(a["id"]): a["name"] for a in aug_data["augments"]}
    df["augment_name"] = df["augment_id"].map(augment_map)
    print(f"✅ Mapped {df['augment_name'].nunique()} augment names.")
except Exception as e:
    print("⚠️ Could not load augment map:", e)
    df["augment_name"] = df["augment_id"]

df = df.dropna(subset=["augment_name", "kda", "champLevel", "totalDamageDealtToChampions"])
print(f"Remaining valid rows after cleaning: {len(df)}")

# %% [markdown]
# ## Augment Frequency Distribution
# Visualize how often each augment appears across all recorded Arena games.  
# A cumulative coverage curve shows how many unique augments account for most of the appearances.

# %%
coverage_target = 95  # cumulative coverage target in percent

augment_counts = df["augment_id"].value_counts().reset_index()
augment_counts.columns = ["augment_id", "count"]
augment_counts["augment_name"] = augment_counts["augment_id"].map(augment_map)
augment_counts = augment_counts.sort_values("count", ascending=False).reset_index(drop=True)
augment_counts["cumulative_pct"] = augment_counts["count"].cumsum() / augment_counts["count"].sum() * 100

cutoff_index = augment_counts[augment_counts["cumulative_pct"] >= coverage_target].index[0]
cutoff_augment = augment_counts.iloc[cutoff_index]
cutoff_rank = cutoff_index + 1

fig, ax1 = plt.subplots(figsize=(12,6))
sns.barplot(x=augment_counts.index, y=augment_counts["count"], color="skyblue", ax=ax1)
ax1.set_yscale("log")
ax1.set_xlabel("Augments (sorted by frequency rank)")
ax1.set_ylabel("Occurrences (log scale)", color="blue")
ax1.set_xticks([])

ax2 = ax1.twinx()
ax2.plot(augment_counts.index, augment_counts["cumulative_pct"], color="orange", linewidth=2)
ax2.set_ylabel("Cumulative % of All Augment Appearances", color="orange")

ax2.axhline(coverage_target, color="gray", linestyle="--", linewidth=1)
ax2.axvline(cutoff_index, color="red", linestyle="--", linewidth=1)
ax2.text(len(augment_counts)*0.9, coverage_target-3, f"{coverage_target}% coverage", color="gray")
ax2.text(cutoff_index + 3, coverage_target + 2, f"{coverage_target}% coverage @ rank {cutoff_rank}", color="red", fontsize=10)

plt.title(f"Augment Frequency Distribution and {coverage_target}% Coverage Threshold")
plt.tight_layout()
plt.savefig(f"../figures/augment_frequency_distribution_{coverage_target}.png", dpi=300)
plt.show()

top_20_coverage = augment_counts.iloc[:20]["cumulative_pct"].iloc[-1]
print(f"Top 20 augments account for {top_20_coverage:.1f}% of all appearances.")
print(f"{coverage_target}% coverage reached at rank {cutoff_rank} (augment ID {int(cutoff_augment['augment_id'])}).")

# %% [markdown]
# ## Filter Rare Augments
# Keep only the top augments that together represent 95% of total appearances.  
# This reduces noise from rarely appearing or champion-specific augments.

# %%
augment_counts = df["augment_id"].value_counts().reset_index()
augment_counts.columns = ["augment_id", "count"]
augment_counts["cumulative_pct"] = augment_counts["count"].cumsum() / augment_counts["count"].sum() * 100

coverage_target = 95
cutoff_rank = (augment_counts["cumulative_pct"] <= coverage_target).sum()
cutoff_count = augment_counts.iloc[cutoff_rank - 1]["count"]
print(f"95% coverage achieved with top {cutoff_rank} augments (≥ {cutoff_count} occurrences).")

keep_ids = augment_counts.iloc[:cutoff_rank]["augment_id"]
df = df[df["augment_id"].isin(keep_ids)]
print(f"Remaining rows after 95% coverage filter: {len(df)} ({coverage_target}% coverage retained)")

# %% [markdown]
# # Exploratory Data Analysis (EDA)
# In this section, we investigate:
# 1. Frequency of each augment  
# 2. Relationship between frequency and performance metrics  
# 3. Survival proxies  
# 4. General metric correlations

# %%
metrics = [
    "kda", "goldEarned", "champLevel", "totalDamageDealtToChampions",
    "totalDamageTaken", "totalHeal", "damageSelfMitigated",
    "teamDamagePercentage", "damageTakenOnTeamPercentage",
    "abilityUses", "skillshotsHit", "skillshotsDodged"
]
augment_stats = df.groupby("augment_name")[metrics].mean().reset_index()
augment_stats["frequency"] = df["augment_name"].value_counts().reindex(augment_stats["augment_name"]).values
print(augment_stats.head())

# %% [markdown]
# ## E1: Augment Frequency Overview

# %%
top_freq = augment_stats.sort_values("frequency", ascending=False).head(20)
plt.figure(figsize=(10,6))
sns.barplot(y="augment_name", x="frequency", data=top_freq, palette="crest")
plt.title("Top 20 Most Frequent Augments")
plt.xlabel("Appearances in Dataset")
plt.ylabel("Augment")
plt.tight_layout()
plt.savefig("../figures/eda_augment_frequency.png", dpi=300)
plt.show()

# %% [markdown]
# ## E2: Frequency vs. Player Metrics
# Examine how augment popularity correlates with different gameplay statistics.

# %%
corrs = {m: augment_stats["frequency"].corr(augment_stats[m]) for m in metrics}
corr_df = pd.DataFrame.from_dict(corrs, orient="index", columns=["correlation"]).sort_values("correlation", ascending=False)

plt.figure(figsize=(10,5))
sns.barplot(data=corr_df, x="correlation", y=corr_df.index, palette="coolwarm")
plt.title("Correlation Between Augment Frequency and Player Metrics")
plt.axvline(0, color="gray", linestyle="--")
plt.tight_layout()
plt.savefig("../figures/freq_metric_correlation.png", dpi=300)
plt.show()
print(corr_df)

# %% [markdown]
# ## E3: Frequency vs. Key Metrics (Scatterplots)

# %%
key_metrics = [
    "kda", "goldEarned", "champLevel", "totalDamageDealtToChampions",
    "totalDamageTaken", "totalHeal", "damageSelfMitigated",
    "teamDamagePercentage", "damageTakenOnTeamPercentage",
    "abilityUses", "skillshotsHit", "skillshotsDodged"
]
fig, axes = plt.subplots(6, 2, figsize=(12,34))
for ax, m in zip(axes.flat, key_metrics):
    sns.regplot(data=augment_stats, x="frequency", y=m, ax=ax, scatter_kws={'s':40}, line_kws={'color':'red'})
    ax.set_title(f"Frequency vs {m}")
plt.tight_layout()
plt.savefig("../figures/freq_key_scatterplots.png", dpi=300)
plt.show()

# %% [markdown]
# # Hypothesis Testing - Augments and Survival/Durability
# While raw KDA and damage indicate offensive performance, they overlook player **durability** — how long a champion stays active in combat.
#
# We define a derived metric:
# 
# ```
# survival_score = (DamageTaken + DamageSelfMitigated + 0.5 × TotalHeal) / (Deaths + 1)
# ```
#
# This captures **sustainability** — how well a player absorbs or mitigates damage before dying.  
# Higher values indicate augments that favor **tanks, sustainers, or bruisers** that prolong fights.


# %%
df_surv = df[df["augment_name"] != "Wisdom of Ages"].copy()
df_surv["survival_score"] = (
    (df_surv["totalDamageTaken"].fillna(0)
     + df_surv["damageSelfMitigated"].fillna(0)
     + 0.5 * df_surv["totalHeal"].fillna(0))
    / (df_surv["deaths"].fillna(0) + 1)
)

anova_surv = stats.f_oneway(*[g["survival_score"].dropna() for _, g in df_surv.groupby("augment_name")])
print(f"ANOVA (survival_score) F={anova_surv.statistic:.3f}, p={anova_surv.pvalue:.4f}")
print(f"✅ Survival ANOVA complete — significant augment-to-augment differences detected (p = {anova_surv.pvalue:.3e})" if anova_surv.pvalue < 0.05 else "❌ No significant survival variation detected between augments.")

top_surv = (
    df_surv.groupby("augment_name")["survival_score"]
    .mean()
    .sort_values(ascending=False)
    .head(20)
)
plt.figure(figsize=(10,6))
sns.barplot(x=top_surv.values, y=top_surv.index, palette="crest")
plt.title("Top 20 Augments by Derived Survival Score")
plt.xlabel("Average Survival Score (DamageTaken + Mitigated + 0.5×Heal / Deaths+1)")
plt.tight_layout()
plt.savefig("../figures/augment_survival_score.png", dpi=300)
plt.show()

# %% [markdown]
# # Hypothesis Testing - Damage and KDA vs. Frequency
# In this section, we test two hypotheses based on earlier EDA findings:
#
# **H1:** More frequently chosen augments lead to higher average **damage output**.  
# **H2:** More frequently chosen augments lead to higher average **KDA**.  
#
# Both are tested using the **Pearson correlation coefficient**.

# %%
r_dmg, p_dmg = stats.pearsonr(augment_stats["frequency"], augment_stats["totalDamageDealtToChampions"])
print(f"Pearson correlation (frequency ↔ damage): r = {r_dmg:.3f}, p = {p_dmg:.3e}")

if p_dmg < 0.05:
    print("✅ Significant positive relationship — more frequent augments tend to yield higher damage.")
else:
    print("❌ No significant relationship detected.")

plt.figure(figsize=(8,6))
sns.regplot(data=augment_stats, x="frequency", y="totalDamageDealtToChampions", scatter_kws={'s':50}, line_kws={'color':'red'})
plt.title("Relationship Between Augment Frequency and Average Damage")
plt.xlabel("Augment Frequency (Appearances in Dataset)")
plt.ylabel("Average Damage to Champions")
plt.tight_layout()
plt.savefig("../figures/hypothesis_freq_vs_damage.png", dpi=300)
plt.show()

# %%
# --- H2: Frequency ↔ KDA ---
r_kda, p_kda = stats.pearsonr(augment_stats["frequency"], augment_stats["kda"])
print(f"H2 — Pearson correlation (frequency ↔ KDA): r = {r_kda:.3f}, p = {p_kda:.3e}")

if p_kda < 0.05:
    print("✅ Significant relationship detected between augment frequency and KDA.")
else:
    print("❌ No significant relationship — frequent augments do not meaningfully affect KDA.")

plt.figure(figsize=(8,6))
sns.regplot(
    data=augment_stats, x="frequency", y="kda",
    scatter_kws={'s':50}, line_kws={'color':'red'}
)
plt.title("H2 — Relationship Between Augment Frequency and KDA")
plt.xlabel("Augment Frequency (Appearances in Dataset)")
plt.ylabel("Average KDA")
plt.tight_layout()
plt.savefig("../figures/hypothesis_freq_vs_kda.png", dpi=300)
plt.show()
# %% [markdown]
# # Summary & Conclusions
# **Hypothesis Results:**
# - **H0 (Survival):** Rejected — significant survival variation among augments.
# - **H1:** Frequency ↔ Damage → Significant positive correlation (offensive augments dominate).
# - **H2:** Frequency ↔ KDA → No significant correlation (p ≫ 0.05).
#
# **Interpretation:**
# - Offensive metrics scale with popular augments, but kill/death balance (KDA) remains largely unaffected.  
# - Suggests that common augments improve raw output rather than survivability or consistency.
# Survival-enhancing augments are rarer but statistically distinct, supporting a trade-off between sustain and raw output.


# %%
