import React from 'react';
import './Breadcrumb.css';

/**
 * Breadcrumb Navigation Component
 *
 * Shows navigation hierarchy for XCRI application
 * Session 009C: Created for improved page structure
 * Session 004: Added Athletic.net attribution (Issue #16)
 */
export default function Breadcrumb() {
  return (
    <nav className="breadcrumb" aria-label="Breadcrumb navigation">
      <div className="breadcrumb-container">
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

        {/* Athletic.net Attribution (Issue #16) */}
        <div className="breadcrumb-attribution">
          <a
            href="https://www.athletic.net"
            target="_blank"
            rel="noopener noreferrer"
            className="anet-attribution-link"
            title="Athletic.net - High School Track and Field and Cross Country"
          >
            <span className="anet-attribution-text">Data provided by</span>
            <img
              src="https://www.ustfccca.org/images/athleticnet.svg"
              alt="Athletic.net"
              className="anet-logo"
            />
          </a>
        </div>
      </div>
    </nav>
  );
}
