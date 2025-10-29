import React, { useState, useEffect } from 'react';
import { teamKnockoutAPI } from '../services/api';
import './MatchupHistoryModal.css';

/**
 * Matchup History Modal Component
 * Shows complete head-to-head matchup history for a team in Team Knockout rankings
 *
 * Features:
 * - Win-loss statistics summary
 * - Complete matchup table (date, meet, opponent, result)
 * - Color-coded wins (green) and losses (red)
 * - Pagination for teams with many matchups
 * - Clickable meet names (open MeetMatchupsModal)
 * - Clickable opponent names (open HeadToHeadModal)
 *
 * Session 018: Phase 2 - Matchup history display
 */
export default function MatchupHistoryModal({
  team,
  onClose,
  onMeetClick = null,
  onOpponentClick = null
}) {
  const [matchupData, setMatchupData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [offset, setOffset] = useState(0);
  const limit = 50; // Show 50 matchups per page

  useEffect(() => {
    if (!team) return;

    // Fetch matchup history from API
    const fetchMatchups = async () => {
      try {
        setLoading(true);
        setError(null);

        const seasonYear = team.season_year || 2025;

        const response = await teamKnockoutAPI.matchups(
          team.team_id || team.anet_team_hnd,
          {
            season_year: seasonYear,
            limit,
            offset
          }
        );

        setMatchupData(response.data);
      } catch (err) {
        console.error('Error fetching matchup history:', err);
        setError(err.response?.data?.message || err.message || 'Failed to fetch matchup history');
      } finally {
        setLoading(false);
      }
    };

    fetchMatchups();
  }, [team, offset, limit]);

  if (!team) return null;

  // Format date as MM/DD/YYYY
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const year = date.getFullYear();
    return `${month}/${day}/${year}`;
  };

  // Format number as ordinal (1st, 2nd, 3rd, 4th, etc.)
  const formatOrdinal = (num) => {
    if (!num) return 'N/A';
    const suffixes = ['th', 'st', 'nd', 'rd'];
    const value = num % 100;
    return num + (suffixes[(value - 20) % 10] || suffixes[value] || suffixes[0]);
  };

  // Determine if team won the matchup
  const isWin = (matchup, teamName) => {
    return matchup.winner_team_name === teamName;
  };

  // Get opponent name (the other team in the matchup)
  const getOpponentName = (matchup, teamName) => {
    if (matchup.team_a_name === teamName) {
      return matchup.team_b_name;
    }
    return matchup.team_a_name;
  };

  // Get opponent rank
  const getOpponentRank = (matchup, teamName) => {
    if (matchup.team_a_name === teamName) {
      return matchup.team_b_rank;
    }
    return matchup.team_a_rank;
  };

  // Get score display (team score vs opponent score)
  const getScoreDisplay = (matchup, teamName) => {
    const teamScore = matchup.team_a_name === teamName ? matchup.team_a_score : matchup.team_b_score;
    const oppScore = matchup.team_a_name === teamName ? matchup.team_b_score : matchup.team_a_score;
    return `${teamScore} - ${oppScore}`;
  };

  // Handle pagination
  const handlePreviousPage = () => {
    setOffset(Math.max(0, offset - limit));
  };

  const handleNextPage = () => {
    if (matchupData && offset + limit < matchupData.total) {
      setOffset(offset + limit);
    }
  };

  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = matchupData ? Math.ceil(matchupData.total / limit) : 1;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content matchup-history-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <h2>Season Varsity Matchups - {team.team_name}</h2>
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
              <p>Loading matchup history...</p>
            </div>
          )}

          {/* Error State */}
          {error && !loading && (
            <div className="error-message">
              <p>Unable to load matchup history: {error}</p>
              <button onClick={() => setOffset(0)} className="retry-button">
                Try Again
              </button>
            </div>
          )}

          {/* Data Display */}
          {!loading && !error && matchupData && (
            <>
              {/* Win-Loss Summary */}
              <div className="matchup-summary">
                <div className="summary-card">
                  <div className="summary-label">Season Record</div>
                  <div className="summary-value record-value">
                    <span className="wins">{matchupData.stats.wins}W</span>
                    {' - '}
                    <span className="losses">{matchupData.stats.losses}L</span>
                  </div>
                </div>
                <div className="summary-card">
                  <div className="summary-label">Win Percentage</div>
                  <div className="summary-value">
                    {matchupData.stats.win_pct?.toFixed(1) || '0.0'}%
                  </div>
                </div>
                <div className="summary-card">
                  <div className="summary-label">Total Matchups</div>
                  <div className="summary-value">
                    {matchupData.stats.total_matchups}
                  </div>
                </div>
              </div>

              {/* Matchups Table */}
              {matchupData.matchups && matchupData.matchups.length > 0 ? (
                <div className="matchups-table-container">
                  <table className="matchups-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Meet</th>
                        <th>Opponent</th>
                        <th>Place</th>
                        <th>Score</th>
                        <th>Result</th>
                      </tr>
                    </thead>
                    <tbody>
                      {matchupData.matchups.map((matchup) => {
                        const won = isWin(matchup, team.team_name);
                        const opponentName = getOpponentName(matchup, team.team_name);
                        const opponentRank = getOpponentRank(matchup, team.team_name);
                        const score = getScoreDisplay(matchup, team.team_name);

                        return (
                          <tr
                            key={matchup.matchup_id}
                            className={won ? 'win-row' : 'loss-row'}
                          >
                            <td className="date-cell nowrap">
                              {formatDate(matchup.race_date)}
                            </td>
                            <td className="meet-cell">
                              <a
                                href={`https://www.athletic.net/CrossCountry/meet/${matchup.race_hnd}/results/${matchup.race_hnd}?tab=team-scores`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="meet-link"
                                title="View meet results on Athletic.net"
                              >
                                {matchup.meet_name}
                              </a>
                            </td>
                            <td className="opponent-cell">
                              {onOpponentClick ? (
                                <button
                                  className="opponent-link"
                                  onClick={() => onOpponentClick(team, {
                                    team_id: matchup.team_a_name === team.team_name ? matchup.team_b_id : matchup.team_a_id,
                                    team_name: opponentName
                                  })}
                                  title="View head-to-head comparison"
                                >
                                  {opponentName}
                                </button>
                              ) : (
                                opponentName
                              )}
                            </td>
                            <td className="rank-cell text-center">
                              {formatOrdinal(opponentRank)}
                            </td>
                            <td className="score-cell text-center">
                              {score}
                            </td>
                            <td className={`result-cell text-center ${won ? 'win' : 'loss'}`}>
                              <span className="result-badge">
                                {won ? 'W' : 'L'}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="no-matchups-message">
                  <p>No matchups found for this team.</p>
                </div>
              )}

              {/* Pagination */}
              {matchupData.total > limit && (
                <div className="pagination-controls">
                  <button
                    onClick={handlePreviousPage}
                    disabled={offset === 0}
                    className="pagination-btn"
                  >
                    ← Previous
                  </button>
                  <span className="pagination-info">
                    Page {currentPage} of {totalPages} ({matchupData.total} total matchups)
                  </span>
                  <button
                    onClick={handleNextPage}
                    disabled={offset + limit >= matchupData.total}
                    className="pagination-btn"
                  >
                    Next →
                  </button>
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
