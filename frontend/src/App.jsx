import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Routes, Route, useSearchParams } from 'react-router-dom';
import Header from './components/Header';
import Breadcrumb from './components/Breadcrumb';
import Footer from './components/Footer';
import DivisionSelector from './components/DivisionSelector';
import GenderSelector from './components/GenderSelector';
import RegionSelector from './components/RegionSelector';
import ConferenceSelector from './components/ConferenceSelector';
import SnapshotSelector from './components/SnapshotSelector';
import SearchBar from './components/SearchBar';
import AthleteTable from './components/AthleteTable';
import TeamTable from './components/TeamTable';
import TeamProfile from './components/TeamProfile';
import Pagination from './components/Pagination';
import ExplainerBox from './components/ExplainerBox';
import FAQ from './pages/FAQ';
import HowItWorks from './pages/HowItWorks';
import Glossary from './pages/Glossary';
import Feedback from './pages/Feedback';
import { athletesAPI, teamsAPI, snapshotAPI } from './services/api';
import './App.css';

/**
 * Main XCRI Rankings Application
 * Displays athlete and team rankings with filtering, search, and pagination
 *
 * Data Sources:
 * - Current Rankings: MySQL database (has athlete handles, full SCS support)
 * - Historical Snapshots: Excel files (no athlete handles, limited features)
 */

// Main Rankings View Component
function MainRankingsView() {
  // URL parameter management (Issue #2: URL persistence for bookmarking/sharing)
  const [searchParams, setSearchParams] = useSearchParams();

  // Initialize state from URL parameters or use defaults
  const getInitialDivision = () => parseInt(searchParams.get('division')) || 2030;
  const getInitialGender = () => searchParams.get('gender') || 'M';
  const getInitialView = () => searchParams.get('view') || 'athletes';
  const getInitialRegion = () => searchParams.get('region') || null;
  const getInitialConference = () => searchParams.get('conference') || null;
  const getInitialSearch = () => searchParams.get('search') || '';

  // State management
  const [division, setDivision] = useState(getInitialDivision());
  const [gender, setGender] = useState(getInitialGender());
  const [view, setView] = useState(getInitialView());
  const [search, setSearch] = useState(getInitialSearch());
  const [offset, setOffset] = useState(0);
  const [limit] = useState(100); // Fixed limit (items per page)
  const [data, setData] = useState({ results: [], total: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Geographic filter state (Session 009B Phase 4)
  const [region, setRegion] = useState(getInitialRegion()); // null = "All Regions"
  const [conference, setConference] = useState(getInitialConference()); // null = "All Conferences"
  const [availableRegions, setAvailableRegions] = useState([]);
  const [availableConferences, setAvailableConferences] = useState([]);

  // Snapshot state (for historical rankings)
  const [isHistorical, setIsHistorical] = useState(false);
  const [selectedSnapshot, setSelectedSnapshot] = useState(null);

  // Session 009C: Full dataset for client-side filtering
  const [fullDataset, setFullDataset] = useState([]);

  // Debounce timer refs (Issue #8: Prevent overwhelming with rapid changes)
  const debounceTimerRef = useRef(null);  // For API calls (filter changes)
  const searchDebounceRef = useRef(null); // For search input

  // Derive current season year (2025 for current, extract from snapshot for historical)
  const getCurrentSeasonYear = () => {
    if (isHistorical && selectedSnapshot) {
      // Extract year from snapshot date (e.g., "2024-11-25" -> 2024)
      return parseInt(selectedSnapshot.split('-')[0]);
    }
    return 2025; // Current season
  };

  const seasonYear = getCurrentSeasonYear();

  // Helper function to get division name
  const getDivisionName = (divCode) => {
    const divisions = {
      2030: 'NCAA D1',
      2031: 'NCAA D2',
      2032: 'NCAA D3',
      2040: 'NAIA',
      2050: 'NJCAA D1',
      2051: 'NJCAA D2',
      2052: 'NJCAA D3',
    };
    return divisions[divCode] || 'Unknown';
  };

  // Update page title based on current view and filters
  useEffect(() => {
    const divName = getDivisionName(division);
    const genderText = gender === 'M' ? 'Men' : 'Women';
    const viewText = view === 'athletes' ? 'Athletes' : 'Teams';

    let title = `USTFCCCA ::: XCRI Rankings - ${divName} ${genderText} ${viewText}`;

    if (isHistorical && selectedSnapshot) {
      title = `USTFCCCA ::: XCRI Rankings - ${divName} ${genderText} ${viewText} (${selectedSnapshot})`;
    }

    document.title = title;
  }, [division, gender, view, isHistorical, selectedSnapshot]);

  // Update URL parameters when filters change (Issue #2: URL persistence)
  useEffect(() => {
    const params = {};

    // Add current filter values to URL (skip defaults to keep URL clean)
    if (division !== 2030) params.division = division;
    if (gender !== 'M') params.gender = gender;
    if (view !== 'athletes') params.view = view;
    if (region) params.region = region;
    if (conference) params.conference = conference;
    if (search) params.search = search;

    setSearchParams(params, { replace: true });
  }, [division, gender, view, region, conference, search]);

  // Fetch data when filters change (Session 010: Server-side region/conference filtering)
  // Issue #8: Debounce to prevent overwhelming API with rapid filter changes
  useEffect(() => {
    // Clear existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Show loading state immediately for instant UI feedback
    setLoading(true);

    // Set new debounced timer (300ms delay)
    debounceTimerRef.current = setTimeout(() => {
      if (isHistorical && selectedSnapshot) {
        fetchHistoricalData();
      } else if (!isHistorical) {
        fetchCurrentData();
      } else {
        // No snapshot selected in historical mode
        setLoading(false);
      }
    }, 300);

    // Cleanup: Clear timer on unmount or dependency change
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [division, gender, view, isHistorical, selectedSnapshot, region, conference]);

  // Apply client-side filtering and pagination (Session 010: Only search is client-side now)
  // Issue #8: Debounce search to prevent excessive re-renders while typing
  useEffect(() => {
    // Clear existing search timer
    if (searchDebounceRef.current) {
      clearTimeout(searchDebounceRef.current);
    }

    // Debounce search (150ms - shorter delay for instant feedback)
    searchDebounceRef.current = setTimeout(() => {
      applyFiltersAndPagination();
    }, 150);

    // Cleanup
    return () => {
      if (searchDebounceRef.current) {
        clearTimeout(searchDebounceRef.current);
      }
    };
  }, [fullDataset, search, offset]);

  /**
   * Apply client-side filtering and pagination (Session 010)
   * Only search is client-side; region/conference handled server-side
   */
  const applyFiltersAndPagination = () => {
    if (!fullDataset || fullDataset.length === 0) {
      setData({ results: [], total: 0 });
      return;
    }

    // Apply search filter to full dataset (client-side for instant feedback)
    let filtered = [...fullDataset];

    // Search filter (case-insensitive)
    if (search && search.trim().length > 0) {
      const searchLower = search.toLowerCase().trim();
      filtered = filtered.filter(item => {
        const athleteName = item.athlete_name?.toLowerCase() ||
                          `${item.athlete_name_first} ${item.athlete_name_last}`.toLowerCase();
        const teamName = item.team_name?.toLowerCase() || '';
        return athleteName.includes(searchLower) || teamName.includes(searchLower);
      });
    }

    // NOTE: Region and conference filtering now done server-side (Session 010)

    // Apply pagination to filtered results
    const startIndex = offset;
    const endIndex = offset + limit;
    const paginatedResults = filtered.slice(startIndex, endIndex);

    setData({
      results: paginatedResults,
      total: filtered.length,
    });
  };

  /**
   * Fetch current rankings from MySQL database
   * Session 010: Use server-side filtering for region/conference
   */
  const fetchCurrentData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch data with server-side region/conference filtering
      const params = {
        season_year: 2025,
        division,
        gender,
        limit: 50000,  // Large limit to get full filtered results
        offset: 0,
      };

      // Add server-side region/conference filters (Session 010)
      if (region) params.region = region;
      if (conference) params.conference = conference;

      const api = view === 'athletes' ? athletesAPI : teamsAPI;
      const response = await api.list(params);

      const results = response.data.results || [];

      // Extract unique regions and conferences
      const uniqueRegions = [...new Set(
        results
          .map(item => item.regl_group_name)
          .filter(name => name && name.trim() !== '')
      )].sort();
      const uniqueConferences = [...new Set(
        results
          .map(item => item.conf_group_name)
          .filter(name => name && name.trim() !== '')
      )].sort();

      setAvailableRegions(uniqueRegions);
      setAvailableConferences(uniqueConferences);
      setFullDataset(results);

    } catch (err) {
      console.error('API Error:', err);
      setError(err.response?.data?.message || err.message || 'Failed to fetch data');
      setFullDataset([]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetch historical rankings from snapshot files
   * Session 010: Use server-side filtering for region/conference
   */
  const fetchHistoricalData = async () => {
    if (!selectedSnapshot) return;

    setLoading(true);
    setError(null);

    try {
      // Fetch data with server-side region/conference filtering
      const params = {
        division,
        gender,
        limit: 50000,  // Large limit to get full filtered results
        offset: 0,
      };

      // Add server-side region/conference filters (Session 010)
      if (region) params.region = region;
      if (conference) params.conference = conference;

      const fetchMethod = view === 'athletes'
        ? snapshotAPI.getAthletes
        : snapshotAPI.getTeams;

      const response = await fetchMethod(selectedSnapshot, params);

      const results = response.data.results || [];

      // Extract unique regions and conferences
      const uniqueRegions = [...new Set(
        results
          .map(item => item.regl_group_name)
          .filter(name => name && name.trim() !== '')
      )].sort();
      const uniqueConferences = [...new Set(
        results
          .map(item => item.conf_group_name)
          .filter(name => name && name.trim() !== '')
      )].sort();

      setAvailableRegions(uniqueRegions);
      setAvailableConferences(uniqueConferences);
      setFullDataset(results);

    } catch (err) {
      console.error('Snapshot API Error:', err);
      setError(err.response?.data?.message || err.message || 'Failed to fetch snapshot data');
      setFullDataset([]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle division change - reset to first page and clear geographic filters
   * (Different divisions have different regions/conferences)
   */
  const handleDivisionChange = (newDivision) => {
    setDivision(newDivision);
    setRegion(null);  // Clear region filter
    setConference(null);  // Clear conference filter
    setOffset(0);
  };

  /**
   * Handle gender change - reset to first page
   */
  const handleGenderChange = (newGender) => {
    setGender(newGender);
    setRegion(null);  // Clear region filter (different athletes)
    setConference(null);  // Clear conference filter
    setOffset(0);
  };

  /**
   * Handle region change - reset to first page
   */
  const handleRegionChange = (newRegion) => {
    setRegion(newRegion);
    setOffset(0);
  };

  /**
   * Handle conference change - reset to first page
   */
  const handleConferenceChange = (newConference) => {
    setConference(newConference);
    setOffset(0);
  };

  /**
   * Handle view change (athletes/teams) - reset to first page
   */
  const handleViewChange = (newView) => {
    setView(newView);
    setOffset(0);
  };

  /**
   * Handle search - reset to first page
   */
  const handleSearch = (query) => {
    setSearch(query);
    setOffset(0);
  };

  /**
   * Handle page change
   */
  const handlePageChange = (newOffset) => {
    setOffset(newOffset);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  /**
   * Handle snapshot view mode change (current vs historical)
   */
  const handleViewModeChange = (historical) => {
    setIsHistorical(historical);
    setOffset(0); // Reset to first page
  };

  /**
   * Handle snapshot date selection
   */
  const handleSnapshotChange = (date) => {
    setSelectedSnapshot(date);
    setOffset(0); // Reset to first page
  };

  return (
    <div className="app">
      {/* USTFCCCA Header */}
      <Header />

      {/* Breadcrumb Navigation */}
      <Breadcrumb />

      {/* Page Title */}
      <div className="page-title-section">
        <h1 className="page-title">
          <span className="icon">🏆</span> XCRI: Cross Country Rating Index
        </h1>
      </div>

      {/* Page Subtitle */}
      <div className="page-subtitle">
        <p>
          {isHistorical && selectedSnapshot
            ? `Historical Rankings - ${selectedSnapshot}`
            : 'Current Rankings - 2025 Season (as of October 20, 2025)'}
        </p>
      </div>

      {/* Snapshot Selector */}
      <SnapshotSelector
        isHistorical={isHistorical}
        selectedDate={selectedSnapshot}
        onViewChange={handleViewModeChange}
        onDateChange={handleSnapshotChange}
      />

      {/* Controls */}
      <div className="controls">
        <div className="controls-row">
          <DivisionSelector value={division} onChange={handleDivisionChange} />
          <GenderSelector value={gender} onChange={handleGenderChange} />

          {/* Geographic Filters (Session 009B Phase 4) */}
          <RegionSelector
            value={region}
            onChange={handleRegionChange}
            regions={availableRegions}
            disabled={availableRegions.length === 0}
          />
          <ConferenceSelector
            value={conference}
            onChange={handleConferenceChange}
            conferences={availableConferences}
            disabled={availableConferences.length === 0}
          />

          {/* View Toggle */}
          <div className="view-toggle">
            <label>View:</label>
            <div className="button-group">
              <button
                onClick={() => handleViewChange('athletes')}
                className={`selector-button ${view === 'athletes' ? 'active' : ''}`}
              >
                Athletes
              </button>
              <button
                onClick={() => handleViewChange('teams')}
                className={`selector-button ${view === 'teams' ? 'active' : ''}`}
              >
                Teams
              </button>
            </div>
          </div>

          {/* Search */}
          <SearchBar value={search} onChange={handleSearch} loading={loading} />
        </div>
      </div>

      {/* Content */}
      <main className="content">
        {/* Result Count */}
        {!loading && !error && data.results && data.results.length > 0 && (
          <div className="results-summary">
            Showing {data.results.length} of {data.total.toLocaleString()} {view}
            {search && ` matching "${search}"`}
            {region && ` in ${region}`}
            {conference && ` in ${conference}`}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading {view === 'athletes' ? 'athletes' : 'teams'}...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="error-message">
            <h3>Unable to Load Data</h3>
            <p>{error}</p>
            <button onClick={isHistorical ? fetchHistoricalData : fetchCurrentData} className="retry-button">
              Try Again
            </button>
          </div>
        )}

        {/* Data Table */}
        {!loading && !error && data.results && data.results.length > 0 && (
          <>
            {view === 'athletes' ? (
              <>
                <ExplainerBox
                  title="What is XCRI?"
                  links={[{ text: "Learn More in FAQ", href: "/faq" }]}
                >
                  <p>
                    The <strong>Cross Country Ratings Index (XCRI)</strong> is a comprehensive ranking
                    system that evaluates athletes based on head-to-head race results and strength of
                    schedule. Rankings are based <strong>solely on current season performances</strong> and
                    are objective and deterministic (no simulations used).
                  </p>
                  {/* Division-specific NCAA qualification rules - Session 009D, Session 010 (dynamic year) */}
                  {division === 2030 && (
                    <p className="qualification-note">
                      <strong>NCAA D1 Rules</strong>: Performances must have occurred on or after September 13, {seasonYear}
                      {' '}and been at least {gender === 'M' ? '7,500 meters (7.5K)' : '4,500 meters (4.5K)'} in distance.
                    </p>
                  )}
                  {division === 2031 && (
                    <p className="qualification-note">
                      <strong>NCAA D2 Rules</strong>: Performances must have occurred on or after September 13, {seasonYear}
                      {' '}and been at least {gender === 'M' ? '7,000 meters (7K)' : '4,800 meters (4.8K)'} in distance.
                    </p>
                  )}
                  {division === 2032 && (
                    <p className="qualification-note">
                      <strong>NCAA D3 Rules</strong>: Performances must have occurred on or after September 20, {seasonYear}
                      {' '}and been at least {gender === 'M' ? '7,000 meters (7K)' : '4,500 meters (4.5K)'} in distance.
                    </p>
                  )}
                  <p>
                    <em>Note: Early in the season, rankings may not fully reflect potential as
                    competition may be limited. Rankings improve as more data accumulates.</em>
                  </p>
                </ExplainerBox>
                <AthleteTable
                  athletes={data.results}
                  isHistorical={isHistorical}  // Pass flag to disable SCS modal for historical
                />
              </>
            ) : (
              <>
                <ExplainerBox
                  title="How are Team Rankings Calculated?"
                  links={[{ text: "Team Scoring FAQ", href: "/faq#faq-9-do-team-rankings-consider-head-to-head-team-results" }]}
                >
                  <p>
                    Team rankings follow <strong>NCAA cross country scoring rules</strong>: Up to 7 athletes
                    from each team can earn a score, but only the <strong>top 5 athletes' ranks are added
                    together</strong> to calculate the team's score. Lower team scores are better (like in XC meets).
                    Teams are then ranked by their team score.
                  </p>
                  <p>
                    <strong>Important</strong>: Team rankings are based solely on <strong>individual athlete
                    XCRI rankings</strong>. Head-to-head team results (e.g., which team won at a specific meet)
                    are <strong>not</strong> a factor. This ensures rankings reflect overall squad depth and
                    quality, not single-meet outcomes.
                  </p>
                </ExplainerBox>
                <TeamTable teams={data.results} />
              </>
            )}

            {/* Pagination */}
            <Pagination
              total={data.total}
              limit={limit}
              offset={offset}
              onPageChange={handlePageChange}
            />
          </>
        )}

        {/* No Results */}
        {!loading && !error && data.results && data.results.length === 0 && (
          <div className="no-results">
            <h3>No Results Found</h3>
            <p>No {view} found matching your current filters.</p>
            {search && <p>Try adjusting your search term.</p>}
            {(region || conference) && <p>Try selecting "All Regions" or "All Conferences".</p>}
          </div>
        )}
      </main>

      {/* USTFCCCA Footer */}
      <Footer />
    </div>
  );
}

// App Component with Routing
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MainRankingsView />} />
      <Route path="/team/:teamId" element={<TeamProfile />} />
      <Route path="/team/:teamId/:snapshot" element={<TeamProfile />} />
      <Route path="/faq" element={<FAQ />} />
      <Route path="/how-it-works" element={<HowItWorks />} />
      <Route path="/glossary" element={<Glossary />} />
      <Route path="/feedback" element={<Feedback />} />
    </Routes>
  );
}
