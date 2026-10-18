
USE premier_league_analysis;

SELECT
    Season,
    PerformanceRank,
    Team,
    Played,
    GoalsFor,
    GoalsAgainst,
    Points
FROM league_table
WHERE Season = '2025/26'
    AND Team IN ('Arsenal', 'Man City')
ORDER BY PerformanceRank;
