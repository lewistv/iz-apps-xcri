import axios from 'axios';

// Get base URL from environment variable or use default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Athlete API endpoints
export const athletesAPI = {
  /**
   * List athletes with filters and pagination
   * @param {Object} params - Query parameters
   * @param {number} params.season_year - Season year (default: 2024)
   * @param {number} params.division - Division code (2030=D1, 2031=D2, 2032=D3)
   * @param {string} params.gender - Gender code (M or F)
   * @param {number} params.limit - Results per page (default: 25)
   * @param {number} params.offset - Pagination offset (default: 0)
   * @param {string} params.search - Search by name or school
   * @param {number} params.min_races - Minimum race count filter
   * @returns {Promise} API response with {total, limit, offset, results}
   */
  list: (params) => api.get('/athletes/', { params }),

  /**
   * Get single athlete by ID
   * @param {number} athleteId - AthleticNet athlete handle
   * @param {Object} params - Query parameters (season_year, etc.)
   * @returns {Promise} API response with athlete details
   */
  get: (athleteId, params) => api.get(`/athletes/${athleteId}`, { params }),

  /**
   * Get team roster
   * @param {number} teamId - AthleticNet team handle
   * @param {Object} params - Query parameters (season_year, etc.)
   * @returns {Promise} API response with roster list
   */
  roster: (teamId, params) => api.get(`/athletes/team/${teamId}/roster`, { params }),
};

// Team API endpoints
export const teamsAPI = {
  /**
   * List teams with filters and pagination
   * @param {Object} params - Query parameters
   * @param {number} params.season_year - Season year (default: 2024)
   * @param {number} params.division - Division code
   * @param {string} params.gender - Gender code (M or F)
   * @param {number} params.limit - Results per page (default: 25)
   * @param {number} params.offset - Pagination offset (default: 0)
   * @param {string} params.search - Search by school name
   * @returns {Promise} API response with {total, limit, offset, results}
   */
  list: (params) => api.get('/teams/', { params }),

  /**
   * Get single team by ID
   * @param {number} teamId - AthleticNet team handle
   * @param {Object} params - Query parameters (season_year, etc.)
   * @returns {Promise} API response with team details
   */
  get: (teamId, params) => api.get(`/teams/${teamId}`, { params }),

  /**
   * Get season resume for a team (Session 004: Issue #15)
   * @param {number} teamId - AthleticNet team handle
   * @param {Object} params - Query parameters (season_year, division, gender)
   * @returns {Promise} API response with resume HTML
   */
  resume: (teamId, params) => api.get(`/teams/${teamId}/resume`, { params }),
};

// Metadata API endpoints
export const metadataAPI = {
  /**
   * Get latest calculation metadata for each division/gender
   * @returns {Promise} API response with latest metadata records
   */
  latest: () => api.get('/metadata/latest'),

  /**
   * List all metadata records with filters
   * @param {Object} params - Query parameters
   * @returns {Promise} API response with metadata list
   */
  list: (params) => api.get('/metadata/', { params }),

  /**
   * Get single metadata record
   * @param {number} metadataId - Metadata ID
   * @returns {Promise} API response with metadata details
   */
  get: (metadataId) => api.get(`/metadata/${metadataId}`),

  /**
   * Get processing summary statistics
   * @returns {Promise} API response with processing stats
   */
  summary: () => api.get('/metadata/summary/processing'),
};

// Health check endpoint
export const healthAPI = {
  /**
   * Check API health and database status
   * @returns {Promise} API response with health status
   */
  check: () => api.get('/health'),
};

// Snapshot API endpoints (historical rankings)
export const snapshotAPI = {
  /**
   * List all available historical snapshots
   * @returns {Promise} API response with list of snapshots
   */
  list: () => api.get('/snapshots/'),

  /**
   * Get athlete rankings from a specific snapshot date
   * @param {string} date - Snapshot date (YYYY-MM-DD format)
   * @param {Object} params - Query parameters (division, gender, limit, offset, search)
   * @returns {Promise} API response with athlete rankings
   */
  getAthletes: (date, params) => api.get(`/snapshots/${date}/athletes`, { params }),

  /**
   * Get team rankings from a specific snapshot date
   * @param {string} date - Snapshot date (YYYY-MM-DD format)
   * @param {Object} params - Query parameters (division, gender, limit, offset, search)
   * @returns {Promise} API response with team rankings
   */
  getTeams: (date, params) => api.get(`/snapshots/${date}/teams`, { params }),

  /**
   * Get metadata for a specific snapshot
   * @param {string} date - Snapshot date (YYYY-MM-DD format)
   * @param {Object} params - Query parameters (division, gender)
   * @returns {Promise} API response with snapshot metadata
   */
  getMetadata: (date, params) => api.get(`/snapshots/${date}/metadata`, { params }),
};

// Division codes reference
export const DIVISIONS = [
  { code: 2030, name: 'NCAA Division I', short: 'D1' },
  { code: 2031, name: 'NCAA Division II', short: 'D2' },
  { code: 2032, name: 'NCAA Division III', short: 'D3' },
  { code: 2028, name: 'NAIA', short: 'NAIA' },
  { code: 19781, name: 'NJCAA Division I', short: 'NJCAA D1' },
  { code: 19782, name: 'NJCAA Division II', short: 'NJCAA D2' },
  { code: 2034, name: 'NJCAA Division III', short: 'NJCAA D3' },
];

// Gender codes reference
export const GENDERS = [
  { code: 'M', name: 'Men' },
  { code: 'F', name: 'Women' },
];

// Export all
export default {
  api,
  athletesAPI,
  teamsAPI,
  metadataAPI,
  healthAPI,
  snapshotAPI,
  DIVISIONS,
  GENDERS,
};
