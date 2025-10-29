import React, { useState, useEffect } from 'react';
import { teamKnockoutAPI } from '../services/api';
import './HeadToHeadModal.css';

/**
 * Head-to-Head Modal Component
 * Shows direct comparison between two teams with complete matchup history
 *
 * Features:
 * - Side-by-side win-loss comparison
 * - Complete matchup history table
 * - Latest matchup highlighting
 * - Link to common opponents analysis
 *
 * Session 018: Phase 2.2 - H2H comparison display
 */
export default function HeadToHeadModal({
  teamA,
  teamB,
  onClose,
  onCommonOpponentsClick = null
}) {
  const [h2hData, setH2hData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!teamA || !teamB) return;

    // Fetch head-to-head data from API
    const fetchH2H = async () => {
      try {
        setLoading(true);
        setError(null);

        const seasonYear = teamA.season_year || 2025;

        const response = await teamKnockoutAPI.headToHead(
          teamA.team_id || teamA.anet_team_hnd,
          teamB.team_id || teamB.anet_team_hnd,
          { season_year: seasonYear }
        );

        setH2hData(response.data);
      } catch (err) {
        console.error('Error fetching H2H data:', err);
        setError(err.response?.data?.message || err.message || 'Failed to fetch head-to-head data');
      } finally {
        setLoading(false);
      }
    };

    fetchH2H();
  }, [teamA, teamB]);

  if (!teamA || !teamB) return null;

  // Format date as MM/DD/YYYY
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const year = date.getFullYear();
    return `${month}/${day}/${year}`;
  };

  // Get win percentage for a team
  const getWinPct = (wins, totalMatchups) => {
    if (totalMatchups === 0) return 0;
    return ((wins / totalMatchups) * 100).toFixed(1);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content h2h-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <h2>Head-to-Head Comparison</h2>
          <button className="close-btn" onClick={onClose} aria-label="Close modal">
            ×
          </button>
        </div>

        {/* Body */}
        <div className="modal-body">
          {/* Loading State */}
          {loading && (
            <div className="loading-message">
              <div className="loading-spinner"></div>
              <p>Loading head-to-head data...</p>
            </div>
          )}

          {/* Error State */}
          {error && !loading && (
            <div className="error-message">
              <p>Unable to load head-to-head data: {error}</p>
              <button onClick={() => window.location.reload()} className="retry-button">
                Try Again
              </button>
            </div>
          )}

          {/* Data Display */}
          {!loading && !error && h2hData && (
            <>
              {/* Side-by-side comparison */}
              <div className="h2h-comparison">
                <div className="team-card team-a">
                  <h3 className="team-name">{h2hData.team_a_name || teamA.team_name}</h3>
                  <div className="team-stats">
                    <div className="stat-value">{h2hData.team_a_wins}</div>
                    <div className="stat-label">
                      {h2hData.team_a_wins === 1 ? 'Win' : 'Wins'}
                    </div>
                    {h2hData.total_matchups > 0 && (
                      <div className="stat-pct">
                        ({getWinPct(h2hData.team_a_wins, h2hData.total_matchups)}%)
                      </div>
                    )}
                  </div>
                </div>

                <div className="vs-divider">
                  <span className="vs-text">VS</span>
                  <div className="vs-line"></div>
                </div>

                <div className="team-card team-b">
                  <h3 className="team-name">{h2hData.team_b_name || teamB.team_name}</h3>
                  <div className="team-stats">
                    <div className="stat-value">{h2hData.team_b_wins}</div>
                    <div className="stat-label">
                      {h2hData.team_b_wins === 1 ? 'Win' : 'Wins'}
                    </div>
                    {h2hData.total_matchups > 0 && (
                      <div className="stat-pct">
                        ({getWinPct(h2hData.team_b_wins, h2hData.total_matchups)}%)
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Summary Info */}
              <div className="h2h-summary">
                <div className="summary-item">
                  <span className="summary-label">Total Matchups:</span>
                  <span className="summary-value">{h2hData.total_matchups}</span>
                </div>
                {h2hData.latest_matchup_date && (
                  <div className="summary-item">
                    <span className="summary-label">Most Recent:</span>
                    <span className="summary-value">
                      {formatDate(h2hData.latest_matchup_date)}
                      {h2hData.latest_winner_name && (
                        <span className="winner-badge">
                          {' '}({h2hData.latest_winner_name} won)
                        </span>
                      )}
                    </span>
                  </div>
                )}
              </div>

              {/* Matchups History */}
              {h2hData.matchups && h2hData.matchups.length > 0 ? (
                <div className="h2h-history">
                  <h4>Matchup History</h4>
                  <div className="matchups-table-container">
                    <table className="matchups-table">
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Meet</th>
                          <th>{h2hData.team_a_name}</th>
                          <th>{h2hData.team_b_name}</th>
                          <th>Winner</th>
                        </tr>
                      </thead>
                      <tbody>
                        {h2hData.matchups.map((matchup, index) => {
                          const isLatest = index === 0; // Assuming API returns in descending order
                          return (
                            <tr
                              key={matchup.matchup_id}
                              className={isLatest ? 'latest-matchup' : ''}
                            >
                              <td className="nowrap">
                                {formatDate(matchup.race_date)}
                                {isLatest && <span className="latest-badge">Latest</span>}
                              </td>
                              <td>{matchup.meet_name}</td>
                              <td className="text-center score-cell">
                                {matchup.team_a_score}
                              </td>
                              <td className="text-center score-cell">
                                {matchup.team_b_score}
                              </td>
                              <td className="text-center winner-cell">
                                <span className={`winner-badge ${
                                  matchup.winner_team_name === h2hData.team_a_name
                                    ? 'team-a-win'
                                    : 'team-b-win'
                                }`}>
                                  {matchup.winner_team_name === h2hData.team_a_name
                                    ? h2hData.team_a_name
                                    : h2hData.team_b_name}
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="no-matchups-message">
                  <p>These teams have not faced each other this season.</p>
                </div>
              )}

              {/* Common Opponents Link */}
              {onCommonOpponentsClick && h2hData.total_matchups >= 0 && (
                <div className="common-opponents-section">
                  <button
                    className="common-opponents-btn"
                    onClick={() => onCommonOpponentsClick(teamA, teamB)}
                  >
                    View Common Opponents Analysis →
                  </button>
                  <p className="common-opponents-note">
                    Compare how these teams performed against shared opponents
                  </p>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button className="btn-close" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
