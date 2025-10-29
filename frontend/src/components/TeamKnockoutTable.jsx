import React from 'react';
import { useNavigate } from 'react-router-dom';
import RankingsTable from './RankingsTable';
import './TeamKnockoutTable.css';

/**
 * Team Knockout Rankings Table Component
 *
 * Wrapper around unified RankingsTable for Team Knockout rankings display.
 * Team Knockout rankings are based on head-to-head (H2H) matchup results
 * rather than aggregate scores.
 *
 * Columns: Knockout Rank | Team | Region | Conference | Record (W-L) | Win % | Team Five Rank
 *
 * Session 018: Phase 1 - Core rankings table implementation
 */
export default function TeamKnockoutTable({
  teams,
  loading,
  isHistorical = false,
  onMatchupClick = null
}) {
  const navigate = useNavigate();

  /**
   * Handle team name click - navigate to team profile
   * Reuses same navigation pattern as TeamTable
   */
  const handleTeamClick = (team) => {
    if (team.anet_team_hnd || team.team_id) {
      const teamHandle = team.anet_team_hnd || team.team_id;
      const snapshotParam = isHistorical && team.checkpoint_date
        ? `/${team.checkpoint_date}`
        : '';
      // Include division and gender as query params for correct team lookup
      const params = new URLSearchParams({
        division: team.rank_group_fk || team.division_code || team.division,
        gender: team.gender_code
      }).toString();
      navigate(`/team/${teamHandle}${snapshotParam}?${params}`);
    }
  };

  /**
   * Handle win-loss record click - open matchup history modal
   * Session 018: Opens modal showing team's complete matchup history
   */
  const handleRecordClick = (team) => {
    if (onMatchupClick) {
      onMatchupClick(team);
    }
  };

  /**
   * Format win-loss record as "W-L (Win%)"
   */
  const formatRecord = (wins, losses) => {
    const totalGames = wins + losses;
    if (totalGames === 0) return '0-0 (0.0%)';

    const winPct = ((wins / totalGames) * 100).toFixed(1);
    return `${wins}-${losses} (${winPct}%)`;
  };

  /**
   * Column configuration for Team Knockout rankings
   * Order: Knockout Rank | Team | Region | Conference | Record | Win % | Team Five Rank
   */
  const columns = [
    {
      id: 'knockout_rank',
      label: 'KO Rank',
      field: 'knockout_rank',
      format: (value) => value || '-',
      className: 'text-center nowrap',
      tooltip: 'Team Knockout ranking based on H2H win-loss record',
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
    {
      id: 'record',
      label: 'Record (W-L)',
      field: 'h2h_wins',
      format: (wins, row) => formatRecord(row.h2h_wins || 0, row.h2h_losses || 0),
      clickable: !!onMatchupClick,
      onClick: onMatchupClick ? handleRecordClick : null,
      clickTitle: onMatchupClick ? 'View matchup history' : '',
      className: 'text-center nowrap record-cell',
      tooltip: 'Click to view complete matchup history',
    },
    {
      id: 'team_five_rank',
      label: 'TF Rank',
      field: 'team_five_rank',
      format: (value) => value || '-',
      className: 'text-center',
      tooltip: 'Traditional Team Five ranking for comparison',
    },
    {
      id: 'team_size',
      label: 'Size',
      field: 'team_size',
      format: (value) => value || '-',
      className: 'text-center',
      tooltip: 'Number of athletes on team roster',
    },
  ];

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
