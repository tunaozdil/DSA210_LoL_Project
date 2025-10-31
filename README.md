# DSA210 Project Proposal  
**Title:** Augment Appearance Trends and Their Effects on Champion Stats in League of Legends: Arena Mode  

---

### Motivation  
Two years ago, the popular video game *League of Legends* introduced a new gamemode called **Arena**.  
This mode added a feature called **Augments** — randomized power-ups that significantly change how a character (called a *champion*) performs during matches.  
Each player chooses several augments per game, and there are nearly 200 different options overall.  
The randomness and variety make Arena an interesting case for studying how random elements influence player behavior and performance.  

This project will explore how often different augments appear in my matches and how they relate to measurable **champion performance statistics** such as damage dealt, survivability, and the **KDA ratio** (kills + assists ÷ deaths).  
If permitted to keep the repository private, I will also analyze *average placement* — a player’s **final ranking in the 16-players, 8-teams match (1 = best, 8 = lowest)** — for additional insight.

---

### Data Source  
- **Collected by:** Myself using a *personal Riot Games API key* (developer key) to collect data from my own match history.  
- **Endpoints:**  
  - `https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid`  
  - `https://{REGION}.api.riotgames.com/lol/match/v5/matches/{matchId}`  
- **Mode:** Arena (`queueId = 1700`)  
- **Augment names:** Mapped from [CommunityDragon](https://raw.communitydragon.org/15.21/cdragon/arena/en_us.json).  
- Each match includes data for **all 16 players** (8 teams of 2), expanding the dataset from ~300 matches to roughly **4,800 player entries**.

---

### Data Analysis Plan  
1. **Collection & Cleaning:**  
   - Extract champion, augment, combat, and ranking information for all participants.  
   - Convert augment IDs to readable names using CommunityDragon data.  

2. **Exploratory Analysis:**  
   - Measure how frequently each augment appears across all players.  
   - Visualize the percentile distribution of augment appearances.  
   - Analyze relationships between augments and **champion statistics** (KDA, gold earned, damage dealt, etc.).  
   - *(Private-only)* Compute **average placement** (final match ranking) per augment for internal analysis.  

3. **Machine Learning:**  
   - Use simple, interpretable models to explore how augments relate to champion performance metrics.  
   - Classify whether a player achieves above-average KDA or damage based on their augment choices.  

---

### Expected Findings  
- Frequency and percentile rankings of augments across all players.  
- Insights into how different augments relate to champion performance metrics.  
- Visualizations showing augment diversity and common augment combinations.  
- *(Private-only)* Exploratory results connecting augments to final match rankings.

---

### Limitations & Future Work  
- Riot’s API policy forbids public display of augment winrates.  
- Data currently represents only my matches, limiting generalization.  
- **If the repository remains private**, average placement and related statistics will be analyzed internally.  
- I plan to contact friends to include their match data, expanding the dataset for broader representation.

---

### Ethical Statement  
This project uses data collected via the Riot Games API under a **personal developer key** for educational, non-commercial use.  
No private player data or match performance statistics are shared publicly.  
All results comply with Riot’s API Terms of Service.  
Riot Games does not endorse or sponsor this project.
