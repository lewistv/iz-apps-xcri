import React from 'react';
import PropTypes from 'prop-types';
import './RankingsTable.css';

/**
 * Unified Rankings Table Component
 *
 * Single table component used for both Athletes and Teams rankings.
 * Eliminates code duplication between AthleteTable and TeamTable.
 *
 * Props:
 * - type: 'athletes' or 'teams'
 * - data: Array of ranking objects
 * - columns: Array of column configurations
 * - isHistorical: Boolean indicating if data is from historical snapshot
 * - onRowClick: Optional callback for row clicks
 * - onSCSClick: Optional callback for SCS score clicks (athletes only)
 * - loading: Boolean for loading state
 */
export default function RankingsTable({
  type = 'athletes',
  data = [],
  columns = [],
  isHistorical = false,
  onRowClick = null,
  onSCSClick = null,
  loading = false,
}) {
  if (loading) {
    return (
      <div className="rankings-table-loading">
        <div className="loading-spinner"></div>
        <p>Loading rankings...</p>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="rankings-table-empty">
        <p>No rankings found matching your criteria.</p>
      </div>
    );
  }

  /**
   * Render a cell value based on column configuration
   */
  const renderCell = (row, column) => {
    const value = row[column.field];

    // Handle clickable cells
    if (column.clickable && column.onClick) {
      return (
        <button
          className="cell-link"
          onClick={() => column.onClick(row)}
          title={column.clickTitle || `View ${value}`}
        >
          {column.format ? column.format(value, row) : value || '-'}
        </button>
      );
    }

    // Handle formatted cells
    if (column.format) {
      return column.format(value, row);
    }

    // Handle null/undefined
    if (value === null || value === undefined) {
      return '-';
    }

    // Default rendering
    return value;
  };

  return (
    <div className="rankings-table-container">
      <table className="rankings-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th
                key={column.id}
                className={column.className || ''}
                title={column.tooltip || ''}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr
              key={row.ranking_id || row.anet_athlete_hnd || row.anet_team_hnd || index}
              className={onRowClick ? 'clickable-row' : ''}
              onClick={onRowClick ? () => onRowClick(row) : null}
            >
              {columns.map((column) => (
                <td
                  key={`${row.ranking_id || index}-${column.id}`}
                  className={column.className || ''}
                >
                  {renderCell(row, column)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

RankingsTable.propTypes = {
  type: PropTypes.oneOf(['athletes', 'teams']).isRequired,
  data: PropTypes.array,
  columns: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      field: PropTypes.string.isRequired,
      format: PropTypes.func,
      clickable: PropTypes.bool,
      onClick: PropTypes.func,
      clickTitle: PropTypes.string,
      className: PropTypes.string,
      tooltip: PropTypes.string,
    })
  ).isRequired,
  isHistorical: PropTypes.bool,
  onRowClick: PropTypes.func,
  onSCSClick: PropTypes.func,
  loading: PropTypes.bool,
};
