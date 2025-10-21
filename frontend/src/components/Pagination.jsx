import React from 'react';

/**
 * Pagination Component
 * Previous/Next controls with page info
 */
export default function Pagination({ total, limit, offset, onPageChange }) {
  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  const hasPrevious = offset > 0;
  const hasNext = offset + limit < total;

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

  // Don't show pagination if there's no data
  if (total === 0) {
    return null;
  }

  return (
    <div className="pagination">
      <button
        onClick={handlePrevious}
        disabled={!hasPrevious}
        className="pagination-button"
      >
        ← Previous
      </button>

      <span className="pagination-info">
        Page {currentPage} of {totalPages} ({total.toLocaleString()} total)
      </span>

      <button
        onClick={handleNext}
        disabled={!hasNext}
        className="pagination-button"
      >
        Next →
      </button>
    </div>
  );
}
