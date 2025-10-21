import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import './DocumentationPage.css';
import howItWorksContent from '../content/how-it-works.md?raw';

/**
 * How It Works Page Component
 * Displays beginner-friendly guide to XCRI algorithms
 */
export default function HowItWorks() {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load How It Works markdown content (imported directly)
    setContent(howItWorksContent);
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="documentation-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading documentation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="documentation-page">
      <div className="documentation-container">
        <nav className="breadcrumb">
          <Link to="/">Home</Link> / <span>How It Works</span>
        </nav>

        <div className="markdown-content">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>

        <footer className="documentation-footer">
          <p>
            <Link to="/faq">FAQ</Link> |{' '}
            <Link to="/glossary">Glossary</Link> |{' '}
            <Link to="/">Back to Rankings</Link>
          </p>
        </footer>
      </div>
    </div>
  );
}
