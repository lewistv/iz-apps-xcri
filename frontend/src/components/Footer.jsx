import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

/**
 * USTFCCCA Footer Component
 *
 * Provides consistent footer across XCRI application,
 * matching iz-apps-clean styling patterns.
 *
 * Session 009C: Updated with working links to documentation pages
 */
export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="ustfccca-footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-copyright">
            <p>&copy; {currentYear} U.S. Track &amp; Field and Cross Country Coaches Association</p>
          </div>
          <div className="footer-links">
            <Link to="/how-it-works" className="footer-link">How It Works</Link>
            <span className="footer-separator">|</span>
            <Link to="/glossary" className="footer-link">Glossary</Link>
            <span className="footer-separator">|</span>
            <Link to="/faq" className="footer-link">FAQ</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
