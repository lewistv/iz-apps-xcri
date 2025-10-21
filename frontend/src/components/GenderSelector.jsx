import React from 'react';
import { GENDERS } from '../services/api';

/**
 * Gender Selector Component
 * Toggle buttons for selecting Men or Women
 */
export default function GenderSelector({ value, onChange }) {
  return (
    <div className="gender-selector">
      <label>Gender:</label>
      <div className="button-group">
        {GENDERS.map((gender) => (
          <button
            key={gender.code}
            className={`selector-button ${value === gender.code ? 'active' : ''}`}
            onClick={() => onChange(gender.code)}
          >
            {gender.name}
          </button>
        ))}
      </div>
    </div>
  );
}
