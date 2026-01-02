# %%
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use("seaborn-v0_8")

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


# %%
df = pd.read_csv("../data/arena_all.csv")

print(f"Rows: {len(df)}")
print("Unique augments:", df["augment_name"].nunique())

df.head()


# %%
df["survival_score"] = (
    (df["totalDamageTaken"].fillna(0)
     + df["damageSelfMitigated"].fillna(0)
     + 0.5 * df["totalHeal"].fillna(0))
    / (df["deaths"].fillna(0) + 1)
)

df[["augment_name", "survival_score"]].head()


# %%
coverage_target = 95

augment_counts = df["augment_name"].value_counts().reset_index()
augment_counts.columns = ["augment_name", "count"]
augment_counts["cumulative_pct"] = (
    augment_counts["count"].cumsum()
    / augment_counts["count"].sum()
    * 100
)

cutoff_rank = (augment_counts["cumulative_pct"] <= coverage_target).sum()
keep_augments = augment_counts.iloc[:cutoff_rank]["augment_name"]

df = df[df["augment_name"].isin(keep_augments)].copy()

print(f"Kept {len(keep_augments)} augments (~{coverage_target}% coverage)")
print(f"Remaining rows: {len(df)}")


# %%
augment_profile = df.groupby("augment_name").agg(
    frequency=("augment_name", "size"),

    mean_damage=("totalDamageDealtToChampions", "mean"),
    std_damage=("totalDamageDealtToChampions", "std"),

    mean_survival=("survival_score", "mean"),
    std_survival=("survival_score", "std"),

    mean_kda=("kda", "mean"),
    std_kda=("kda", "std"),

    mean_rarity=("rarity", "mean")
).reset_index()

augment_profile.fillna(0, inplace=True)

augment_profile.head()


# %%
features = [
    "mean_damage",
    "mean_survival",
    "mean_kda"
]


X = augment_profile[features].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# %%
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)

print("Explained variance (PC1, PC2):", pca.explained_variance_ratio_)
print("Total explained:", pca.explained_variance_ratio_.sum())


# %%
# Final clustering choice based on silhouette analysis
# k=4 was tested but rejected due to lower silhouette score
k = 3

kmeans = KMeans(n_clusters=k, random_state=42, n_init=20)
labels = kmeans.fit_predict(X_scaled)

sil = silhouette_score(X_scaled, labels)
print(f"Final model: k={k}, silhouette={sil:.3f}")


# %%
cluster_summary = df_plot.groupby("cluster")[features].mean()
cluster_summary["n_augments"] = df_plot["cluster"].value_counts().sort_index()

cluster_summary


# %%
loadings = pd.DataFrame(
    pca.components_,
    columns=features,
    index=["PC1", "PC2"]
)

loadings


# %%
# --- Map cluster IDs to interpretable labels ---
cluster_labels = {
    0: "Offensive-focused augments",
    1: "Survivability-focused augments",
    2: "Extreme-risk outlier"
}

df_plot = augment_profile.copy()
df_plot["pc1"] = X_pca[:, 0]
df_plot["pc2"] = X_pca[:, 1]
df_plot["cluster"] = labels
df_plot["cluster_label"] = df_plot["cluster"].map(cluster_labels)

# --- Compute centroids in PCA space ---
centroids = df_plot.groupby("cluster")[["pc1", "pc2"]].mean().reset_index()
centroids["cluster_label"] = centroids["cluster"].map(cluster_labels)

# --- Plot ---
plt.figure(figsize=(9, 7))

sns.scatterplot(
    data=df_plot,
    x="pc1", y="pc2",
    hue="cluster_label",
    palette="tab10",
    s=60,
    alpha=0.65
)

# Axis labels with explained variance
pc1_var = pca.explained_variance_ratio_[0] * 100
pc2_var = pca.explained_variance_ratio_[1] * 100

plt.xlabel("PC1: Survivability & consistency (KDA-driven)")
plt.ylabel("PC2: Damage-oriented performance")


plt.title(
    "Outcome-Based Clustering of Arena Augments\n"
    "Two dominant strategies with comparable damage but different survivability",
    fontsize=13
)

plt.legend(title="Augment Archetype", frameon=True)
plt.tight_layout()
plt.savefig("../figures/pca_outcome_clusters_with_outlier.png", dpi=300, bbox_inches="tight")
plt.show()


# %%
# --- Map cluster IDs to interpretable labels ---
cluster_labels = {
    0: "Offensive-focused augments",
    1: "Survivability-focused augments",
    2: "Extreme-risk outlier"
}

df_plot = augment_profile.copy()
df_plot["pc1"] = X_pca[:, 0]
df_plot["pc2"] = X_pca[:, 1]
df_plot["cluster"] = labels
df_plot["cluster_label"] = df_plot["cluster"].map(cluster_labels)

# --- Filter out the extreme-risk outlier for visualization only ---
df_viz = df_plot[df_plot["cluster"] != 2].copy()

# --- Compute centroids (excluding outlier) ---
centroids = (
    df_viz.groupby("cluster")[["pc1", "pc2"]]
    .mean()
    .reset_index()
)
centroids["cluster_label"] = centroids["cluster"].map(cluster_labels)

# --- Plot ---
plt.figure(figsize=(9, 7))

sns.scatterplot(
    data=df_viz,
    x="pc1", y="pc2",
    hue="cluster_label",
    palette="tab10",
    s=60,
    alpha=0.65
)

# Plot centroids
plt.scatter(
    centroids["pc1"], centroids["pc2"],
    marker="X",  color="black", label="Cluster centroid", alpha=0.8
)

# Center axes at origin
plt.axhline(0, color="gray", linestyle="--", linewidth=1, alpha=0.5)
plt.axvline(0, color="gray", linestyle="--", linewidth=1, alpha=0.5)

# Axis labels with interpretation
pc1_var = pca.explained_variance_ratio_[0] * 100
pc2_var = pca.explained_variance_ratio_[1] * 100

plt.xlabel(f"PC1: Survivability & consistency (KDA-driven) ({pc1_var:.1f}% var)")
plt.ylabel(f"PC2: Damage-oriented performance ({pc2_var:.1f}% var)")

plt.title(
    "Outcome-Based Clustering of Arena Augments\n"
    "Two dominant strategies with comparable damage but different survivability",
    fontsize=13
)

plt.legend(title="Augment Archetype", frameon=True)
plt.tight_layout()
# --- Force symmetric axes around origin ---
x_lim = max(abs(df_viz["pc1"].min()), abs(df_viz["pc1"].max()))
y_lim = max(abs(df_viz["pc2"].min()), abs(df_viz["pc2"].max()))

plt.xlim(-x_lim, x_lim)
plt.ylim(-y_lim, y_lim)
plt.savefig("../figures/pca_outcome_clusters.png", dpi=300, bbox_inches="tight")
plt.show()


# %%
# --- Map cluster IDs to interpretable labels ---
cluster_labels = {
    0: "Offensive-focused augments",
    1: "Survivability-focused augments",
    2: "Extreme-risk outlier"
}

# --- Prepare data for visualization ---
df_box = df_plot.copy()
df_box["cluster_label"] = df_box["cluster"].map(cluster_labels)

# Remove the extreme-risk outlier for visualization clarity
df_box = df_box[df_box["cluster"] != 2]

# --- Plot ---
fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharex=True)

sns.boxplot(
    data=df_box,
    x="cluster_label", y="mean_damage",
    ax=axes[0]
)
axes[0].set_title("Mean Damage by Augment Archetype")
axes[0].set_xlabel("")
axes[0].set_ylabel("Average Damage to Champions")

sns.boxplot(
    data=df_box,
    x="cluster_label", y="mean_survival",
    ax=axes[1]
)
axes[1].set_title("Mean Survivability by Augment Archetype")
axes[1].set_xlabel("")
axes[1].set_ylabel("Average Survivability Score")

sns.boxplot(
    data=df_box,
    x="cluster_label", y="mean_kda",
    ax=axes[2]
)
axes[2].set_title("Mean KDA by Augment Archetype")
axes[2].set_xlabel("")
axes[2].set_ylabel("Average KDA")

plt.suptitle(
    "Outcome Distributions of Arena Augment Archetypes",
    fontsize=14, y=1.05
)

plt.tight_layout()
plt.savefig("../figures/augment_outcome_distributions.png", dpi=300, bbox_inches="tight")
plt.show()



