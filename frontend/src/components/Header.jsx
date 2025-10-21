import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

/**
 * USTFCCCA Header Component
 *
 * Provides consistent branding across XCRI application,
 * matching iz-apps-clean styling patterns.
 *
 * Session 009C: Enhanced with better logo, sticky positioning
 */
export default function Header() {
  return (
    <header className="ustfccca-header">
      <div className="header-container">
        <div className="header-content">
          <Link to="https://www.ustfccca.org" className="logo-section">
            {/* Logo placeholder - can be replaced with actual USTFCCCA logo */}
            <div className="logo-placeholder">
              <span className="logo-text">USTFCCCA</span>
            </div>
          </Link>
          <div className="title-section">
            <h1 className="site-title">
              XCRI: Cross Country Ratings Index
            </h1>
            <p className="site-tagline">
              Objective rankings system for NCAA, NAIA, and NJCAA collegiate cross country provided by the USTFCCCA. Performance data provided by presenting sponsor AthleticNET.
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
