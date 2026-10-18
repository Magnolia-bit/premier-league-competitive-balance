
USE premier_league_analysis;

CREATE OR REPLACE VIEW team_matches_grouped AS

SELECT
    tm.Season,
    tm.MatchID,
    tm.Team,
    tm.Opponent,
    tm.Venue,
    tm.GoalsFor,
    tm.GoalsAgainst,
    tm.Result,
    tm.Points,

    own.PerformanceGroup AS TeamGroup,
    opp.PerformanceGroup AS OpponentGroup

FROM team_matches AS tm

-- Find the team's own performance group
JOIN league_table AS own
    ON tm.Season = own.Season
    AND tm.Team = own.Team

-- Find the opponent's performance group
JOIN league_table AS opp
    ON tm.Season = opp.Season
    AND tm.Opponent = opp.Team;


SELECT
    COUNT(*) AS TotalTeamMatches,
    SUM(CASE
        WHEN TeamGroup = 'Bottom five'
        THEN 1 ELSE 0
    END) AS BottomFiveMatches
FROM team_matches_grouped;


CREATE OR REPLACE VIEW bottom_opponent_contributions AS

WITH selected_matches AS (
    SELECT
        CASE
            WHEN LEFT(Season, 4) BETWEEN '2010' AND '2014'
                THEN 'Earlier'
            WHEN LEFT(Season, 4) BETWEEN '2021' AND '2025'
                THEN 'Recent'
        END AS Period,
        OpponentGroup,
        Points
    FROM team_matches_grouped
    WHERE TeamGroup = 'Bottom five'
),

period_stats AS (
    SELECT
        Period,
        OpponentGroup,
        COUNT(*) AS Matches,
        SUM(Points) / COUNT(*) AS PPG
    FROM selected_matches
    WHERE Period IS NOT NULL
    GROUP BY Period, OpponentGroup
),

comparison AS (
    SELECT
        OpponentGroup,

        MAX(CASE WHEN Period = 'Earlier'
            THEN Matches END) AS EarlierMatches,

        MAX(CASE WHEN Period = 'Recent'
            THEN Matches END) AS RecentMatches,

        MAX(CASE WHEN Period = 'Earlier'
            THEN PPG END) AS EarlierPPG,

        MAX(CASE WHEN Period = 'Recent'
            THEN PPG END) AS RecentPPG

    FROM period_stats
    GROUP BY OpponentGroup
)

SELECT
    OpponentGroup,
    EarlierMatches,
    RecentMatches,
    EarlierPPG,
    RecentPPG,

    RecentPPG - EarlierPPG AS PPGChange,

    EarlierMatches /
        SUM(EarlierMatches) OVER () AS Weight,

    (RecentPPG - EarlierPPG)
        * (
            EarlierMatches /
            SUM(EarlierMatches) OVER ()
        ) AS Contribution

FROM comparison;


SELECT
    OpponentGroup,
    EarlierMatches,
    RecentMatches,
    ROUND(EarlierPPG, 3) AS EarlierPPG,
    ROUND(RecentPPG, 3) AS RecentPPG,
    ROUND(PPGChange, 3) AS PPGChange,
    ROUND(Weight, 3) AS Weight,
    ROUND(Contribution, 4) AS Contribution

FROM bottom_opponent_contributions

ORDER BY FIELD(
    OpponentGroup,
    'Top five',
    'Middle ten',
    'Bottom five'
);

SELECT
    ROUND(SUM(Contribution), 6)
        AS TotalBottomFivePPGChange
FROM bottom_opponent_contributions;

