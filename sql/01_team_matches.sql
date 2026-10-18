
USE premier_league_analysis;

CREATE OR REPLACE VIEW team_matches AS

-- Home team's perspective
SELECT
    Season,
    MatchID,
    HomeTeam AS Team,
    AwayTeam AS Opponent,
    'Home' AS Venue,
    FTHG AS GoalsFor,
    FTAG AS GoalsAgainst,

    CASE
        WHEN FTHG > FTAG THEN 'W'
        WHEN FTHG = FTAG THEN 'D'
        ELSE 'L'
    END AS Result,

    CASE
        WHEN FTHG > FTAG THEN 3
        WHEN FTHG = FTAG THEN 1
        ELSE 0
    END AS Points

FROM fixtures

UNION ALL

-- Away team's perspective
SELECT
    Season,
    MatchID,
    AwayTeam AS Team,
    HomeTeam AS Opponent,
    'Away' AS Venue,
    FTAG AS GoalsFor,
    FTHG AS GoalsAgainst,

    CASE
        WHEN FTAG > FTHG THEN 'W'
        WHEN FTAG = FTHG THEN 'D'
        ELSE 'L'
    END AS Result,

    CASE
        WHEN FTAG > FTHG THEN 3
        WHEN FTAG = FTHG THEN 1
        ELSE 0
    END AS Points

FROM fixtures;


SELECT
    COUNT(*) AS TotalTeamMatches,
    COUNT(DISTINCT Season) AS TotalSeasons,
    COUNT(DISTINCT Season, Team) AS TeamSeasons
FROM team_matches;


SELECT
    Season,
    Team,
    COUNT(*) AS MatchesPlayed
FROM team_matches
GROUP BY Season, Team
HAVING COUNT(*) <> 38;


