import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { teamsAPI, athletesAPI, snapshotAPI } from '../services/api';

/**
 * Team Profile Page Component
 * Shows team details and roster with real API data
 * Session 009D: Fixed to use API client instead of hardcoded URLs
 * Session 010: Fixed to use division/gender from URL params for correct team lookup
 * Session 010: Added historical rankings progression table
 */
export default function TeamProfile() {
  const { teamId, snapshot } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [teamData, setTeamData] = useState(null);
  const [roster, setRoster] = useState([]);
  const [historicalRankings, setHistoricalRankings] = useState([]);
  const [seasonResume, setSeasonResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [loadingResume, setLoadingResume] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTeamData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Determine season year from snapshot or use default
        const seasonYear = snapshot ? parseInt(snapshot.split('-')[0]) : 2025;

        // Get division and gender from URL query params (Session 010 fix)
        const division = searchParams.get('division');
        const gender = searchParams.get('gender');

        let teamResponse;
        let rosterResponse;

        if (snapshot) {
          // HISTORICAL SNAPSHOT: Fetch from snapshot API
          // Snapshot API doesn't have single-team endpoint, so fetch all teams and filter
          const teamsResponse = await snapshotAPI.getTeams(snapshot, {
            division: parseInt(division),
            gender: gender,
            limit: 500  // Get enough to find our team
          });

          // Find this specific team in the results
          const teams = teamsResponse.data.results || [];
          const team = teams.find(t => parseInt(t.anet_team_hnd) === parseInt(teamId));

          if (team) {
            teamResponse = { data: team };

            // Fetch roster from snapshot athletes
            const athletesResponse = await snapshotAPI.getAthletes(snapshot, {
              division: parseInt(division),
              gender: gender,
              limit: 500  // Get enough athletes to find all team members
            });

            // Filter athletes by team name (snapshots may not have team handle filtering)
            const allAthletes = athletesResponse.data.results || [];
            const teamRoster = allAthletes.filter(a => a.team_name === team.team_name);

            rosterResponse = { data: { results: teamRoster } };
          } else {
            throw new Error('Team not found in snapshot');
          }
        } else {
          // CURRENT RANKINGS: Fetch from MySQL API
          const params = { season_year: seasonYear };
          if (division) params.division = parseInt(division);
          if (gender) params.gender = gender;

          teamResponse = await teamsAPI.get(teamId, params);

          if (teamResponse.data) {
            // Fetch team roster using API client - filter by gender (Session 010)
            const rosterParams = {
              season_year: seasonYear,
              limit: 100
            };
            // Add gender filter to match team's gender
            if (teamResponse.data.gender_code) {
              rosterParams.gender = teamResponse.data.gender_code;
            }
            rosterResponse = await athletesAPI.roster(teamId, rosterParams);
          }
        }

        if (teamResponse && teamResponse.data) {
          setTeamData(teamResponse.data);
          setRoster(rosterResponse?.data?.results || []);
        } else {
          throw new Error('Team not found');
        }
      } catch (err) {
        console.error('Error fetching team data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (teamId) {
      fetchTeamData();
    }
  }, [teamId, snapshot, searchParams]);

  // Update page title when team data loads
  useEffect(() => {
    if (teamData && teamData.team_name) {
      document.title = `USTFCCCA ::: XCRI - ${teamData.team_name}`;
    } else {
      document.title = 'USTFCCCA ::: XCRI - Team Profile';
    }
  }, [teamData]);

  // Fetch historical rankings progression (Session 010)
  useEffect(() => {
    const fetchHistoricalRankings = async () => {
      // Only fetch if we have team data and we're viewing current rankings (not a snapshot)
      if (!teamData || snapshot) {
        return;
      }

      try {
        setLoadingHistory(true);

        // Get list of available snapshots
        const snapshotsResponse = await snapshotAPI.list();
        const snapshots = snapshotsResponse.data.snapshots || [];

        // Filter to current season only
        const currentSeasonSnapshots = snapshots.filter(s =>
          s.date.startsWith(teamData.season_year.toString())
        );

        // Fetch team ranking for each snapshot
        const rankingsPromises = currentSeasonSnapshots.map(async (snap) => {
          try {
            // Fetch ALL teams for this division/gender (no search filter)
            // We'll filter client-side to find this specific team
            const response = await snapshotAPI.getTeams(snap.date, {
              division: teamData.division_code,
              gender: teamData.gender_code,
              limit: 500  // Get enough teams to find ours
            });

            // Find this team in the results by team handle AND gender (Session 010: critical for disambiguation)
            const teams = response.data.results || [];
            const teamInSnapshot = teams.find(t =>
              parseInt(t.anet_team_hnd) === parseInt(teamData.anet_team_hnd || teamId) &&
              t.gender_code === teamData.gender_code
            );

            if (teamInSnapshot) {
              return {
                date: snap.date,
                // Snapshot API uses different field names than MySQL API
                rank: teamInSnapshot.rank || teamInSnapshot.team_rank,
                score: teamInSnapshot.team_score || teamInSnapshot.team_xcri_score,
                athletesCount: teamInSnapshot.squad_size || teamInSnapshot.athletes_count
              };
            }
            return null;
          } catch (err) {
            console.error(`Error fetching snapshot ${snap.date}:`, err);
            return null;
          }
        });

        const rankings = await Promise.all(rankingsPromises);
        const validRankings = rankings.filter(r => r !== null);

        // Sort by date ascending
        validRankings.sort((a, b) => new Date(a.date) - new Date(b.date));

        setHistoricalRankings(validRankings);
      } catch (err) {
        console.error('Error fetching historical rankings:', err);
      } finally {
        setLoadingHistory(false);
      }
    };

    fetchHistoricalRankings();
  }, [teamData, teamId, snapshot]);

  // Fetch season resume (Session 004: Issue #15)
  useEffect(() => {
    const fetchSeasonResume = async () => {
      // Only fetch for current rankings (not snapshots)
      if (!teamData || snapshot) {
        return;
      }

      try {
        setLoadingResume(true);

        const resumeResponse = await teamsAPI.resume(teamId, {
          season_year: teamData.season_year,
          division: teamData.division_code,
          gender: teamData.gender_code
        });

        if (resumeResponse && resumeResponse.data) {
          setSeasonResume(resumeResponse.data);
        }
      } catch (err) {
        // Resume not found is not an error - it's optional data
        if (err.response && err.response.status !== 404) {
          console.error('Error fetching season resume:', err);
        }
      } finally {
        setLoadingResume(false);
      }
    };

    fetchSeasonResume();
  }, [teamData, teamId, snapshot]);

  // Get division name from code
  const getDivisionName = (code) => {
    const divisions = {
      2030: 'NCAA Division I',
      2031: 'NCAA Division II',
      2032: 'NCAA Division III',
      2028: 'NAIA',
      19781: 'NJCAA Division I',
      19782: 'NJCAA Division II',
      2034: 'NJCAA Division III'
    };
    return divisions[code] || `Division ${code}`;
  };

  if (loading) {
    return (
      <div className="team-profile">
        <button onClick={() => navigate(-1)} className="back-button">
          ← Back to Rankings
        </button>
        <div className="loading-message">Loading team profile...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="team-profile">
        <button onClick={() => navigate(-1)} className="back-button">
          ← Back to Rankings
        </button>
        <div className="error-message">
          <h3>Error Loading Team</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!teamData) {
    return (
      <div className="team-profile">
        <button onClick={() => navigate(-1)} className="back-button">
          ← Back to Rankings
        </button>
        <div className="error-message">
          <h3>Team Not Found</h3>
          <p>Team ID: {teamId}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="team-profile">
      {/* Back Button */}
      <button onClick={() => navigate(-1)} className="back-button">
        ← Back to Rankings
      </button>

      {/* Team Header */}
      <div className="team-header">
        <h2>{teamData.team_name}</h2>
        {snapshot && (
          <p className="snapshot-date-note">
            Historical Snapshot: {(() => {
              // Format date without timezone conversion
              const [year, month, day] = snapshot.split('-');
              const dateObj = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
              return dateObj.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              });
            })()}
          </p>
        )}
        <p className="team-id-note">Team ID: {teamId}</p>
      </div>

      {/* Team Info Card */}
      <div className="team-info">
        <div className="info-row">
          <span className="info-label">Division:</span>
          <span className="info-value">{getDivisionName(teamData.division_code)}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Gender:</span>
          <span className="info-value">
            {teamData.gender_code === 'M' ? "Men's" : "Women's"}
          </span>
        </div>
        <div className="info-row">
          <span className="info-label">Region:</span>
          <span className="info-value">{teamData.regl_group_name || 'N/A'}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Conference:</span>
          <span className="info-value">{teamData.conf_group_name || 'N/A'}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Team XCRI Rank:</span>
          <span className="info-value">#{teamData.team_rank}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Team XCRI Score:</span>
          <span className="info-value">{teamData.team_xcri_score?.toFixed(1) || 'N/A'}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Date of XCRI Ranking:</span>
          <span className="info-value">
            {teamData.calculated_at
              ? new Date(teamData.calculated_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })
              : teamData.checkpoint_date || 'N/A'
            }
          </span>
        </div>
        <div className="info-row">
          <span className="info-label">Top 5 Average:</span>
          <span className="info-value">{teamData.top5_average?.toFixed(1) || 'N/A'}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Top 7 Average:</span>
          <span className="info-value">{teamData.top7_average?.toFixed(1) || 'N/A'}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Squad Size:</span>
          <span className="info-value">{teamData.athletes_count} athletes</span>
        </div>
        <div className="info-row">
          <span className="info-label">Season:</span>
          <span className="info-value">{teamData.season_year}</span>
        </div>
      </div>

      {/* Roster Section */}
      <div className="roster-section">
        <h3>Team Roster ({roster.length} athletes)</h3>

        {roster.length === 0 ? (
          <div className="stub-message">
            <h4>No Roster Data Available</h4>
            <p>This team does not have any ranked athletes in the current dataset.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="roster-table rankings-table">
              <thead>
                <tr>
                  <th>XCRI Rank</th>
                  <th>Athlete Name</th>
                  <th>SCS Score</th>
                  <th>SCS Rank</th>
                  <th>Races</th>
                  <th>H2H Record</th>
                </tr>
              </thead>
              <tbody>
                {roster.map((athlete, index) => (
                  <tr key={athlete.ranking_id} className={index < 7 ? 'top-seven' : ''}>
                    <td className="rank-cell">#{athlete.athlete_rank}</td>
                    <td className="name-cell">
                      <a
                        href={`https://www.athletic.net/athlete/${athlete.anet_athlete_hnd}/cross-country/`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="athlete-link"
                      >
                        {athlete.athlete_name_first} {athlete.athlete_name_last}
                      </a>
                    </td>
                    <td className="score-cell">{athlete.scs_score?.toFixed(1) || 'N/A'}</td>
                    <td className="rank-cell">#{athlete.scs_rank || 'N/A'}</td>
                    <td className="races-cell">{athlete.races_count || 0}</td>
                    <td className="h2h-cell">
                      {athlete.h2h_wins}-{athlete.h2h_losses}
                      {athlete.h2h_win_rate !== null &&
                        ` (${(athlete.h2h_win_rate * 100).toFixed(0)}%)`
                      }
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Historical Rankings Progression (Session 010) */}
      {!snapshot && (
        <div className="historical-rankings-section">
          <h3>XCRI Team Rankings by Date</h3>

          {loadingHistory ? (
            <div className="loading-message">Loading historical rankings...</div>
          ) : historicalRankings.length === 0 ? (
            <div className="stub-message">
              <p>No historical ranking data available for this season.</p>
            </div>
          ) : (
            <div className="table-container">
              <table className="historical-table rankings-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>XCRI Rank</th>
                    <th>XCRI Score</th>
                    <th>Squad Size</th>
                  </tr>
                </thead>
                <tbody>
                  {historicalRankings.map((ranking, index) => (
                    <tr key={ranking.date}>
                      <td className="date-cell">
                        {/* Format date without timezone conversion to avoid off-by-one errors */}
                        {(() => {
                          const [year, month, day] = ranking.date.split('-');
                          const dateObj = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
                          return dateObj.toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric'
                          });
                        })()}
                      </td>
                      <td className="rank-cell">
                        #{ranking.rank}
                        {index > 0 && (
                          <span className={`rank-change ${
                            ranking.rank < historicalRankings[index - 1].rank ? 'improved' :
                            ranking.rank > historicalRankings[index - 1].rank ? 'declined' : 'same'
                          }`}>
                            {ranking.rank < historicalRankings[index - 1].rank &&
                              ` ↑ ${historicalRankings[index - 1].rank - ranking.rank}`}
                            {ranking.rank > historicalRankings[index - 1].rank &&
                              ` ↓ ${ranking.rank - historicalRankings[index - 1].rank}`}
                          </span>
                        )}
                      </td>
                      <td className="score-cell">{ranking.score?.toFixed(1) || 'N/A'}</td>
                      <td className="athletes-cell">{ranking.athletesCount || 0} athletes</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Season Resume Section (Session 004: Issue #15) */}
      {!snapshot && (
        <div className="season-resume-section">
          <h3>Season Resume</h3>

          {loadingResume ? (
            <div className="loading-message">Loading season resume...</div>
          ) : !seasonResume ? (
            <div className="stub-message">
              <p>No season resume data available for this team.</p>
            </div>
          ) : (
            <div className="season-resume-container">
              {/* Render HTML from trusted database source */}
              <div
                className="season-resume-content"
                dangerouslySetInnerHTML={{ __html: seasonResume.season_html }}
              />
              <div className="resume-metadata">
                <small>
                  Last updated: {new Date(seasonResume.updated_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </small>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
