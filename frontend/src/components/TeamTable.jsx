import React from 'react';
import { useNavigate } from 'react-router-dom';
import RankingsTable from './RankingsTable';

/**
 * Team Rankings Table Component
 *
 * Wrapper around unified RankingsTable for team-specific display.
 * Columns: XCRI Rank | Team | Team Score (integer) | Region | Conference
 *
 * Team Score = Sum of best 5 athletes' XCRI ranks (like XC race scoring)
 */
export default function TeamTable({ teams, loading, isHistorical = false }) {
  const navigate = useNavigate();

  /**
   * Handle team name click - navigate to team profile
   * Session 010: Fixed to include division/gender params, works for historical snapshots
   */
  const handleTeamClick = (team) => {
    if (team.anet_team_hnd) {
      const snapshotParam = isHistorical && team.checkpoint_date
        ? `/${team.checkpoint_date}`
        : '';
      // Include division and gender as query params for correct team lookup
      const params = new URLSearchParams({
        division: team.division_code || team.division,
        gender: team.gender_code
      }).toString();
      navigate(`/team/${team.anet_team_hnd}${snapshotParam}?${params}`);
    }
  };

  /**
   * Column configuration for team rankings
   * Order: XCRI Rank | Team | Team Score | Region | Conference
   */
  const columns = [
    {
      id: 'xcri_rank',
      label: 'XCRI Rank',
      field: 'team_rank',
      format: (value, row) => row.team_rank || row.rank || '-',
      className: 'text-center nowrap',
      tooltip: 'Overall team XCRI ranking position',
    },
    {
      id: 'team',
      label: 'Team',
      field: 'team_name',
      clickable: true,
      onClick: handleTeamClick,
      clickTitle: 'View team roster and details',
      className: 'nowrap',
    },
    {
      id: 'team_score',
      label: 'Team Score',
      field: 'team_xcri_score',
      format: (value, row) => {
        // Format as integer (per requirements)
        const score = row.team_xcri_score || row.team_score;
        return score ? Math.floor(score) : '-';
      },
      className: 'text-center',
      tooltip: 'Sum of best 5 athletes\' XCRI ranks',
    },
    {
      id: 'region',
      label: 'Region',
      field: 'regl_group_name',
      format: (value) => value || '-',
      className: 'nowrap',
    },
    {
      id: 'conference',
      label: 'Conference',
      field: 'conf_group_name',
      format: (value) => value || '-',
      className: 'nowrap',
    },
  ];

  // Add Most Recent Race column only for current LIVE rankings (Session 010)
  if (!isHistorical) {
    columns.push({
      id: 'most_recent_race',
      label: 'Latest Race',
      field: 'most_recent_race_date',
      format: (value) => {
        if (!value) return '-';
        // Format as MM/DD (e.g., "10/15")
        const date = new Date(value);
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return `${month}/${day}`;
      },
      className: 'text-center',
      tooltip: 'Most recent race among top athletes',
    });
  }

  return (
    <RankingsTable
      type="teams"
      data={teams}
      columns={columns}
      isHistorical={isHistorical}
      loading={loading}
    />
  );
}
