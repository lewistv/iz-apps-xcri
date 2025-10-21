import React, { useState, useEffect } from 'react';
import { snapshotAPI } from '../services/api';
import './SnapshotSelector.css';

/**
 * Snapshot Selector Component
 *
 * Provides UI for switching between current rankings and historical snapshots.
 * Fetches available snapshots from API and displays them in a dropdown.
 *
 * NOTE: Both current rankings and historical snapshots use MySQL database
 *       with full SCS component score support (Backend Session 013)
 */
export default function SnapshotSelector({
  isHistorical,
  selectedDate,
  onViewChange,
  onDateChange,
}) {
  const [snapshots, setSnapshots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedYear, setSelectedYear] = useState(2025); // Default to latest year

  // Fetch available snapshots on component mount
  useEffect(() => {
    fetchSnapshots();
  }, []);

  /**
   * Fetch list of available snapshots from API
   */
  const fetchSnapshots = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await snapshotAPI.list();
      setSnapshots(response.data.snapshots || []);
    } catch (err) {
      console.error('Error fetching snapshots:', err);
      setError('Failed to load snapshots');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle view mode change (current vs historical)
   */
  const handleViewChange = (historical) => {
    onViewChange(historical);
    // If switching to historical and no date selected, select the latest snapshot for selected year
    if (historical && !selectedDate) {
      const yearSnapshots = getSnapshotsForYear(selectedYear);
      if (yearSnapshots.length > 0) {
        onDateChange(yearSnapshots[0].date);
      }
    }
  };

  /**
   * Handle year change
   */
  const handleYearChange = (year) => {
    setSelectedYear(year);
    // Auto-select the latest snapshot for the new year
    const yearSnapshots = getSnapshotsForYear(year);
    if (yearSnapshots.length > 0) {
      onDateChange(yearSnapshots[0].date);
    }
  };

  /**
   * Get snapshots for a specific year
   */
  const getSnapshotsForYear = (year) => {
    return snapshots.filter((s) => s.season === year);
  };

  /**
   * Get available years from snapshots
   */
  const getAvailableYears = () => {
    const years = [...new Set(snapshots.map((s) => s.season))];
    return years.sort((a, b) => b - a); // Descending order (newest first)
  };

  // Filter snapshots for selected year
  const filteredSnapshots = getSnapshotsForYear(selectedYear);

  return (
    <div className="snapshot-selector">
      {/* View Toggle: Current vs Historical */}
      <div className="view-toggle">
        <label className={!isHistorical ? 'active' : ''}>
          <input
            type="radio"
            name="view-mode"
            value="current"
            checked={!isHistorical}
            onChange={() => handleViewChange(false)}
          />
          <span>Current LIVE Rankings</span>
        </label>
        <label className={isHistorical ? 'active' : ''}>
          <input
            type="radio"
            name="view-mode"
            value="historical"
            checked={isHistorical}
            onChange={() => handleViewChange(true)}
          />
          <span>Historical Snapshots</span>
        </label>
      </div>

      {/* Snapshot Date Selector (only visible in historical mode) */}
      {isHistorical && (
        <div className="snapshot-controls">
          {/* Year Selector */}
          <div className="year-selector">
            <label htmlFor="snapshot-year">Season:</label>
            <div className="year-buttons">
              {getAvailableYears().map((year) => (
                <button
                  key={year}
                  className={`year-button ${selectedYear === year ? 'active' : ''}`}
                  onClick={() => handleYearChange(year)}
                  disabled={loading}
                >
                  {year}
                </button>
              ))}
            </div>
          </div>

          {/* Date Selector */}
          <div className="date-selector">
            <label htmlFor="snapshot-date">
              Snapshot ({filteredSnapshots.length} available):
            </label>
            <select
              id="snapshot-date"
              value={selectedDate || ''}
              onChange={(e) => onDateChange(e.target.value)}
              disabled={loading || filteredSnapshots.length === 0}
              className="snapshot-dropdown"
            >
              <option value="">Select a date...</option>
              {filteredSnapshots.map((snapshot) => (
                <option key={snapshot.date} value={snapshot.date}>
                  {snapshot.display_name}
                  {snapshot.week && ` - Week ${snapshot.week}`}
                </option>
              ))}
            </select>
          </div>

          {/* Loading/Error States */}
          {loading && <span className="loading-text">Loading snapshots...</span>}
          {error && <span className="error-text">{error}</span>}
          {!loading && snapshots.length === 0 && (
            <span className="info-text">No snapshots available</span>
          )}
        </div>
      )}
    </div>
  );
}
