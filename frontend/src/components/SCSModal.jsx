import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import './SCSModal.css';

/**
 * SCS Modal Component
 * Shows detailed breakdown of Season Composite Score (SCS) for an athlete
 * Fetches SAGA, SEWR, OSMA component scores from API
 * Session 009D: Fixed to use API client instead of hardcoded URL
 */
export default function SCSModal({ athlete, onClose }) {
  const [components, setComponents] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!athlete) return;

    // Fetch SCS component data from API using API client
    const fetchComponents = async () => {
      try {
        setLoading(true);
        setError(null);

        // Use athlete's season_year if available, otherwise derive from current year
        // Session 003 Issue #17: Fixed hardcoded 2024 to use current season (2025)
        const seasonYear = athlete.season_year || 2025;

        const response = await api.get(
          `/scs/athletes/${athlete.anet_athlete_hnd}/components`,
          {
            params: {
              season_year: seasonYear,
              division: athlete.division_code,
              gender: athlete.gender_code
            }
          }
        );

        setComponents(response.data);
      } catch (err) {
        console.error('Error fetching SCS components:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchComponents();
  }, [athlete]);

  if (!athlete) return null;

  // Calculate rank difference
  const rankDiff = athlete.scs_rank - athlete.athlete_rank;
  const isXCRIBetter = rankDiff > 0; // XCRI rank is lower number (better)

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <h2>Season Composite Score (SCS) Breakdown</h2>
          <button className="close-btn" onClick={onClose} aria-label="Close modal">
            ×
          </button>
        </div>

        {/* Body */}
        <div className="modal-body">
          {/* Athlete Info */}
          <div className="athlete-info">
            <h3>
              {athlete.athlete_name_first} {athlete.athlete_name_last}
            </h3>
            <p className="school">{athlete.team_name}</p>
            <p className="races-info">
              {athlete.races_count} {athlete.races_count === 1 ? 'race' : 'races'} completed
            </p>
          </div>

          {/* SCS Scaling Note - Session 009C: Corrected */}
          <div className="scs-scaling-note">
            <span className="note-icon">💡</span>
            <span className="note-text">
              SCS scores are normalized with 1000 representing the median athlete.
              Each 100 points represents one standard deviation. For example, a score of 1100
              is one standard deviation above the median, while 900 is one standard deviation below.
            </span>
          </div>

          {/* SCS Components Table */}
          <div className="scs-components">
            <h4>SCS Component Scores</h4>
            <p className="component-note">
              SCS (Season Component Score) is a season-long measure of statistical strength.
              It combines multiple factors including gap scores, strength of schedule, and performance consistency.
              SCS is normalized against all athletes in the division, with scores comparing each athlete to the field median.
            </p>

            {loading ? (
              <div className="loading-message">Loading component data...</div>
            ) : error ? (
              <div className="error-message">
                <p>Unable to load component scores: {error}</p>
                <p className="fallback-note">Showing basic information only.</p>
              </div>
            ) : components ? (
              <table className="component-table">
                <thead>
                  <tr>
                    <th>Component</th>
                    <th>Description</th>
                    <th>Score</th>
                    <th>Rank</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="component-name">
                      <strong>SAGA</strong>
                    </td>
                    <td className="component-desc">
                      Season Adjusted Gap Average - Represents where, on average, an athlete finishes each race in relation to the rest of the field
                    </td>
                    <td className="component-value">
                      {components.saga_score !== null ? Number(components.saga_score).toFixed(2) : 'N/A'}
                    </td>
                    <td className="component-rank">
                      #{components.saga_rank || 'N/A'}
                    </td>
                  </tr>
                  <tr>
                    <td className="component-name">
                      <strong>SEWR</strong>
                    </td>
                    <td className="component-desc">
                      Season Equal-Weight Rating - Strength of schedule indicator based on the quality of opponents faced throughout the season
                    </td>
                    <td className="component-value">
                      {components.sewr_score !== null ? Number(components.sewr_score).toFixed(2) : 'N/A'}
                    </td>
                    <td className="component-rank">
                      #{components.sewr_rank || 'N/A'}
                    </td>
                  </tr>
                  <tr>
                    <td className="component-name">
                      <strong>OSMA</strong>
                    </td>
                    <td className="component-desc">
                      Opponent SEWR Moving Average - Rolling average of opponent strength ratings, giving recent performances more weight
                    </td>
                    <td className="component-value">
                      {components.osma_score !== null ? Number(components.osma_score).toFixed(2) : 'N/A'}
                    </td>
                    <td className="component-rank">
                      #{components.osma_rank || 'N/A'}
                    </td>
                  </tr>
                  <tr className="composite-row">
                    <td className="component-name">
                      <strong>SCS (Composite)</strong>
                    </td>
                    <td className="component-desc">
                      Final score: (0.6 × SEWR) + (0.4 × OSMA)
                    </td>
                    <td className="component-value">
                      <strong>{athlete.scs_score?.toFixed(2) || 'N/A'}</strong>
                    </td>
                    <td className="component-rank">
                      <strong>#{athlete.scs_rank || 'N/A'}</strong>
                    </td>
                  </tr>
                </tbody>
              </table>
            ) : (
              <div className="no-data-message">No component data available</div>
            )}
          </div>

          {/* Explanation */}
          <div className="explanation">
            <h4>Understanding the Components</h4>
            <ul className="component-explainer">
              <li>
                <strong>SAGA</strong>: Higher is better - measures gap-closing consistency (higher score = smaller gaps to winners)
              </li>
              <li>
                <strong>SEWR</strong>: Higher is better - evaluates individual performance quality across the season
              </li>
              <li>
                <strong>OSMA</strong>: Higher is better - reflects strength of competition faced
              </li>
              <li>
                <strong>SCS</strong>: Composite score balancing performance (SEWR) and competition (OSMA). Higher is better.
              </li>
            </ul>

            <h4 style={{ marginTop: '1rem' }}>XCRI vs SCS: Different Perspectives</h4>
            <p>
              XCRI is tuned to balance head-to-head competition and season statistical strength,
              making it effective throughout the season. SCS is a season-long measure of statistical
              strength that becomes particularly relevant once championship season commences.
              Both provide valuable insights into athlete performance.
            </p>
            {isXCRIBetter ? (
              <p style={{ marginTop: '0.5rem' }}>
                This athlete's <strong>XCRI rank is higher</strong>, indicating success in head-to-head
                competition against quality opponents.
              </p>
            ) : rankDiff < 0 ? (
              <p style={{ marginTop: '0.5rem' }}>
                This athlete's <strong>SCS rank is higher</strong>, indicating strong statistical
                performances across the season.
              </p>
            ) : (
              <p style={{ marginTop: '0.5rem' }}>
                <strong>Ranks are identical</strong>, which means competitive results and
                statistical performance align perfectly.
              </p>
            )}
          </div>
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
