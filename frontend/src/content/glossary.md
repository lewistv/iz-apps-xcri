# XCRI Rankings Glossary

Comprehensive guide to technical terms used in the XCRI (Cross Country Rating Index) ranking system.

---

## A

### AGS (Adjusted Gap Score)

**Definition**: Raw performance time adjusted for field strength and race context. **Used in**: SCS calculation (Component \#1) **Why it matters**: Allows fair comparison of performances from different races. **Example**: Running 25:30 in a strong field yields better AGS than 25:00 in a weak field.

---

## C

### Common Opponents

**Definition**: Athletes that two compared athletes have both raced against. **Used in**: Knockout Algorithm tiebreaking (Criterion \#2) **Why it matters**: If two athletes haven't raced each other, comparing wins against shared opponents reveals relative strength. **Example**: Alex beat 12 common opponents, Brady beat 8 → Alex advances.

### CPR (Contest Performance Rating)

**Definition**: Race-specific performance rating scaled to 1000-point system. **Used in**: SCS calculation (Component \#3) **Why it matters**: Measures whether athlete exceeded, met, or underperformed expectations in a specific race.

---

## D

### Distance Normalization

**Definition**: Mathematical correction for converting raw race times to distance-normalized pace (time per kilometer). **Used in**: Season average calculation (adjusted time per km) **Why it matters**: Allows comparison of performances across different race distances (e.g., 5K vs 6K, 5 Miles vs 8K, etc.). **Note**: This adjustment only normalizes for race distance, not for course terrain or weather conditions.

---

## H

### H2H (Head-to-Head)

**Definition**: Direct comparison between two athletes who competed in the same race. **Used in**: Knockout Algorithm primary ranking logic **Why it matters**: Most reliable indicator of competitive ability \- who actually beat whom.

---

## K

### Knockout Algorithm

**Definition**: Round-by-round elimination algorithm that ranks athletes based on pairwise comparisons using direct race results. **Used in**: Primary XCRI ranking system **Why it matters**: More accurately represents direct performance amongst peers than statistical models. 

**Tiebreaking Hierarchy**:

1. Most Recent Common Race  
2. Common Opponents  
3. Quality of Wins  
4. SCS Fallback

---

## M

### Most Recent Common Race

**Definition**: The most recent race where two athletes competed together. **Used in**: Knockout Algorithm tiebreaking (Criterion \#1) **Why it matters**: Direct race results are the strongest evidence of relative ability. **Example**: If Alex and Brady raced last week and Alex finished ahead, Alex advances in pairwise comparison.

---

## O

### One-Removed Average

**Definition**: Season average calculation that drops the worst race if an athlete has 3+ races. **Used in**: Season average calculation, internal fallback logic **Why it matters**: Provides more stable performance measure by removing outliers.

### OSMA (Opponent SEWR Moving Average)

**Definition**: Strength of schedule metric based on average SEWR of all opponents faced. **Used in**: SCS calculation (Component \#5) **Why it matters**: Rewards athletes who compete against top-tier competition.

---

## P

### Pairwise Comparison

**Definition**: Systematic comparison of two athletes using hierarchical tiebreaking criteria. **Used in**: Knockout Algorithm elimination process **Why it matters**: Ensures objective, consistent ranking decisions based on actual evidence.

---

## Q

### Quality of Wins

**Definition**: Metric measuring the strength of opponents an athlete has defeated, based on the best (fastest) opponent's adjusted time per kilometer. **Used in**: Knockout Algorithm tiebreaking (Criterion \#3) **Why it matters**: Beating an athlete with 3:05/km pace is more impressive than beating one with 3:30/km pace. **Threshold**: Must be 3+ seconds difference to matter (prevents noise from affecting rankings). **Note**: This is a **time-based metric** \- quality is determined by the defeated opponent's season average adjusted time per kilometer.

---

## R

### Round-by-Round Selection

**Definition**: Top-down ranking process where one athlete is selected per round. **Used in**: Knockout Algorithm **How it works**: Start with all athletes, select strongest in each round using pairwise comparisons, assign ranks from top down (rank \#1, then \#2, then \#3, etc.).

---

## S

### SAGA (Season Adjusted Gap Average)

**Definition**: Average AGS across all races with outlier removal. **Used in**: SCS calculation (Component \#2) **Why it matters**: Represents consistent performance level throughout season.

### SCS (Season Composite Score)

**Definition**: A ranking that attempts to balance three factors: (1) the athlete's performance, (2) the athlete's performance relative to others in each race, and (3) the strength of each race relative to other races during the season. Calculated through a 17-step process \= (0.6 × SEWR) \+ (0.4 × OSMA). **Used in**: Secondary ranking metric, fourth tiebreaker in Knockout Algorithm **Why it matters**: Provides statistical comparison when head-to-head data is insufficient. 

**Components**:

1. AGS \- Adjusted Gap Score  
2. SAGA \- Season Adjusted Gap Average  
3. CPR \- Contest Performance Rating  
4. SEWR \- Season Equal-Weight Rating  
5. OSMA \- Opponent SEWR Moving Average  
6. SCS \- Final composite score  
7. SCS Rank \- Ranking by XCRI score

### Season Average

**Definition**: Average race performance (time per kilometer, distance-normalized). **Used in**: Internal fallback (only if SCS calculation fails) **Why it matters**: Baseline performance measure across different race distances. **Note**: Uses "one-removed" averaging (drops worst race if 3+ races).

### SEWR (Season Equal-Weight Rating)

**Definition**: Average CPR across all races, giving equal weight to each race. **Used in**: SCS calculation (Component \#4) **Why it matters**: Represents athlete's consistent performance level.

### Strength of Schedule

**Definition**: Measure of competition quality based on opponents faced. **Used in**: OSMA calculation, quality assessment **Why it matters**: Competing against top athletes indicates higher skill level.

---

## T

### Tiebreaking Hierarchy

**Definition**: Ordered criteria used when athletes are compared in Knockout Algorithm. **Used in**: Pairwise comparison in Knockout Algorithm **Order** (applied sequentially until one criterion separates the athletes):

1. **Most Recent Common Race** \- Direct race finish order  
2. **Common Opponents** \- Win count against shared competition  
3. **Quality of Wins** \- Strongest opponent defeated (3+ second threshold)  
4. **SCS Fallback** \- Season Composite Score

---

## Race Qualification Rules

### Qualifying Distance

**Definition**: Minimum race distance for performances to count toward rankings. 

**2024 and 2025 Criteria**:

- NCAA DI Men: 7.5K minimum  
- NCAA DI Women: 4.5K minimum  
- NCAA DII Men: 7K minimum  
- NCAA DII Women: 4.8K minimum  
- NCAA DIII Men: 7K minimum  
- NCAA DIII Women: 4.5K minimum

### Qualifying Date

**Definition**: First date of the season when races count toward rankings.   
---

## Team Scoring

### Team Score

**Definition**: Sum of top 5 athletes' individual XCRI ranks. **How it works**: Lower total \= better Team Five ranking **Example**: Ranks 1+15+42+68+95 \= Score of 221

---

**Document Version**: 2.1 **Last Updated**: October 20, 2025 
