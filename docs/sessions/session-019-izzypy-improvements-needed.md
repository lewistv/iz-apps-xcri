# Session 019: Data Structure Improvements Needed in izzypy_xcri

**Date**: October 29, 2025
**Session**: Bug Fixes and Refinements
**Target Repository**: `izzypy_xcri` (backend data generation)

---

## Executive Summary

During Session 019 frontend/backend bug fixes for the XCRI Team Knockout feature, we identified several data structure issues that require improvements in the `izzypy_xcri` repository (the backend system that generates and populates the ranking data).

These issues prevent proper functionality of region/conference filtering and Athletic.net meet linking in the web application.

---

## Critical Issues Requiring izzypy_xcri Fixes

### 1. Region/Conference Names Not Populating in Team Knockout Rankings

**Problem**: The `iz_rankings_xcri_team_knockout` table lacks region and conference name fields, requiring a JOIN with `iz_rankings_xcri_team_rankings` to retrieve them. However, the JOIN is failing because the tables use different primary key structures.

**Current State**:
- Team Knockout table has: `team_id`, `season_year`, `rank_group_fk`, `gender_code`, `checkpoint_date`
- Team Rankings table has: `anet_team_hnd`, `season_year`, `division_code`, `gender_code`, `checkpoint_date`, **`algorithm_type`**, **`scoring_group`**

**Issue**: The JOIN fails because:
1. Team Rankings table requires `algorithm_type` and `scoring_group` for matching
2. Team Knockout table doesn't have these fields
3. No way to reliably join the two tables

**Impact**:
- ❌ Region names don't display in Team Knockout table
- ❌ Conference names don't display in Team Knockout table
- ❌ Region/Conference filters don't work in Team Knockout view
- ❌ Latest race date doesn't display

**Recommended Fix in izzypy_xcri**:

Add the following columns directly to `iz_rankings_xcri_team_knockout` table during data generation:

```python
# In batch_xcri_team_knockout.py or equivalent

# When generating Team Knockout rankings, also fetch and store:
regl_group_name: str        # Region name (e.g., "Great Lakes", "Southeast")
conf_group_name: str        # Conference name (e.g., "Big 12", "ACC")
most_recent_race_date: date # Team's latest race date
```

**Rationale**:
- Avoids complex JOINs with mismatched key structures
- Improves query performance (no JOIN needed)
- Data is static at calculation time, so denormalization is acceptable
- Follows same pattern as other denormalized fields in the table

**Alternative Solution** (less preferred):
Add `algorithm_type` and `scoring_group` to Team Knockout table, but this adds unnecessary fields since Team Knockout doesn't use these concepts.

---

### 2. Athletic.net Meet Links Require Separate meet_id and race_id

**Problem**: The `iz_rankings_xcri_team_knockout_matchups` table only stores `race_hnd` (AthleticNET race ID), but Athletic.net URLs require both a `meet_id` and `race_id`.

**Current URL Format** (incorrect):
```
https://www.athletic.net/CrossCountry/meet/{race_hnd}/results/{race_hnd}?tab=team-scores
```

**Correct URL Format** (needed):
```
https://www.athletic.net/CrossCountry/meet/{meet_id}/results/{race_id}?tab=team-scores
```

**Example Issue**:
- race_hnd: 1073547
- Generated URL: `/meet/1073547/results/1073547` ← Wrong, uses race_id twice
- Correct URL: `/meet/123456/results/1073547` ← Needs actual meet_id

**Impact**:
- ❌ Meet links in Matchup History modal may link to wrong meet
- ❌ Links may 404 if meet_id ≠ race_id
- ⚠️ Currently using race_hnd for both parameters as workaround

**Recommended Fix in izzypy_xcri**:

Add `meet_id` field to `iz_rankings_xcri_team_knockout_matchups` table:

```python
# In team knockout matchup data generation

# When collecting matchup data from Athletic.net:
matchup_record = {
    'race_hnd': race_id,        # Keep existing field
    'meet_id': meet_id,         # ADD THIS NEW FIELD
    'race_date': race_date,
    'meet_name': meet_name,
    # ... other fields
}
```

**Data Source**: Athletic.net API should provide both `meet_id` and `race_id` when fetching race results.

---

### 3. Varsity Team Designation Not Stored in Database

**Problem**: The Team Knockout algorithm description mentions "varsity" team determination, but there's no field in the database indicating whether a matchup involved varsity teams.

**Current State**:
- No `is_varsity` or similar flag in `iz_rankings_xcri_team_knockout_matchups`
- No way to filter matchups to varsity-only
- Algorithm determines varsity status internally but doesn't persist it

**Impact**:
- ⚠️ Cannot filter matchup history to varsity-only matchups
- ⚠️ Win-loss records may include non-varsity matchups
- ⚠️ No way to validate if a matchup met varsity criteria

**Recommended Fix in izzypy_xcri** (optional, for future enhancement):

Add varsity designation fields:

```python
# In iz_rankings_xcri_team_knockout_matchups table

team_a_is_varsity: bool  # Was Team A fielding varsity squad?
team_b_is_varsity: bool  # Was Team B fielding varsity squad?
matchup_type: str        # "varsity_vs_varsity", "varsity_vs_jv", etc.
```

**Note**: This is lower priority since the algorithm already filters to varsity matchups during calculation. However, storing this explicitly would enable:
- Better debugging and validation
- Future filtering options in the UI
- Historical analysis of varsity vs non-varsity performance

---

### 4. Opponent KO Rank Not Available in Matchup Data

**Problem**: User requested opponent KO rank to be displayed in matchup history, but this data isn't stored in the matchups table.

**Current State**:
- Matchup table has: `team_a_rank`, `team_b_rank` (finish places in race)
- Does NOT have: opponent's Team Knockout ranking at time of matchup

**Impact**:
- ❌ Cannot display opponent's KO rank in matchup history modal
- ❌ Cannot sort matchups by opponent strength (KO rank)
- ⚠️ Users cannot easily identify which matchups were against top-ranked opponents

**Recommended Fix in izzypy_xcri**:

Add opponent KO rank fields to matchup records:

```python
# In iz_rankings_xcri_team_knockout_matchups table

team_a_ko_rank: int  # Team A's knockout rank at time of matchup
team_b_ko_rank: int  # Team B's knockout rank at time of matchup
```

**Challenge**: This requires storing knockout ranks as they evolve throughout the season, not just final ranks. Options:

1. **Snapshot approach**: Store KO rank at time of each matchup (preferred)
2. **Calculation-time approach**: Use final KO ranks only (less accurate but simpler)
3. **Deferred**: Wait until future season for implementation

**User Feedback**: "Add a column to the left of opponent for 'KO Rank' and show that? Also sort by KO Rank, showing the best-ranked KO ranked opponents up top?"

---

## Lower Priority Data Improvements

### 5. Season/Gender Filtering for Matchups

**Current State**: Matchup API returns all matchups for a team, but filtering by specific season/gender is done application-side.

**Recommended**: Ensure backend stores season_year and gender_code consistently across all matchup records for efficient filtering.

### 6. Place (Finish Position) Representation

**Current State**: Database stores `team_a_rank` and `team_b_rank` as integers (1, 2, 3, etc.)

**UI Preference**: Display as ordinals (1st, 2nd, 3rd, 4th, etc.)

**Status**: ✅ Already handled in frontend formatting, no database changes needed.

---

## Implementation Priority

### High Priority (Blocks Key Features)
1. **Region/Conference Names** - Prevents filtering and display
2. **Meet ID for Athletic.net Links** - Breaks external navigation

### Medium Priority (Enhances UX)
3. **Opponent KO Rank** - User-requested feature for matchup analysis
4. **Varsity Team Designation** - Enables filtering and validation

### Low Priority (Nice to Have)
5. Season/Gender filtering optimizations
6. Additional metadata fields for analytics

---

## Testing Recommendations

After implementing these fixes in izzypy_xcri:

1. **Regenerate Team Knockout Rankings**: Run full calculation with updated schema
2. **Validate Data Population**: Ensure new fields are populated for all records
3. **Test JOIN Compatibility**: If using JOIN approach, verify match rates
4. **Check URL Validity**: Test Athletic.net links with actual meet_id/race_id pairs
5. **Verify Filters**: Test region/conference filtering with populated data

---

## Contact for Questions

- **Web App Issues**: XCRI Rankings web application repository
- **Data Generation Issues**: izzypy_xcri repository
- **This Report**: Session 019 wrap-up documentation

---

**Status**: Awaiting izzypy_xcri implementation
**Next Steps**: Implement high-priority fixes in izzypy_xcri, regenerate data, re-test web application

