
import pandas as pd
import numpy as np
from pathlib import Path

# Load the verified fixture dataset
folder = Path(__file__).parent
fixtures = pd.read_csv(folder / "results" / "fixtures.csv")

# Construct home and away team perspectives
home = fixtures[
    ["Season", "HomeTeam", "FTHG", "FTAG"]
].copy()

home.columns = ["Season", "Team", "GF", "GA"]

away = fixtures[
    ["Season", "AwayTeam", "FTAG", "FTHG"]
].copy()

away.columns = ["Season", "Team", "GF", "GA"]

team_matches = pd.concat([home, away], ignore_index=True)

# Calculate points independently from goals
team_matches["Points"] = np.select(
    [
        team_matches["GF"] > team_matches["GA"],
        team_matches["GF"] == team_matches["GA"]
    ],
    [3, 1],
    default=0
)

# Reconstruct season-level league tables
league = team_matches.groupby(
    ["Season", "Team"], as_index=False
).agg(
    Played=("Points", "size"),
    Points=("Points", "sum"),
    GF=("GF", "sum"),
    GA=("GA", "sum")
)

league["GD"] = league["GF"] - league["GA"]

league = league.sort_values(
    ["Season", "Points", "GD", "GF", "Team"],
    ascending=[True, False, False, False, True]
)

league["Position"] = league.groupby(
    "Season"
).cumcount() + 1

# Verify basic league structure
assert len(league) == 320
assert league["Played"].eq(38).all()

# Compare alternative group boundaries
results = []

for group_size in [5, 4]:

    selected = league.loc[
        (league["Position"] <= group_size) |
        (league["Position"] > 20 - group_size)
    ].copy()

    selected["Group"] = np.where(
        selected["Position"] <= group_size,
        "Top",
        "Bottom"
    )

    season_ppg = selected.groupby(
        ["Season", "Group"], as_index=False
    ).agg(
        Points=("Points", "sum"),
        Played=("Played", "sum")
    )

    season_ppg["PPG"] = (
        season_ppg["Points"] / season_ppg["Played"]
    )

    season_ppg["Year"] = (
        season_ppg["Season"].str[:4].astype(int)
    )

    earlier = season_ppg.loc[
        season_ppg["Year"].between(2010, 2014)
    ].groupby("Group")["PPG"].mean()

    recent = season_ppg.loc[
        season_ppg["Year"].between(2021, 2025)
    ].groupby("Group")["PPG"].mean()

    earlier_gap = earlier["Top"] - earlier["Bottom"]
    recent_gap = recent["Top"] - recent["Bottom"]

    results.append({
        "Grouping": f"Top {group_size} / Bottom {group_size}",
        "EarlierGap": earlier_gap,
        "RecentGap": recent_gap,
        "GapChange": recent_gap - earlier_gap
    })

comparison = pd.DataFrame(results)

print("\nSENSITIVITY TEST: GROUP BOUNDARIES")
print(comparison.round(4).to_string(index=False))

# Confirm the original result has been reproduced
original_change = comparison.loc[
    comparison["Grouping"] == "Top 5 / Bottom 5",
    "GapChange"
].iloc[0]

if abs(original_change - 0.115) > 0.002:
    raise ValueError("Original gap change does not reconcile")

# Export for Tableau and documentation
comparison.to_csv(
    folder / "results" / "sensitivity_group_boundaries.csv",
    index=False
)

print("\nSensitivity comparison exported successfully.")

print("\nSensitivity comparison exported successfully.")


# SENSITIVITY TEST 2: League-wide PPG dispersion

# Calculate each club's unrounded PPG
league["PPG"] = league["Points"] / league["Played"]

# Calculate population standard deviation across 20 clubs
dispersion = (
    league.groupby("Season")
    .agg(
        SD_PPG=("PPG", lambda x: x.std(ddof=0))
    )
    .reset_index()
)

dispersion["StartYear"] = (
    dispersion["Season"].str[:4].astype(int)
)

# Compare the two predefined five-season periods
earlier_sd = dispersion.loc[
    dispersion["StartYear"].between(2010, 2014),
    "SD_PPG"
].mean()

recent_sd = dispersion.loc[
    dispersion["StartYear"].between(2021, 2025),
    "SD_PPG"
].mean()

print("\nSENSITIVITY TEST 2: PPG DISPERSION")
print(f"Earlier SD: {earlier_sd:.4f}")
print(f"Recent SD:  {recent_sd:.4f}")
print(f"Change:     {recent_sd - earlier_sd:+.4f}")

# Save annual values for Tableau
dispersion.to_csv(
    folder / "results" / "sensitivity_ppg_dispersion.csv",
    index=False
)


# TEST 3: HOME VS AWAY BY OPPONENT GROUP

# Reconstruct fixture perspectives with opponent and venue
home_side = fixtures[
    ["Season", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
].rename(columns={
    "HomeTeam": "Team",
    "AwayTeam": "Opponent",
    "FTHG": "GF",
    "FTAG": "GA"
})
home_side["Venue"] = "Home"

away_side = fixtures[
    ["Season", "AwayTeam", "HomeTeam", "FTAG", "FTHG"]
].rename(columns={
    "AwayTeam": "Team",
    "HomeTeam": "Opponent",
    "FTAG": "GF",
    "FTHG": "GA"
})
away_side["Venue"] = "Away"

venue_matches = pd.concat(
    [home_side, away_side], ignore_index=True
)

venue_matches["Points"] = np.select(
    [
        venue_matches["GF"] > venue_matches["GA"],
        venue_matches["GF"] == venue_matches["GA"]
    ],
    [3, 1],
    default=0
)

# Assign each club its current-season performance group
groups = league[["Season", "Team", "Position"]].copy()

groups["Group"] = np.select(
    [groups["Position"] <= 5, groups["Position"] >= 16],
    ["Top five", "Bottom five"],
    default="Middle ten"
)

venue_matches = venue_matches.merge(
    groups[["Season", "Team", "Group"]].rename(
        columns={"Group": "TeamGroup"}
    ),
    on=["Season", "Team"],
    validate="many_to_one"
)

venue_matches = venue_matches.merge(
    groups[["Season", "Team", "Group"]].rename(
        columns={
            "Team": "Opponent",
            "Group": "OpponentGroup"
        }
    ),
    on=["Season", "Opponent"],
    validate="many_to_one"
)

assert len(venue_matches) == 12160

# Select bottom-five matches in the comparison windows
bottom_venue = venue_matches.loc[
    venue_matches["TeamGroup"] == "Bottom five"
].copy()

bottom_venue["Year"] = (
    bottom_venue["Season"].str[:4].astype(int)
)

bottom_venue = bottom_venue.loc[
    bottom_venue["Year"].between(2010, 2014)
    | bottom_venue["Year"].between(2021, 2025)
].copy()

bottom_venue["Period"] = np.where(
    bottom_venue["Year"].between(2010, 2014),
    "Earlier",
    "Recent"
)

# Check expected home/away appearances in each window
assert bottom_venue.groupby(
    ["Period", "Venue"]
).size().eq(475).all()

venue_summary = bottom_venue.groupby(
    ["OpponentGroup", "Venue", "Period"]
).agg(
    Matches=("Points", "size"),
    PPG=("Points", "mean")
).reset_index()

venue_comparison = venue_summary.pivot(
    index=["OpponentGroup", "Venue"],
    columns="Period",
    values="PPG"
).reset_index()

venue_comparison.columns.name = None

venue_comparison["Change"] = (
    venue_comparison["Recent"]
    - venue_comparison["Earlier"]
)

print("\nTEST 3: HOME VS AWAY BY OPPONENT GROUP")
print(venue_comparison.round(3).to_string(index=False))

venue_comparison.to_csv(
    folder / "results" / "sensitivity_home_away.csv",
    index=False
)


# TEST 4: PANDEMIC-SEASON EXCLUSION

# Calculate the annual top-five/bottom-five PPG gap
gap_teams = league.loc[
    (league["Position"] <= 5)
    | (league["Position"] >= 16)
].copy()

gap_teams["Group"] = np.where(
    gap_teams["Position"] <= 5,
    "Top",
    "Bottom"
)

annual_gap = (
    gap_teams.groupby(["Season", "Group"])["PPG"]
    .mean()
    .unstack()
)

annual_gap["PPGGap"] = (
    annual_gap["Top"] - annual_gap["Bottom"]
)

annual_gap = annual_gap.reset_index()

# Combine with the annual standard deviation
annual = annual_gap[
    ["Season", "PPGGap"]
].merge(
    dispersion[["Season", "SD_PPG"]],
    on="Season",
    validate="one_to_one"
)

annual["Year"] = annual["Season"].str[:4].astype(int)

# Exclude 2019/20 and 2020/21
without_pandemic = annual.loc[
    ~annual["Year"].isin([2019, 2020])
].copy()

assert len(annual) == 16
assert len(without_pandemic) == 14

# Calculate a linear trend slope for each sample
def trend_slope(data, metric):
    return np.polyfit(
        data["Year"],
        data[metric],
        1
    )[0]

results = []

for metric in ["PPGGap", "SD_PPG"]:
    for label, data in [
        ("All seasons", annual),
        ("Excluding pandemic", without_pandemic)
    ]:
        results.append({
            "Metric": metric,
            "Sample": label,
            "Seasons": len(data),
            "SlopePerSeason": trend_slope(data, metric)
        })

pandemic_test = pd.DataFrame(results)

print("\nTEST 4: PANDEMIC EXCLUSION")
print(pandemic_test.round(5).to_string(index=False))

pandemic_test.to_csv(
    folder / "results" / "sensitivity_pandemic_trend.csv",
    index=False
)


# TEST 5: OFFICIAL POINTS-DEDUCTION SENSITIVITY

official = league.copy()
official["Deduction"] = 0

# Identify the exact Forest name used in our dataset
forest = official.loc[
    (official["Season"] == "2023/24")
    & official["Team"].str.contains(
        "Forest", case=False, regex=False
    ),
    "Team"
]

assert len(forest) == 1
forest_name = forest.iloc[0]

deductions = {
    "Everton": 8,
    forest_name: 4
}

for team, points in deductions.items():
    mask = (
        (official["Season"] == "2023/24")
        & (official["Team"] == team)
    )
    assert mask.sum() == 1
    official.loc[mask, "Deduction"] = points

# Keep earned points separate from adjusted points
official["OfficialPoints"] = (
    official["Points"] - official["Deduction"]
)

# Recalculate rankings using adjusted points
official = official.sort_values(
    ["Season", "OfficialPoints", "GD", "GF", "Team"],
    ascending=[True, False, False, False, True]
)

official["OfficialPosition"] = (
    official.groupby("Season").cumcount() + 1
)

def performance_group(position):
    return np.select(
        [position <= 5, position >= 16],
        ["Top five", "Bottom five"],
        default="Middle ten"
    )

official["OriginalGroup"] = performance_group(
    official["Position"]
)

official["OfficialGroup"] = performance_group(
    official["OfficialPosition"]
)

# Identify changes to our performance groups
changes = official.loc[
    official["OriginalGroup"] != official["OfficialGroup"]
]

print("\nTEST 5: OFFICIAL POINTS DEDUCTIONS")
print(
    official.loc[
        official["Season"] == "2023/24",
        [
            "Team", "Points", "Deduction",
            "OfficialPoints", "Position",
            "OfficialPosition", "OriginalGroup",
            "OfficialGroup"
        ]
    ].sort_values("OfficialPosition").to_string(index=False)
)

print("\nClubs changing performance group:")
if changes.empty:
    print("None")
else:
    print(changes.to_string(index=False))

official.to_csv(
    folder / "results" / "sensitivity_points_deductions.csv",
    index=False
)