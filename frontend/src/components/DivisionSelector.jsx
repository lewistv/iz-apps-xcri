import React from 'react';
import { DIVISIONS } from '../services/api';

/**
 * Division Selector Component
 * Dropdown for selecting NCAA division (D1, D2, D3)
 */
export default function DivisionSelector({ value, onChange }) {
  return (
    <div className="division-selector">
      <label htmlFor="division-select">Division:</label>
      <select
        id="division-select"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="selector-input"
      >
        {DIVISIONS.map((div) => (
          <option key={div.code} value={div.code}>
            {div.name}
          </option>
        ))}
      </select>
    </div>
  );
}
