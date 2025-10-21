import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import './DocumentationPage.css';
import faqContent from '../content/faq.md?raw';

/**
 * FAQ Page Component
 * Displays comprehensive FAQ content about XCRI ranking algorithms
 */
export default function FAQ() {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Set page title
    document.title = 'USTFCCCA ::: XCRI - Frequently Asked Questions';

    // Load FAQ markdown content (imported directly)
    setContent(faqContent);
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="documentation-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading FAQ...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="documentation-page">
      <div className="documentation-container">
        <nav className="breadcrumb">
          <Link to="/">Home</Link> / <span>FAQ</span>
        </nav>

        <div className="markdown-content">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>

        <footer className="documentation-footer">
          <p>
            <Link to="/how-it-works">How It Works</Link> |{' '}
            <Link to="/glossary">Glossary</Link> |{' '}
            <Link to="/">Back to Rankings</Link>
          </p>
        </footer>
      </div>
    </div>
  );
}
