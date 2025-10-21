import React, { useState } from 'react';

/**
 * Pagination Component
 * Previous/Next/First/Last controls with page info and jump-to-page
 * Session 003: Added First/Last buttons and page jump functionality (Issue #3)
 */
export default function Pagination({ total, limit, offset, onPageChange }) {
  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;
  const [jumpPage, setJumpPage] = useState('');

  const hasPrevious = offset > 0;
  const hasNext = offset + limit < total;

  const handleFirst = () => {
    onPageChange(0);
  };

  const handlePrevious = () => {
    if (hasPrevious) {
      onPageChange(Math.max(0, offset - limit));
    }
  };

  const handleNext = () => {
    if (hasNext) {
      onPageChange(offset + limit);
    }
  };

  const handleLast = () => {
    const lastPageOffset = (totalPages - 1) * limit;
    onPageChange(lastPageOffset);
  };

  const handleJumpToPage = (e) => {
    e.preventDefault();
    const pageNum = parseInt(jumpPage);
    if (pageNum >= 1 && pageNum <= totalPages) {
      const newOffset = (pageNum - 1) * limit;
      onPageChange(newOffset);
      setJumpPage(''); // Clear input after jump
    }
  };

  const handleJumpInputChange = (e) => {
    const value = e.target.value;
    // Only allow numeric input
    if (value === '' || /^\d+$/.test(value)) {
      setJumpPage(value);
    }
  };

  // Don't show pagination if there's no data
  if (total === 0) {
    return null;
  }

  return (
    <div className="pagination">
      {/* First Button */}
      <button
        onClick={handleFirst}
        disabled={!hasPrevious}
        className="pagination-button"
        title="Go to first page"
      >
        ⏮ First
      </button>

      {/* Previous Button */}
      <button
        onClick={handlePrevious}
        disabled={!hasPrevious}
        className="pagination-button"
        title="Go to previous page"
      >
        ← Previous
      </button>

      {/* Page Info */}
      <span className="pagination-info">
        Page {currentPage} of {totalPages} ({total.toLocaleString()} total)
      </span>

      {/* Next Button */}
      <button
        onClick={handleNext}
        disabled={!hasNext}
        className="pagination-button"
        title="Go to next page"
      >
        Next →
      </button>

      {/* Last Button */}
      <button
        onClick={handleLast}
        disabled={!hasNext}
        className="pagination-button"
        title="Go to last page"
      >
        Last ⏭
      </button>

      {/* Jump to Page (only show if more than 5 pages) */}
      {totalPages > 5 && (
        <form onSubmit={handleJumpToPage} className="pagination-jump">
          <label htmlFor="jump-to-page" className="pagination-jump-label">
            Jump to:
          </label>
          <input
            id="jump-to-page"
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            value={jumpPage}
            onChange={handleJumpInputChange}
            placeholder={`1-${totalPages}`}
            className="pagination-jump-input"
            title="Enter page number"
          />
          <button
            type="submit"
            className="pagination-jump-button"
            disabled={!jumpPage || parseInt(jumpPage) < 1 || parseInt(jumpPage) > totalPages}
            title="Go to page"
          >
            Go
          </button>
        </form>
      )}
    </div>
  );
}
