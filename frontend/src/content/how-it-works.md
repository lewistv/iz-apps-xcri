# XCRI Rankings Explained: The Simple Version

A beginner-friendly guide to understanding XCRI (Cross Country Rating Index) rankings.

---

## What Problem Does XCRI Solve?

**The Challenge**: How do you compare cross country runners who:

- Race on different courses (flat vs. hilly)?  
- Compete in different regions?  
- Face different levels of competition?  
- Use different racing strategies 

**The Solution**: XCRI focuses on **who beats whom** rather  than race times solely.

---

## The Core Idea

Traditional rankings use race times:

- "Runner A averaged 24:30 for 8K"  
- Problem: Times vary widely based on course, weather, and altitude \- making cross-race comparisons unreliable

XCRI uses competitive results:

- "Runner A has beaten 15 top-100 opponents in direct races"  
- Better: Reflects actual competitive ability regardless of race conditions

---

## How XCRI Ranks Athletes

### The Knockout Algorithm

Think of it like this: Instead of looking at who ran the fastest times, we ask **"Who would win if everyone raced head-to-head?"**

#### **Step 1: Collect Race Results**

- Gather all race results from the season  
- Track who competed against whom  
- Record finish positions (1st, 2nd, 3rd, etc.)

#### **Step 2: Select From the Top**

The system works **from the top down** \- selecting one athlete at a time:

1. Start with all 4,000+ athletes  
2. In each round, identify 50 candidates most likely to be selected next (those who finished ahead of remaining athletes AND have best season average)  
3. Compare each pair using the tiebreaking hierarchy (see below)  
4. Use a **process-of-elimination procedure**: eliminate candidates one by one through pairwise comparisons until only one survives  
5. Repeat until everyone is ranked

**How it works**: Athletes who finished near already-selected athletes become candidates to be selected sooner.

#### **Step 3: Pairwise Comparison (Tiebreaking Hierarchy)**

When comparing two athletes, use these criteria **in order**:

**1\. Most Recent Common Race**

- Did they race each other? The one who finished ahead is selected.  
- Example: Alex 15th, Brady 20th → Alex is selected (ranks higher)  
- **Why it matters**: Direct race results are the strongest evidence

**2\. Common Opponents**

- Who beat more shared competition?  
- Example: Alex beat 12 common opponents, Brady beat 8 → Alex is selected  
- **Why it matters**: Shows relative strength when they haven't raced each other

**3\. Quality of Wins**

- Who has beaten the strongest athlete (based on opponent's adjusted time per km)?  
- Example: Alex's best win was against an athlete with 3:05/km pace, Brady's best win was 3:30/km → Alex is selected  
- **Why it matters**: Beating top competition (faster athletes) is more impressive  
- **Note**: This is a **time-based metric**. Must be 3+ seconds difference to matter.

**4\. SCS Fallback**

- Use statistical composite score (see below)  
- Example: Alex SCS 1050, Brady SCS 1020 → Alex is selected  
- **Why it matters**: Ensures no ties in final rankings

### Example: Alex vs. Brady

**Scenario 1**: They raced together

- Check most recent race: Alex 15th, Brady 20th  
- **Result**: Alex is selected (ranks higher)

**Scenario 2**: They never raced, but have common opponents

- Alex beat 15 common opponents  
- Brady beat 10 common opponents  
- **Result**: Alex is selected (ranks higher)

**Scenario 3**: No common race, no common opponents

- Check quality of wins: Alex's best win defeated an athlete with 3:10/km pace, Brady's best win was 3:35/km  
- **Result**: Alex is selected (ranks higher)

**Scenario 4**: Everything tied

- Check SCS: Alex 1050, Brady 1020  
- **Result**: Alex is selected (ranks higher)

---

## What is SCS and Why Isn't It the Primary Ranking?

### SCS (Season Composite Score)

SCS is a ranking that attempts to balance three factors:

1. **The athlete's performance** (how fast they run)  
2. **The athlete's performance relative to others in each race** (how they compare to the field)  
3. **The strength of each race relative to other races during the season** (quality of competition)

Calculated through a 17-step statistical process that combines these elements.

**Think of it like**: A balanced performance rating that considers speed, competitiveness, and strength of schedule.

### Why SCS is Secondary

The **Knockout Algorithm** is primary because:

✅ **Championships use place-based scoring** \- In cross country, 1st place \= 1 point, 2nd place \= 2 points, etc. Finish position matters, not time.

✅ **Tactical racing is valid** \- An athlete who sits and kicks to win (slower time, better place) is more competitive than one who runs fast but loses.

✅ **Head-to-head beats statistics** \- Beating someone in a race is stronger evidence than a statistical projection.

✅ **Better championship prediction** \- Knockout Algorithm better predicts who will perform well at championships.

### When SCS Matters

Despite being secondary, SCS is valuable:

**1\. As a Tiebreaker**

- When pairwise comparisons can't separate athletes  
- Ensures no ties in final rankings

**2\. For Statistical Analysis**

- Comparing athletes from different regions who haven't raced  
- Identifying athletes improving statistically

**3\. As a Secondary Metric**

- Provides additional context beyond competitive results

---

## How Team Five Rankings Work

**Simple Version**: Add up the ranks of your top 5 athletes. Lowest total wins.

### NCAA Cross Country Team Scoring

**Rules**:

1. Team must have at least 5 finishers  
2. Only top 7 athletes earn a place score  
3. Team score \= sum of top 5 individual ranks

**Example**:

- **Team Harvard**: Individual ranks 1, 15, 42, 68, 95, 112, 140
- **Team Score**: 1 \+ 15 \+ 42 \+ 68 \+ 95 \= **221**

Lower score \= better Team Five ranking.

### What Makes a Great Team?

1. **Elite front-runner** (\#1 ranked athlete in single digits or low teens)  
2. **Strong pack** (\#2-\#5 all in top 100\)  
3. **Good depth** (\#6-\#7 competitive, \#8 runner close behind)
