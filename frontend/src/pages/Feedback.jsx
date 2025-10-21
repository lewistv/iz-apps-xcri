import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Feedback.css';

/**
 * Feedback Form Component
 * Allows users to submit bugs, feedback, or questions
 * Creates GitHub issues via backend API
 */
export default function Feedback() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    feedback_type: 'feedback',
    message: ''
  });

  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);
  const [issueUrl, setIssueUrl] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/iz/xcri/api';
      const response = await axios.post(`${API_BASE_URL}/feedback/`, formData);

      setSubmitted(true);
      setIssueUrl(response.data.issue_url);

      // Reset form
      setFormData({
        name: '',
        email: '',
        feedback_type: 'feedback',
        message: ''
      });

    } catch (err) {
      if (err.response?.status === 429) {
        setError('Rate limit exceeded. Please try again later (max 3 per hour, 10 per day).');
      } else {
        setError(err.response?.data?.detail || 'Failed to submit feedback. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  // Update page title
  React.useEffect(() => {
    document.title = 'USTFCCCA ::: XCRI - Submit Feedback';
  }, []);

  if (submitted) {
    return (
      <div className="feedback-page">
        <div className="feedback-container">
          <nav className="breadcrumb">
            <Link to="/">Home</Link> / <span>Feedback</span>
          </nav>

          <div className="feedback-success">
            <h2>✓ Thank You!</h2>
            <p>Your feedback has been received and our team will review it soon.</p>
            <p>We appreciate you taking the time to help us improve XCRI!</p>

            <div className="success-actions">
              <button onClick={() => setSubmitted(false)} className="btn-primary">
                Submit Another
              </button>
              <Link to="/" className="btn-secondary">
                Back to Rankings
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="feedback-page">
      <div className="feedback-container">
        <nav className="breadcrumb">
          <Link to="/">Home</Link> / <span>Feedback</span>
        </nav>

        <h1>Submit Feedback</h1>

        <div className="feedback-intro">
          <p>
            We value your feedback! Use this form to report bugs, suggest improvements,
            or ask questions about the XCRI rankings system.
          </p>
          <p>
            Your submission will be tracked as a GitHub issue, and we'll review it as soon as possible.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="feedback-form">
          {/* Optional Fields */}
          <div className="form-section">
            <h3>Your Information (Optional)</h3>

            <div className="form-group">
              <label htmlFor="name">Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                maxLength={100}
                placeholder="Your name (optional)"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                maxLength={100}
                placeholder="your.email@example.com (optional)"
              />
              <small className="form-help">
                We'll only use this if we need to follow up on your submission.
              </small>
            </div>
          </div>

          {/* Feedback Type */}
          <div className="form-section">
            <h3>Feedback Type</h3>

            <div className="form-group">
              <label htmlFor="feedback_type">What type of feedback is this?</label>
              <select
                id="feedback_type"
                name="feedback_type"
                value={formData.feedback_type}
                onChange={handleChange}
                required
              >
                <option value="bug">Bug Report - Something isn't working</option>
                <option value="feedback">Feedback - Suggestion or improvement</option>
                <option value="question">Question - I need help understanding something</option>
              </select>
            </div>
          </div>

          {/* Message */}
          <div className="form-section">
            <h3>Your Message</h3>

            <div className="form-group">
              <label htmlFor="message">
                Please describe your {formData.feedback_type === 'bug' ? 'bug' : formData.feedback_type} in detail
                <span className="required">*</span>
              </label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                required
                minLength={10}
                maxLength={2000}
                rows={8}
                placeholder={
                  formData.feedback_type === 'bug'
                    ? "Please describe what happened, what you expected to happen, and steps to reproduce the issue..."
                    : formData.feedback_type === 'question'
                    ? "What would you like to know about XCRI rankings?"
                    : "What improvements would you like to see?"
                }
              />
              <small className="form-help">
                {formData.message.length} / 2000 characters (minimum 10)
              </small>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Submit Button */}
          <div className="form-actions">
            <button type="submit" disabled={submitting || formData.message.length < 10} className="btn-submit">
              {submitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
            <Link to="/" className="btn-cancel">
              Cancel
            </Link>
          </div>

          {/* Rate Limit Notice */}
          <div className="rate-limit-notice">
            <small>
              <strong>Rate limit:</strong> 3 submissions per hour, 10 per day per IP address.
            </small>
          </div>
        </form>

        <footer className="feedback-footer">
          <p>
            <Link to="/">Back to Rankings</Link> |{' '}
            <Link to="/faq">FAQ</Link> |{' '}
            <Link to="/how-it-works">How It Works</Link>
          </p>
        </footer>
      </div>
    </div>
  );
}
