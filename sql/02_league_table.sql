
USE premier_league_analysis;

CREATE OR REPLACE VIEW league_table AS

-- Step 1: Aggregate each club's season results
WITH team_totals AS (
    SELECT
        Season,
        Team,
        COUNT(*) AS Played,

        SUM(CASE WHEN Result = 'W' THEN 1 ELSE 0 END) AS Wins,
        SUM(CASE WHEN Result = 'D' THEN 1 ELSE 0 END) AS Draws,
        SUM(CASE WHEN Result = 'L' THEN 1 ELSE 0 END) AS Losses,

        SUM(GoalsFor) AS GoalsFor,
        SUM(GoalsAgainst) AS GoalsAgainst,

        SUM(GoalsFor) - SUM(GoalsAgainst) AS GoalDifference,

        SUM(Points) AS Points,

        ROUND(SUM(Points) / COUNT(*), 4) AS PPG

    FROM team_matches
    GROUP BY Season, Team
),

-- Step 2: Rank clubs within each season
ranked_teams AS (
    SELECT
        team_totals.*,

        ROW_NUMBER() OVER (
            PARTITION BY Season
            ORDER BY
                Points DESC,
                GoalDifference DESC,
                GoalsFor DESC,
                Team ASC
        ) AS PerformanceRank

    FROM team_totals
)

-- Step 3: Assign performance groups
SELECT
    ranked_teams.*,

    CASE
        WHEN PerformanceRank <= 5 THEN 'Top five'
        WHEN PerformanceRank >= 16 THEN 'Bottom five'
        ELSE 'Middle ten'
    END AS PerformanceGroup

FROM ranked_teams;


SELECT
    PerformanceRank,
    Team,
    Played,
    Wins,
    Draws,
    Losses,
    GoalsFor,
    GoalsAgainst,
    GoalDifference,
    Points,
    PPG,
    PerformanceGroup
FROM league_table
WHERE Season = '2025/26'
ORDER BY PerformanceRank;


SELECT
    Season,
    COUNT(*) AS Clubs,
    SUM(Played) AS TeamAppearances,
    SUM(CASE WHEN PerformanceGroup = 'Top five'
        THEN 1 ELSE 0 END) AS TopFive,
    SUM(CASE WHEN PerformanceGroup = 'Middle ten'
        THEN 1 ELSE 0 END) AS MiddleTen,
    SUM(CASE WHEN PerformanceGroup = 'Bottom five'
        THEN 1 ELSE 0 END) AS BottomFive
FROM league_table
GROUP BY Season
ORDER BY Season;


