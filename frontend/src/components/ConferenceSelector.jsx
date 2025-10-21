import React from 'react';

/**
 * Conference Selector Component
 * Dropdown for filtering by athletic conference
 *
 * Conferences vary by division (139 total across all divisions)
 * Populated dynamically from available data
 */
export default function ConferenceSelector({ value, onChange, conferences = [], disabled = false }) {
  return (
    <div className="conference-selector">
      <label htmlFor="conference-select">Conference:</label>
      <select
        id="conference-select"
        value={value || ''}
        onChange={(e) => onChange(e.target.value || null)}
        className="selector-input"
        disabled={disabled}
      >
        <option value="">All Conferences</option>
        {conferences.map((conference) => (
          <option key={conference} value={conference}>
            {conference}
          </option>
        ))}
      </select>
    </div>
  );
}
