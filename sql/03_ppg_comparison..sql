
USE premier_league_analysis;

CREATE OR REPLACE VIEW season_group_ppg AS

SELECT
    Season,
    PerformanceGroup,

    COUNT(*) AS Clubs,
    SUM(Points) AS TotalPoints,
    SUM(Played) AS TotalMatches,

    SUM(Points) / SUM(Played) AS PPG

FROM league_table

GROUP BY Season, PerformanceGroup;

SELECT *
FROM season_group_ppg
ORDER BY Season, PerformanceGroup;


WITH periods AS (
    SELECT
        CASE
            WHEN LEFT(Season, 4) BETWEEN '2010' AND '2014'
                THEN 'Earlier'
            WHEN LEFT(Season, 4) BETWEEN '2021' AND '2025'
                THEN 'Recent'
            ELSE NULL
        END AS Period,
        PerformanceGroup,
        PPG
    FROM season_group_ppg
),

comparison AS (
    SELECT
        PerformanceGroup,

        AVG(CASE
            WHEN Period = 'Earlier' THEN PPG
        END) AS EarlierPPG,

        AVG(CASE
            WHEN Period = 'Recent' THEN PPG
        END) AS RecentPPG

    FROM periods
    WHERE Period IS NOT NULL
    GROUP BY PerformanceGroup
)

SELECT
    PerformanceGroup,
    ROUND(EarlierPPG, 3) AS EarlierPPG,
    ROUND(RecentPPG, 3) AS RecentPPG,
    ROUND(RecentPPG - EarlierPPG, 3) AS ChangePPG
FROM comparison
ORDER BY FIELD(
    PerformanceGroup,
    'Top five',
    'Middle ten',
    'Bottom five'
);


WITH season_gaps AS (
    SELECT
        Season,

        MAX(CASE
            WHEN PerformanceGroup = 'Top five'
            THEN PPG
        END)
        -
        MAX(CASE
            WHEN PerformanceGroup = 'Bottom five'
            THEN PPG
        END) AS PPGGap

    FROM season_group_ppg
    GROUP BY Season
),

period_gaps AS (
    SELECT
        CASE
            WHEN LEFT(Season, 4) BETWEEN '2010' AND '2014'
                THEN 'Earlier'
            WHEN LEFT(Season, 4) BETWEEN '2021' AND '2025'
                THEN 'Recent'
            ELSE NULL
        END AS Period,
        PPGGap
    FROM season_gaps
)

SELECT
    ROUND(AVG(CASE WHEN Period = 'Earlier'
        THEN PPGGap END), 3) AS EarlierGap,

    ROUND(AVG(CASE WHEN Period = 'Recent'
        THEN PPGGap END), 3) AS RecentGap,

    ROUND(
        AVG(CASE WHEN Period = 'Recent' THEN PPGGap END)
        -
        AVG(CASE WHEN Period = 'Earlier' THEN PPGGap END),
        3
    ) AS GapChange

FROM period_gaps;






