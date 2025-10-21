import React, { useState, useEffect } from 'react';

/**
 * Search Bar Component with Debouncing
 * Session 009C: Added debouncing and 3-letter minimum
 *
 * Search input for filtering athletes/teams by name or school
 * - 300ms debounce delay
 * - 3-letter minimum before search triggers
 * - Loading indicator during search operations
 */
export default function SearchBar({
  value = '',
  onChange,
  loading = false,
  placeholder = 'Search athletes or schools...'
}) {
  const [inputValue, setInputValue] = useState(value);
  const [debouncedValue, setDebouncedValue] = useState(value);

  // Sync with external value changes
  useEffect(() => {
    setInputValue(value);
    setDebouncedValue(value);
  }, [value]);

  // Debounce logic with 3-letter minimum (Session 009C)
  useEffect(() => {
    const timer = setTimeout(() => {
      // Only trigger search if 3+ letters OR empty (to clear search)
      if (inputValue.length >= 3 || inputValue.length === 0) {
        setDebouncedValue(inputValue);
        if (onChange) {
          onChange(inputValue);
        }
      }
    }, 300); // 300ms debounce

    return () => clearTimeout(timer);
  }, [inputValue]);

  const handleChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleClear = () => {
    setInputValue('');
    if (onChange) {
      onChange('');
    }
  };

  // Show character count if < 3 letters
  const showCharCount = inputValue.length > 0 && inputValue.length < 3;
  const charCount = inputValue.length;

  return (
    <div className="search-bar">
      <div className="search-input-container">
        <input
          type="text"
          value={inputValue}
          onChange={handleChange}
          placeholder={placeholder}
          className="search-input"
          disabled={loading}
        />
        {showCharCount && (
          <span className="search-hint" title="Type at least 3 letters to search">
            {charCount}/3
          </span>
        )}
        {loading && (
          <span className="search-loading-indicator" title="Searching...">
            ⏳
          </span>
        )}
        {inputValue && !loading && (
          <button
            type="button"
            onClick={handleClear}
            className="search-clear-button"
            title="Clear search"
            aria-label="Clear search"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
