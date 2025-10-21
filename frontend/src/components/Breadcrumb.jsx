import React from 'react';
import './Breadcrumb.css';

/**
 * Breadcrumb Navigation Component
 *
 * Shows navigation hierarchy for XCRI application
 * Session 009C: Created for improved page structure
 */
export default function Breadcrumb() {
  return (
    <nav className="breadcrumb" aria-label="Breadcrumb navigation">
      <ol className="breadcrumb-list">
        <li className="breadcrumb-item">
          <span className="breadcrumb-link">Home</span>
        </li>
        <li className="breadcrumb-separator" aria-hidden="true">›</li>
        <li className="breadcrumb-item">
          <span className="breadcrumb-link">Rankings</span>
        </li>
        <li className="breadcrumb-separator" aria-hidden="true">›</li>
        <li className="breadcrumb-item breadcrumb-current" aria-current="page">
          <span className="breadcrumb-text">XCRI</span>
        </li>
      </ol>
    </nav>
  );
}
