import React from 'react';

/**
 * Region Selector Component
 * Dropdown for filtering by geographic region
 *
 * Regions vary by division (16 total across all divisions)
 * Populated dynamically from available data
 */
export default function RegionSelector({ value, onChange, regions = [], disabled = false }) {
  return (
    <div className="region-selector">
      <label htmlFor="region-select">Region:</label>
      <select
        id="region-select"
        value={value || ''}
        onChange={(e) => onChange(e.target.value || null)}
        className="selector-input"
        disabled={disabled}
      >
        <option value="">All Regions</option>
        {regions.map((region) => (
          <option key={region} value={region}>
            {region}
          </option>
        ))}
      </select>
    </div>
  );
}
