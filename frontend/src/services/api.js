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

// Team Knockout API endpoints (Session 015)
export const teamKnockoutAPI = {
  /**
   * List Team Knockout rankings (H2H-based) with filters and pagination
   * @param {Object} params - Query parameters
   * @param {number} params.season_year - Season year (default: 2025)
   * @param {string} params.rank_group_type - Ranking type (D=Division, R=Regional, C=Conference)
   * @param {number} params.rank_group_fk - Ranking group ID (division code, etc.)
   * @param {string} params.gender_code - Gender code (M or F)
   * @param {number} params.limit - Results per page (default: 100)
   * @param {number} params.offset - Pagination offset (default: 0)
   * @param {string} params.search - Search by team name
   * @returns {Promise} API response with {total, limit, offset, results}
   */
  list: (params) => api.get('/team-knockout/', { params }),

  /**
   * Get single Team Knockout ranking by team ID
   * @param {number} teamId - Team identifier (anet_team_hnd)
   * @param {Object} params - Query parameters (season_year, rank_group_type, etc.)
   * @returns {Promise} API response with team knockout ranking details
   */
  get: (teamId, params) => api.get(`/team-knockout/${teamId}`, { params }),

  /**
   * Get all matchups for a specific team
   * @param {number} teamId - Team identifier (required)
   * @param {Object} params - Query parameters
   * @returns {Promise} API response with {total, limit, offset, stats, matchups}
   */
  matchups: (teamId, params) => api.get('/team-knockout/matchups', { params: { ...params, team_id: teamId } }),

  /**
   * Get head-to-head record between two teams
   * @param {number} teamAId - First team identifier
   * @param {number} teamBId - Second team identifier
   * @param {Object} params - Query parameters
   * @returns {Promise} API response with H2H stats and matchup history
   */
  headToHead: (teamAId, teamBId, params) => api.get('/team-knockout/matchups/head-to-head', {
    params: { ...params, team_a_id: teamAId, team_b_id: teamBId }
  }),

  /**
   * Get all matchups from a specific meet
   * @param {number} raceHnd - Race handle (AthleticNET race ID)
   * @param {Object} params - Query parameters
   * @returns {Promise} API response with meet info and all matchups
   */
  meetMatchups: (raceHnd, params) => api.get(`/team-knockout/matchups/meet/${raceHnd}`, { params }),

  /**
   * Find common opponents between two teams
   * @param {number} teamAId - First team identifier
   * @param {number} teamBId - Second team identifier
   * @param {Object} params - Query parameters
   * @returns {Promise} API response with common opponent analysis
   */
  commonOpponents: (teamAId, teamBId, params) => api.get('/team-knockout/matchups/common-opponents', {
    params: { ...params, team_a_id: teamAId, team_b_id: teamBId }
  }),
};

// Metadata API endpoints
export const metadataAPI = {
  /**
   * Get latest calculation date (optimized query)
   * Session 007: Lightweight endpoint for date display
   * @returns {Promise} API response with { calculated_at: "2025-10-22T16:12:21" }
   */
  latestDate: () => api.get('/metadata/latest/date'),

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
  teamKnockoutAPI,
  metadataAPI,
  healthAPI,
  snapshotAPI,
  DIVISIONS,
  GENDERS,
};
