import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
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
  // State management
  const [division, setDivision] = useState(2030); // D1 by default
  const [gender, setGender] = useState('M'); // Men by default
  const [view, setView] = useState('athletes'); // 'athletes' or 'teams'
  const [search, setSearch] = useState('');
  const [offset, setOffset] = useState(0);
  const [limit] = useState(100); // Fixed limit (items per page)
  const [data, setData] = useState({ results: [], total: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Geographic filter state (Session 009B Phase 4)
  const [region, setRegion] = useState(null); // null = "All Regions"
  const [conference, setConference] = useState(null); // null = "All Conferences"
  const [availableRegions, setAvailableRegions] = useState([]);
  const [availableConferences, setAvailableConferences] = useState([]);

  // Snapshot state (for historical rankings)
  const [isHistorical, setIsHistorical] = useState(false);
  const [selectedSnapshot, setSelectedSnapshot] = useState(null);

  // Session 009C: Full dataset for client-side filtering
  const [fullDataset, setFullDataset] = useState([]);

  // Derive current season year (2025 for current, extract from snapshot for historical)
  const getCurrentSeasonYear = () => {
    if (isHistorical && selectedSnapshot) {
      // Extract year from snapshot date (e.g., "2024-11-25" -> 2024)
      return parseInt(selectedSnapshot.split('-')[0]);
    }
    return 2025; // Current season
  };

  const seasonYear = getCurrentSeasonYear();

  // Fetch data when filters change (Session 010: Server-side region/conference filtering)
  useEffect(() => {
    if (isHistorical && selectedSnapshot) {
      fetchHistoricalData();
    } else if (!isHistorical) {
      fetchCurrentData();
    }
    // Don't fetch if historical mode but no snapshot selected
  }, [division, gender, view, isHistorical, selectedSnapshot, region, conference]);

  // Apply client-side filtering and pagination (Session 010: Only search is client-side now)
  useEffect(() => {
    applyFiltersAndPagination();
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
        {/* Loading State */}
        {loading && (
          <div className="loading-message">
            <div className="spinner"></div>
            <p>Loading data...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="error-message">
            <h3>Error</h3>
            <p>{error}</p>
            <button onClick={isHistorical ? fetchHistoricalData : fetchCurrentData} className="retry-button">
              Retry
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
                      <strong>NCAA D3 Rules</strong>: Performances must have occurred on or after September 28, {seasonYear}
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
          <div className="empty-message">
            <p>No {view} found matching your criteria.</p>
            {search && <p>Try adjusting your search term.</p>}
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
    </Routes>
  );
}
