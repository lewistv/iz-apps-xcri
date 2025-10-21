# XCRI Rankings \- Frequently Asked Questions

This document contains FAQ content for the XCRI Rankings frontend website.

---

## FAQ 1: What is the XCRI?

The **XCRI (Cross Country Rating Index)** is a comprehensive ranking system designed to evaluate cross country runners and teams throughout the season using only performance data from the season-in-question. The XCRI takes into account:

- **Head-to-Head Performance**: Direct comparisons between athletes in the same races  
- **Common Opposition:** Apples-to-apples comparisons of performance between common opponents  
- **Strength of Field**: The quality of competition faced

The XCRI provides objective, deterministic ratings that provide a means of understanding relative performance.

---

## FAQ 2: How are Individual XCRI Rankings Calculated?

Individual XCRI rankings use a **round-by-round elimination** process called the **Knockout Algorithm**. This approach emphasizes who beats whom in actual races as its primary driver.

### Step 1: Collect Race Results

Only data provided to and collected by AthleticNET is subject for calculation. The system gathers the provided race results and tracks:

- Who competed against whom in each race  
- Finish positions (1st, 2nd, 3rd, etc.)  
- Adjusted time per kilometer (course-normalized pace to 8k men and 6k women)

**Example**:

- Alex finishes 15th, Brady finishes 20th in the same race  
- This head-to-head result is recorded  
- Results are tracked across all races throughout the season

### Step 2: Round-by-Round Selection

The algorithm works **from the top down**, selecting one athlete at a time:

1. All eligible athletes start as potential candidates  
2. In each round, the algorithm identifies **up to 50 candidates** most likely to be selected next  
3. Candidates are chosen based on: The top-finishing,  non-selected athlete among the domain-in-question (i.e., among NAIA athletes for the NAIA rankings) in each valid race AND best season average adjusted time per kilometer.   
4. Among those candidates, the athlete who survives a **process-of-elimination procedure** that evaluates all candidates is selected and assigned the next rank  
5. The process repeats until all athletes are ranked

**How candidate selection works**: Athletes who finish near already-selected athletes become candidates to be selected sooner. Therefore, the algorithm looks first to  athletes who have finished in actual races at the front among the remaining peer group.

### Step 3: Pairwise Comparison (How Rankings Are Determined)

When comparing two athletes to determine who should be selected (ranked higher), the algorithm uses these criteria **in order**:

1. **Most Recent Common Race**: If the athletes competed in the same race, the one who finished ahead is selected  
     
   - Direct race results take priority over everything else  
   - Uses the most recent race if they met multiple times

   

2. **Common Opponents**: Count wins against shared competition  
     
   - Who beat more athletes that both have faced?  
   - Example: Alex beat 12 common opponents, Brady beat 8 → **Alex is selected** (ranks higher)

   

3. **Quality of Wins**: Best opponent quality among athletes defeated (based on adjusted time per km)  
     
   - Who has beaten the strongest athlete (fastest adjusted time)?  
   - Must be 3+ seconds difference to matter (prevents noise)  
   - Example: Alex's best win was against an athlete with 3:05/km pace, Brady's best win was 3:30/km → **Alex is selected**

   

4. **SCS Fallback**: Season Composite Score (comprehensive statistical metric)  
     
   - Used when the above criteria can't separate athletes  
   - Ensures no ties in final rankings  
   - See "What is the SCS?" below for details

---

**Key Insight**: The Knockout Algorithm prioritizes **actual race results** (who beat whom) over statistical models, ensuring rankings reflect competitive ability rather than just performance times.

---

## FAQ 3: How Does Round-by-Round Selection Work?

The **Knockout Algorithm** uses a top-down selection approach to build rankings. This section explains the technical details of how athletes are evaluated and selected.

### Example Round

**Round 10**: Selecting the 10th ranked athlete (3,991 athletes remaining)

1. Algorithm identifies 50 candidates most likely to be selected (based on finishing ahead in races and season average)  
2. Candidates enter process-of-elimination: compared pairwise using the hierarchy  
3. Candidates are eliminated one by one (e.g., Candidate B eliminated because Candidate A finished ahead in their most recent race)  
4. Process continues until only one candidate survives  
5. **Candidate A survives elimination** and is assigned rank \#10  
6. Process continues to select rank \#11 (3,990 remaining athletes)

**Key Insight**: The algorithm systematically selects athletes from the top down using a process-of-elimination “knockout” tournament.

---

## FAQ 4: How are Team Rankings Calculated?

Team rankings are based on the **top 7 athletes** from each team, following NCAA cross country scoring rules. This section explains how team scores are calculated and what factors contribute to team rankings.

### Calculation Method

#### **Identify Top 7 Athletes**

For each team, the algorithm identifies the top 7 athletes based on their individual XCRI rankings.

**Example \- Harvard Men's Team**:

- Graham Blanks (XCRI Rank: 1\)  
- Additional 6 top athletes  
- These 7 athletes form the scoring squad  
- The top-five athletes’ scores comprise the actual team score

#### **Calculate Team Score**

The team score is calculated by **summing the XCRI ranks** of the top 5 athletes. Lower total score \= better team ranking.

**Example**:

- Top 7 Ranks: 1, 15, 42, 68, 95, (112), (140)  
- **Team Score**: 1 \+ 15 \+ 42 \+ 68 \+ 95 \= **221**

This follows the standard cross country scoring system where lower scores are better.

---

## FAQ 5: What is the SCS and Why is it NOT the Primary Ranking?

The **SCS (Season Composite Score)** is a ranking that attempts to balance three factors: **(1) the athlete's performance**, **(2) the athlete's performance relative to others in each race**, and **(3) the strength of each race relative to other races during the season**. This section explains what SCS is, how it's calculated, and why it's used as a secondary metric rather than the primary ranking.

### What is SCS?

SCS is a **comprehensive statistical score** that evaluates an athlete's performance across the season using a 17-step calculation with seven key components:

1. **AGS** (Adjusted Gap Score): Raw performance adjusted for field strength  
2. **SAGA** (Season Adjusted Gap Average): Average AGS across all races  
3. **CPR** (Contest Performance Rating): Race-specific performance rating  
4. **SEWR** (Season Equal-Weight Rating): Average CPR across all races giving equal weighting based on number of runners faced in each race  
5. **OSMA** (Opponent SEWR Moving Average): Strength of schedule metric  
6. **SCS** (Final Score): Weighted combination of SEWR (60%) and OSMA (40%)  
7. **SCS Rank**: Ranking based on XCRI score

### Why SCS is NOT the Primary Ranking

The system uses the **Knockout Algorithm** as the primary ranking instead of SCS for several important reasons:

#### **Knockout Algorithm (Primary Ranking)** 

- **Reflects Actual Race Outcomes**: Based on who actually beats whom in races  
- **Accounts for Competitive Context**: Recognizes that racing is about competition  
- **Evidence-Based**: Uses direct race results and pairwise comparisons  
- **Emphasizes Who Beats Whom**: Direct matchups are the gold standard

#### **SCS (Secondary Metric)** 

- **Based on Adjusted Performance Times**: Statistical modeling rather than direct competition  
- **Can Overvalue Athletes Who Race Weaker Fields**: Posting fast times and posting large winning gaps against weak competition inflates SCS  
- **May Not Reflect Championship Potential**: Time-based metrics don't always predict head-to-head outcomes

### When SCS is Used

Despite not being the primary ranking, SCS serves three important purposes:

#### **Tiebreaker (Fourth Criterion)**

When two athletes cannot be separated by:

- Most recent common race  
- Common opponents analysis  
- Quality of wins comparison

SCS provides the final tiebreaker to ensure no athletes have identical ranks.

**Example**:

- Athlete A and Athlete B never raced each other  
- No common opponents  
- Both defeated similar quality opponents  
- Athlete A has SCS of 1025, Athlete B has SCS of 1020  
- **Athlete A ranks higher** due to better SCS, likely due to a better gap between them and their competition at race finish

#### **Statistical Comparison**

SCS allows comparison of athletes who haven't raced each other directly. Coaches and analysts can use SCS to estimate how athletes from different regions might compare statistically.

---

## FAQ 6: What are All the Components of the SCS?

The Season Composite Score is calculated through a **17-step statistical process** with **7 key components**. This section provides a detailed breakdown of each component, how it's calculated, and what it represents.

### Component Overview

The SCS calculation follows this progression:

```
Raw Times → AGS → SAGA → CPR → SEWR → OSMA → XCRI → SCS Rank
```

Each step builds on the previous, creating a comprehensive statistical profile of an athlete's season.

---

### 1\. AGS (Adjusted Gap Score)

**What it is**: Raw performance time adjusted for field strength and race context

**How it's calculated**:

1. Compare athlete's time to the race winner's time  
2. Calculate the time gap (athlete time \- winner time)  
3. Adjust for the quality of the field (using 75th percentile cutoff)  
4. Normalize for race context and performance level

**Formula** (simplified):

```
AGS = (Athlete Time - Winner Time) × Field Quality Factor × Context Factor
```

**Example**:

- Race 1: Athlete runs 25:30, winner runs 24:00 in a **strong field** (top 75% under 26:00)  
    
  - Gap: 90 seconds  
  - Field Quality Factor: 0.8 (strong field reduces gap impact)  
  - AGS: 90 × 0.8 \= **72** (good AGS)


- Race 2: Athlete runs 25:30, winner runs 26:00 in a **weak field** (top 75% over 28:00)  
    
  - Gap: \-30 seconds (athlete beat winner\!)  
  - Field Quality Factor: 1.2 (weak field increases gap impact)  
  - AGS: \-30 × 1.2 \= **\-36** (excellent AGS)

**Interpretation**:

- Lower AGS \= Better performance  
- Negative AGS \= Beat high-quality competition  
- AGS accounts for field strength, so 25:30 in a strong field \> 25:00 in a weak field

---

### 2\. SAGA (Season Adjusted Gap Average)

**What it is**: Average AGS across all races, with outlier removal

**How it's calculated**:

1. Collect all AGS scores from the season  
2. If athlete has 3+ races, drop the worst AGS (outlier removal)  
3. Calculate the average of remaining AGS scores

**Formula**:

```
SAGA = Average(AGS scores, excluding worst if 3+ races)
```

**Example**:

- Athlete has 5 races with AGS scores: 95, 72, 102, 88, 110  
- Drop worst: 110  
- SAGA \= (95 \+ 72 \+ 102 \+ 88\) ÷ 4 \= **89.25**

**Interpretation**:

- Lower SAGA \= More consistent strong performance  
- SAGA removes outliers to focus on typical performance level  
- Athletes with more races have more stable SAGA values

---

### 3\. CPR (Contest Performance Rating)

**What it is**: Race-specific performance rating that compares performance to expected level

**How it's calculated**:

1. Establish expected performance based on athlete's season history  
2. Compare actual performance to expected performance  
3. Account for race quality and field strength  
4. Scale to 1000-point system (1000 \= expected performance)

**Formula** (simplified):

```
CPR = 1000 + (Expected Performance - Actual Performance) × Scaling Factor
```

**Example**:

- Athlete's expected AGS based on season history: 95  
- Actual AGS in this race: 72 (better than expected)  
- Performance improvement: 95 \- 72 \= 23  
- Scaling factor: 1.5  
- CPR \= 1000 \+ (23 × 1.5) \= **1034.5**

**Interpretation**:

- CPR \> 1000: Exceeded expected performance  
- CPR \= 1000: Met expected performance  
- CPR \< 1000: Underperformed relative to expectations  
- Higher CPR in high-quality races \= particularly impressive

---

### 4\. SEWR (Season Equal-Weight Rating)

**What it is**: Average CPR across all races, giving equal weight to each race based on number of athletes faced

**How it's calculated**:

1. Collect all CPR scores from the season  
2. Calculate simple average (no outlier removal)  
3. Equal weight to each race regardless of quality or timing

**Formula**:

```
SEWR = Average(All CPR scores)
```

**Example**:

- Athlete has 5 races with CPR scores: 1020, 1035, 1015, 1042, 1018  
- SEWR \= (1020 \+ 1035 \+ 1015 \+ 1042 \+ 1018\) ÷ 5 \= **1026**

**Interpretation**:

- SEWR represents athlete's consistent performance level  
- Higher SEWR \= More consistent strong performances  
- SEWR does not favor later-season races over early-season

---

### 5\. OSMA (Opponent SEWR Moving Average)

**What it is**: Strength of schedule metric based on opponents faced

**How it's calculated**:

1. For each race, identify all opponents faced  
2. Calculate the average SEWR of all opponents  
3. Weight by number of matchups (more opponents \= more data)  
4. Compute moving average across all races

**Formula**:

```
OSMA = Weighted Average of (Average Opponent SEWR per race)
```

**Example**:

- Race 1: Faced 50 opponents, average opponent SEWR \= 1010  
- Race 2: Faced 75 opponents, average opponent SEWR \= 1020  
- Race 3: Faced 60 opponents, average opponent SEWR \= 1005  
- OSMA \= \[(50×1010) \+ (75×1020) \+ (60×1005)\] ÷ (50+75+60) \= **1012.4**

**Interpretation**:

- Higher OSMA \= Faced stronger competition  
- OSMA rewards athletes who compete against top-tier fields  
- Accounts for strength of schedule across the season

---

### 6\. SCS (Final Score)

**What it is**: Weighted combination of SEWR (own performance) and OSMA (competition strength)

**How it's calculated**:

1. SEWR represents own performance quality (60% weight)  
2. OSMA represents competition faced (40% weight)  
3. Calculate weighted average  
4. Scale to 1000-point system

**Formula**:

```
XCRI = (0.6 × SEWR) + (0.4 × OSMA)
```

**Example**:

- Athlete SEWR: 1026  
- Athlete OSMA: 1012  
- XCRI \= (0.6 × 1026\) \+ (0.4 × 1012\) \= 615.6 \+ 404.8 \= **1020.4**

**Interpretation**:

- Higher XCRI \= Better overall season performance and competition faced  
- 60/40 split favors own performance but rewards strong schedules  
- XCRI combines "how well" with "against whom"

**Component Weights**:

- Own Performance (SEWR): 60% \- rewards athletes who perform well  
- Strength of Schedule (OSMA): 40% \- rewards athletes who face tough competition

---

### 7\. SCS Rank

**What it is**: Final ranking based on SCS score

**How it's calculated**:

1. Sort all athletes by XCRI score (descending order)  
2. Assign ranks: 1, 2, 3, ..., N  
3. Ties broken by: SEWR, then SAGA, then AGS

**Example**:

- Athlete A: XCRI \= 1025  
- Athlete B: XCRI \= 1020  
- Athlete C: XCRI \= 1020 (tied with B)  
- Athlete D: XCRI \= 1015

**Rankings**:

1. Athlete A (1025)  
2. Athlete B (1020) \- wins tiebreaker with better SEWR  
3. Athlete C (1020)  
4. Athlete D (1015)

**Interpretation**:

- Lower SCS Rank \= Better statistical season performance  
- SCS Rank 1 \= Best statistical performance across all athletes  
- Tiebreakers ensure no duplicate ranks

---

### Viewing Component Breakdown

Each athlete's profile in the XCRI system includes a detailed component breakdown:

#### **Summary View**

- **SCS Score**: Overall value (e.g., 1020.4)  
- **SCS Rank**: Ranking based on SCS (e.g., 120\)

#### **Component Scores**

- **SAGA**: 89.25 (Rank: 150\) \- Season adjusted gap average  
- **SEWR**: 1026 (Rank: 75\) \- Own performance rating  
- **OSMA**: 1012 (Rank: 200\) \- Strength of schedule  
- **SCS**: 1020.4 (Rank: 120\) \- Final composite score

*All scores are z-score normalized to the population. 1000 points marks the median and 100-points in either direction represents a standard deviation difference from the median (i.e., a score of 1150 in any component means for that particular component, the athlete scored 1.5 standard deviations better than the median athlete)*

#### **Race-by-Race Breakdown**

Each individual race shows:

- **AGS**: Gap score for that race  
- **CPR**: Performance rating for that race  
- **Opponent Quality**: Average SEWR of opponents in that race

---

### Key Takeaways

1. **Progressive Calculation**: Each component builds on the previous, creating a comprehensive statistical profile  
     
2. **Accounts for Multiple Factors**:  
     
   - Raw performance (AGS)  
   - Consistency (SAGA, SEWR)  
   - Race-specific excellence (CPR)  
   - Competition quality (OSMA)  
   - Overall composite (XCRI)

   

3. **Transparency**: Athletes and coaches will be able to can see exactly how their SCS is calculated and which components drive their ranking  
     
4. **Use Cases**:  
     
   - Tiebreaker for Knockout Algorithm rankings  
   - Statistical comparison tool  
   - Performance trend analysis  
   - Strength of schedule evaluation

   

5. **Complementary to Knockout Algorithm**: SCS provides statistical depth while the Knockout Algorithm focuses on competitive outcomes

---

## FAQ 7: Are These Rankings Based on Current Season Only?

**Yes**. XCRI rankings are based **solely on performances from the current cross country season**.

### Important Considerations

**Early in the Season** (September \- Early October):

- Rankings may not fully reflect a team's or athlete's potential  
- Competition may be limited for specific athletes and teams  
- Some top athletes may not have raced yet  
- Regional differences in schedule timing affect early rankings

**Mid-Season** (Mid-October \- Early November):

- Rankings become more reliable as more data accumulates  
- Most athletes have competed multiple times  
- Strength of schedule differences begin to even out

**Late Season / Championship** (Late November):

- Rankings most accurately reflect championship potential  
- Full season of head-to-head results available  
- Regional and national championship performances included

### What This Means

- **Early season rankings** are provisional and improve with more data  
- **Team potential** may not be fully reflected if key athletes haven't competed yet

**Bottom Line**: Use early season rankings as a guide, but understand they improve significantly as the season progresses and more competitive matchups occur.

---

## FAQ 8: Are XCRI Rankings Simulated or Predicted?

**No**. XCRI rankings are **objective and deterministic**, not simulated or predicted.

### What This Means

**Deterministic**:

- Same input data always produces the same rankings  
- No randomness or probability models  
- Fully reproducible results  
- Transparent algorithm

**Objective**:

- Based entirely on actual race results  
- No subjective opinions or votes  
- No simulations of hypothetical matchups  
- No predictions of future performance

### How This Differs from Other Systems

Some ranking systems use:

- **Monte Carlo simulations**: Run thousands of virtual races  
- **Predictive models**: Estimate future performance based on trends  
- **Expert polls**: Human opinions and votes  
- **Projected times**: Estimates of what athletes "would" run

**XCRI does NOT use any of these**. Rankings are based purely on:

1. Who beat whom in actual races  
2. Strength of schedule (quality of opponents faced)  
3. Consistency across multiple performances

### Benefits of Deterministic Rankings

- **Reproducible**: Can verify rankings by re-running algorithm  
- **Transparent**: Clear rules, no black-box predictions  
- **Fair**: Everyone judged by same objective criteria  
- **Stable**: Rankings change only when new race results are added

**Bottom Line**: XCRI rankings reflect **what has happened**, not what might happen or what we think will happen.

---

## FAQ 9: Do Team Rankings Consider Head-to-Head Team Results?

**No**. Team rankings are based **solely on individual athlete XCRI placements**, not head-to-head team results.

### How Team Rankings Work

Team rankings use the **top 7 athletes** from each team:

1. Each athlete has an individual XCRI score and rank  
2. Team score \= Sum of top 5 athletes' XCRI scores

### What This Means

**Team A beats Team B at a meet** does NOT directly affect team rankings.

Instead, XCRI rankings reflect:

- Individual athlete performance across the entire season  
- Squad depth (quality of top 7 athletes)  
- Strength of schedule for each athlete  
- Consistency across multiple competitions

### Why This Approach?

**Single-meet results can be misleading**:

- Absences (injury, rest, academics)  
- Tactical decisions (not running full team)  
- Course-specific advantages  
- Weather conditions on one day

**Season-long individual rankings are more reliable**:

- Capture full body of work for each athlete  
- Account for strength of schedule  
- Reflect squad depth accurately  
- Less affected by single-meet anomalies

**Example**: Team A might beat Team B at a major invitational, but if Team B's athletes have stronger individual seasons overall (better head-to-head records, tougher competition faced), Team B could rank higher in XCRI team rankings.

**Bottom Line**: Team rankings aggregate individual athlete quality, not direct team-vs-team results.

---

**Document Version**: 1.1  
**Created**: October 20, 2025  
