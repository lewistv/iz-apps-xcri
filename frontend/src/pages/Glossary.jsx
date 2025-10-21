import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import './DocumentationPage.css';
import glossaryContent from '../content/glossary.md?raw';

/**
 * Glossary Page Component
 * Displays technical terms and definitions for XCRI system
 */
export default function Glossary() {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Set page title
    document.title = 'USTFCCCA ::: XCRI - Glossary';

    // Load Glossary markdown content (imported directly)
    setContent(glossaryContent);
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="documentation-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading glossary...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="documentation-page">
      <div className="documentation-container">
        <nav className="breadcrumb">
          <Link to="/">Home</Link> / <span>Glossary</span>
        </nav>

        <div className="markdown-content">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>

        <footer className="documentation-footer">
          <p>
            <Link to="/faq">FAQ</Link> |{' '}
            <Link to="/how-it-works">How It Works</Link> |{' '}
            <Link to="/">Back to Rankings</Link>
          </p>
        </footer>
      </div>
    </div>
  );
}
