import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import RankingsTable from './RankingsTable';
import SCSModal from './SCSModal';

/**
 * Athlete Rankings Table Component
 *
 * Wrapper around unified RankingsTable for athlete-specific display.
 * Columns: XCRI Rank | Athlete | Team | Region | Conference | SCS Score | SCS Rank | Races
 *
 * NOTE: SCS component breakdown only available for current rankings (MySQL data)
 *       Historical snapshots lack athlete handles needed for component API
 */
export default function AthleteTable({ athletes, loading, isHistorical = false }) {
  const navigate = useNavigate();
  const [selectedAthlete, setSelectedAthlete] = useState(null);
  const [showSCSModal, setShowSCSModal] = useState(false);

  /**
   * Handle SCS score click - open modal with component breakdown
   * Only works for current rankings with athlete handles
   */
  const handleSCSClick = (athlete) => {
    if (!isHistorical && athlete.anet_athlete_hnd) {
      setSelectedAthlete(athlete);
      setShowSCSModal(true);
    }
  };

  /**
   * Handle team name click - navigate to team profile
   */
  const handleTeamClick = (athlete) => {
    if (athlete.anet_team_hnd) {
      const snapshotParam = isHistorical && athlete.checkpoint_date
        ? `/${athlete.checkpoint_date}`
        : '';
      // Include division and gender as query params for correct team lookup
      const params = new URLSearchParams({
        division: athlete.division_code,
        gender: athlete.gender_code
      }).toString();
      navigate(`/team/${athlete.anet_team_hnd}${snapshotParam}?${params}`);
    }
  };

  /**
   * Column configuration for athlete rankings
   * Order: XCRI Rank | Athlete | Team | Region | Conference | SCS Score | SCS Rank | Races
   */
  const columns = [
    {
      id: 'xcri_rank',
      label: 'XCRI Rank',
      field: 'athlete_rank',
      format: (value, row) => row.athlete_rank || row.rank || '-',
      className: 'text-center nowrap',
      tooltip: 'Overall XCRI ranking position',
    },
    {
      id: 'athlete',
      label: 'Athlete',
      field: 'athlete_name',
      format: (value, row) => {
        // Handle different data structures
        const fullName = row.athlete_name_first && row.athlete_name_last
          ? `${row.athlete_name_first} ${row.athlete_name_last}`
          : row.athlete_name || 'Unknown';

        // Session 009C: Add Athletic.net link if athlete handle available
        if (row.anet_athlete_hnd) {
          return (
            <a
              href={`https://www.athletic.net/CrossCountry/Athlete.aspx?AID=${row.anet_athlete_hnd}`}
              target="_blank"
              rel="noopener noreferrer"
              className="athlete-name-link"
              onClick={(e) => e.stopPropagation()}
              title="View on Athletic.net"
            >
              {fullName} <span className="external-link-icon">↗</span>
            </a>
          );
        }

        return fullName;
      },
      className: 'nowrap',
    },
    {
      id: 'team',
      label: 'Team',
      field: 'team_name',
      clickable: true,
      onClick: handleTeamClick,
      clickTitle: 'View team profile',
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
      id: 'scs_score',
      label: 'SCS Score',
      field: 'scs_score',
      format: (value) => value ? value.toFixed(2) : '-',
      clickable: !isHistorical, // Only clickable for current rankings
      onClick: !isHistorical ? handleSCSClick : null,
      clickTitle: !isHistorical ? 'View SCS component breakdown' : null,
      className: 'text-center',
      tooltip: 'Season Composite Score (Heavy XCRI)',
    },
    {
      id: 'scs_rank',
      label: 'SCS Rank',
      field: 'scs_rank',
      format: (value) => value || '-',
      className: 'text-center',
      tooltip: 'Rank by SCS score',
    },
    {
      id: 'races',
      label: 'Races',
      field: 'races_count',
      format: (value, row) => row.races_count || row.num_races || 0,
      className: 'text-center',
      tooltip: 'Number of qualifying races',
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
      tooltip: 'Most recent race date',
    });
  }

  return (
    <>
      <RankingsTable
        type="athletes"
        data={athletes}
        columns={columns}
        isHistorical={isHistorical}
        loading={loading}
      />

      {/* SCS Component Breakdown Modal */}
      {showSCSModal && selectedAthlete && (
        <SCSModal
          athlete={selectedAthlete}
          onClose={() => {
            setShowSCSModal(false);
            setSelectedAthlete(null);
          }}
        />
      )}
    </>
  );
}
