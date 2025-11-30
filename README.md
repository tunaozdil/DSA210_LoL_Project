# 🎯 Arena Augment Performance & Survival Analysis
*League of Legends: Arena Data Science Project (DSA210)*  
**Author:** Tuna Özdil
**Date:** November 2025  

---

## 🧩 Project Overview

This project explores **League of Legends: Arena mode**, introduced in 2023, where each player selects randomized power-ups called **Augments** during matches.  
Augments can drastically alter champion playstyles, strategies, and match outcomes — making them a rich subject for quantitative analysis.

The study investigates how **augment appearance frequency** relates to **player performance metrics**, such as:
- **KDA ratio** (kills + assists ÷ deaths)
- **Total damage dealt to champions**
- **Durability and survivability** (a derived *sustain score* based on healing and damage mitigation)

The dataset represents matches from multiple accounts (myself and consenting friends), providing thousands of Arena match records for analysis.

---

## 🧠 Motivation

Arena is a 2v2v2v2 elimination mode where randomness and adaptation define success.  
Because augments are randomly offered, players often speculate whether certain augments are objectively stronger or simply more common.  

This project aims to **quantify those relationships** by combining statistical testing and exploratory visualization to identify:
- Which augments appear most frequently,
- Whether common augments improve performance,
- And how sustain-focused augments differ statistically from offensive ones.

---

## 📚 Data Source

### **Collection**
All data were gathered **personally** through the official [Riot Games API](https://developer.riotgames.com/docs/lol) under a **personal developer key** for educational use.

- **API Endpoints Used:**
  - `GET /lol/match/v5/matches/by-puuid/{puuid}/ids`
  - `GET /lol/match/v5/matches/{matchId}`
- **Game Mode:** Arena (`queueId = 1700`)
- **Augment Names:** Mapped via [CommunityDragon JSON](https://raw.communitydragon.org/15.23/cdragon/arena/en_us.json)

### **Scope**
Each Arena match includes **16 anonymized player entries** (8 teams of 2).  
Across ~3,000 matches from multiple regions (TR1, NA1, EUW), the dataset expands to **≈ 48,000 player-level entries**.

### **Fields Used**
Only non-identifying, gameplay-relevant fields:
- `championName`, `kills`, `deaths`, `assists`
- `goldEarned`, `totalDamageDealtToChampions`, `damageSelfMitigated`
- `totalHeal`, `teamDamagePercentage`, `abilityUses`
- `playerAugment1–6` (converted to readable names)

> ⚠️ No personally identifiable information (PUUIDs, Riot IDs, usernames, etc.) is stored or shared.  
> Data is anonymized and aggregated before analysis.

---

## 📊 Data Cleaning and Preparation

- Expanded augment arrays into one record per augment (`explode` transformation).
- Mapped augment IDs → names using the CommunityDragon dataset.
- Dropped incomplete rows and invalid augment entries.
- Filtered out rare augments that together represented less than **5% of total appearances** (noise reduction).
- Combined datasets from three accounts into a unified CSV under `data/players/`.

---

## 🔬 Analysis Methodology

The analysis proceeds in three stages:

### **1️⃣ Exploratory Data Analysis (EDA)**
- **Augment frequency distribution** with cumulative coverage curve  
  → identifies dominant and rare augments.  
- **Correlation sweep** between augment frequency and 12 gameplay metrics.  
- **Regression visualization** for frequency vs. key stats (KDA, damage, sustain).  

### **2️⃣ Hypothesis Testing (Survival/Durability)**
Derived a custom **survival score**:

survival_score = (DamageTaken + DamageSelfMitigated + 0.5 × TotalHeal) / (Deaths + 1)


**H₀:** All augments yield equal survival performance.  
**H₁:** At least one augment significantly differs.  

A one-way **ANOVA test** confirmed statistically significant survival differences among augments (p < 0.001).

### **3️⃣ Hypothesis Testing (Frequency–Performance Relations)**
Two **Pearson correlation** tests examined whether augment popularity aligns with player performance.

| Hypothesis | Variable Relationship | Result | p-value | Conclusion |
|-------------|-----------------------|---------|----------|-------------|
| **H1** | Frequency ↔ Damage | r = **0.33** | 2.4e-05 | ✅ Significant positive correlation |
| **H2** | Frequency ↔ KDA | r = **-0.07** | 0.37 | ❌ No significant relationship |

---

## 📈 Key Visualizations

### **Augment Frequency Distribution (Log Scale)**
Shows a steep long-tail curve — a few augments dominate most selections.

![Augment Frequency Distribution](figures/augment_frequency_distribution_95.png)

---

### **Correlation Between Frequency and Player Metrics**
Offensive metrics (damage, ability use) rise with augment frequency.

![Correlation Between Frequency and Player Metrics](figures/freq_metric_correlation.png)

---

### **Augment Frequency vs Damage Output**
Frequent augments significantly correlate with higher damage to champions.

![Augment Frequency vs Damage Output](figures/hypothesis_freq_vs_damage.png)

---

### **Augment Frequency vs KDA**
No meaningful correlation between augment frequency and overall KDA consistency.

![Augment Frequency vs KDA](figures/hypothesis_freq_vs_kda.png)

---

### **Augments by Survival/Durability**
Derived sustain metric shows clear outliers — some augments enhance durability disproportionately.

![Top 20 Augments by Survival Score](figures/augment_survival_score.png)

---

## 🧾 Summary of Findings

| Aspect | Finding | Interpretation |
|---------|----------|----------------|
| **Frequency Distribution** | Top 80 augments cover 95% of all appearances | Arena meta favors a small subset of augments |
| **Frequency ↔ Damage** | Strong positive correlation (r = 0.33, p < 0.001) | Common augments drive offensive output |
| **Frequency ↔ KDA** | No significant correlation | Popular augments improve raw stats, not consistency |
| **Survival Score** | Significant augment-to-augment variance | Some augments enhance durability disproportionately |

---

## 🧠 Conclusions

- **Frequent augments ≠ balanced augments:** Offensive augments dominate both selection rate and output.  
- **Durability augments are distinct:** Though rarer, they show statistically significant variance in survival contribution.  
- **KDA unaffected by popularity:** Common augments boost raw output but not strategic efficiency.  
- **Arena’s meta skews toward offense, not sustain.**

---

## ⚖️ Ethical and Legal Compliance

- All data collected via the **official Riot Games API** using a personal *developer key* for academic, non-commercial use.  
- No personal identifiers or player-specific outcomes (e.g., win/loss, placement) are stored or displayed.  
- The repository includes only **aggregated statistical summaries** and **derived metrics**.  
- Public results comply with Riot’s API Terms of Service — no augment winrates, rankings, or individual outcomes are disclosed.  
- Any future private analysis involving placements will remain offline and strictly for academic evaluation.

> **Riot Games does not endorse or sponsor this project.**

---



---

## 🧩 Future Work
- Categorize augments by **function** (offensive, defensive, utility) for deeper comparative testing.  
- Study **augment co-occurrence patterns** to identify synergy effects.  
- Extend dataset across more regions and patches to analyze meta shifts.  
- *(Private only)* Integrate placement outcomes for ranking-based performance modeling.

---

## 🧰 Setup & Reproduction

### Requirements
- Python ≥ 3.10  
- Packages: `pandas`, `numpy`, `seaborn`, `matplotlib`, `scipy`, `requests`

### Run Instructions
```bash
pip install -r requirements.txt
cd notebooks
jupyter aff.py

All figures are automatically saved under figures/.

📚 References

Riot Games Developer Portal

CommunityDragon Augment Dataset

