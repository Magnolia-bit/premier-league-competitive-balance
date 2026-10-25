from pathlib import Path
import pandas as pd

# Find the CSV beside this Python script.
csv_path = Path(__file__).parent / "10-11 original.csv"

def analyse_season(file_path, season):

    # Load the data without changing the original file.
    matches = pd.read_csv(file_path)

    empty_rows = matches.isna().all(axis=1)
    print("Fully empty rows excluded:", empty_rows.sum())

    matches = matches.loc[~empty_rows].copy()

    # Inspect the first five matches and the dataset size.
    print(matches.head())
    print("Number of rows:", len(matches))
    print("Column names:", matches.columns.tolist())


    # Count the distinct clubs appearing at home or away.
    teams = pd.concat([matches["HomeTeam"], matches["AwayTeam"]])
    print("Number of teams:", teams.nunique())

    # Check for missing values in the fields we need.
    required_columns = [
        "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"
    ]
    print("Missing values:")
    print(matches[required_columns].isna().sum())

    # Check for repeated home-versus-away fixtures.
    duplicates = matches.duplicated(subset=["HomeTeam", "AwayTeam"])
    print("Duplicate fixtures:", duplicates.sum())


    # Work out the result independently from the goals.
    expected_result = pd.Series("D", index=matches.index)

    expected_result.loc[matches["FTHG"] > matches["FTAG"]] = "H"
    expected_result.loc[matches["FTHG"] < matches["FTAG"]] = "A"

    # Find matches where the recorded result disagrees.
    mismatches = matches["FTR"] != expected_result

    print("Score/result mismatches:", mismatches.sum())
    print(matches.loc[mismatches, required_columns])

    home_counts = matches["HomeTeam"].value_counts()
    away_counts = matches["AwayTeam"].value_counts()

    fixture_counts = pd.DataFrame({
        "Home": home_counts,
        "Away": away_counts
    })

    fixture_counts["Total"] = fixture_counts["Home"] + fixture_counts["Away"]

    print(fixture_counts)

    goals = matches[["FTHG", "FTAG"]]

    invalid_goals = (
        goals.isna()
        | (goals < 0)
        | (goals % 1 != 0)
    ).any(axis=1)

    print("Matches with invalid goals:", invalid_goals.sum())
    print(matches.loc[invalid_goals, required_columns])

    # Parse day-first dates; unreadable values become NaT (missing dates).
    parsed_dates = pd.to_datetime(
        matches["Date"],
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )

    # Use a broad July–June window for the 2010/11 season.
    start_year = int(season.split("/")[0])
    start_date = f"{start_year}-07-01"
    end_date = f"{start_year + 1}-06-30"

    if season == "2019/20":
        end_date = "2020-07-31"

    invalid_dates = (
        parsed_dates.isna()
        | ~parsed_dates.between(start_date, end_date)
    )
    
    print("Invalid or out-of-season dates:", invalid_dates.sum())
    print(matches.loc[invalid_dates, required_columns])

    print("Earliest match:", parsed_dates.min())
    print("Latest match:", parsed_dates.max())

    # A club cannot be its own opponent.
    same_team = matches["HomeTeam"] == matches["AwayTeam"]

    print("Matches with identical opponents:", same_team.sum())
    print(matches.loc[same_team, required_columns])
    
        # Critical validation checks
    checks = {
        "380 fixtures": len(matches) == 380,
        "20 clubs": teams.nunique() == 20,
        "No missing required values":
            not matches[required_columns].isna().any().any(),
        "No duplicate fixtures": not duplicates.any(),
        "Scores match recorded results": not mismatches.any(),
        "Valid goal values": not invalid_goals.any(),
        "Valid fixture dates": not invalid_dates.any(),
        "No identical opponents": not same_team.any(),
        "19 home matches per club":
            home_counts.reindex(teams.unique(), fill_value=0).eq(19).all(),
        "19 away matches per club":
            away_counts.reindex(teams.unique(), fill_value=0).eq(19).all(),
    }

    failed_checks = [
        name for name, passed in checks.items()
        if not passed
    ]

    if failed_checks:
        raise ValueError(
            f"{season}: validation failed: "
            + ", ".join(failed_checks)
        )

    print(f"{season}: all critical source checks passed")

    # Preserve cleaned fixture-level data for SQL.
    fixtures = matches[required_columns].copy()

    # Keep the original source-row identity.
    fixtures.insert(0, "MatchID", matches.index)
    fixtures.insert(0, "Season", season)

    # Preserve a consistently parsed date.
    fixtures["MatchDate"] = parsed_dates

# Each match from the home team's perspective.
    home = matches[["HomeTeam", "AwayTeam", "FTHG", "FTAG"]].copy()
    home.columns = ["Team", "Opponent", "GF", "GA"]
    home["Venue"] = "Home"

    # The same match from the away team's perspective.
    away = matches[["AwayTeam", "HomeTeam", "FTAG", "FTHG"]].copy()
    away.columns = ["Team", "Opponent", "GF", "GA"]
    away["Venue"] = "Away"

    # Combine both perspectives, keeping the original match row as an identifier.
    team_matches = pd.concat(
        [home, away], axis=0
    ).rename_axis("MatchID").reset_index()

    team_matches["Season"] = season

    print(team_matches.head())
    print("Team-match rows:", len(team_matches))

    # Compare each team's goals with its opponent's goals.
    team_matches["Win"] = (
        team_matches["GF"] > team_matches["GA"]
    ).astype(int)

    team_matches["Draw"] = (
        team_matches["GF"] == team_matches["GA"]
    ).astype(int)

    team_matches["Loss"] = (
        team_matches["GF"] < team_matches["GA"]
    ).astype(int)

    # Three points for a win, one for a draw.
    team_matches["Points"] = (
        3 * team_matches["Win"] + team_matches["Draw"]
    )

    print(
        team_matches[
            ["Team", "Opponent", "GF", "GA", "Win", "Draw", "Loss", "Points"]
        ].head(10)
    )

    # Group the match records by season and team, then calculate totals.
    league_table = team_matches.groupby(["Season", "Team"]).agg(
        Played=("MatchID", "count"),
        Wins=("Win", "sum"),
        Draws=("Draw", "sum"),
        Losses=("Loss", "sum"),
        GF=("GF", "sum"),
        GA=("GA", "sum"),
        Points=("Points", "sum")
    ).reset_index()

    # Calculate goal difference and points per game.
    league_table["GD"] = league_table["GF"] - league_table["GA"]
    league_table["PPG"] = league_table["Points"] / league_table["Played"]

    # Order clubs by points, then goal difference, then goals scored.
    league_table = league_table.sort_values(
        ["Season", "Points", "GD", "GF"],
        ascending=[True, False, False, False]
    ).reset_index(drop=True)

    print(league_table.to_string(index=False))

    # Every match must count as a win, draw or loss for each team.
    print(
        "Played totals correct:",
        (
            league_table["Played"]
            == league_table["Wins"]
            + league_table["Draws"]
            + league_table["Losses"]
        ).all()
    )

    # Every goal scored is also a goal conceded by an opponent.
    print(
        "Goals balance:",
        league_table["GF"].sum() == league_table["GA"].sum()
    )

    # Every winning team has a corresponding losing team.
    print(
        "Wins and losses balance:",
        league_table["Wins"].sum() == league_table["Losses"].sum()
    )

    # A decisive match awards 3 points in total; a draw awards 2.
    expected_total_points = 3 * len(matches) - (matches["FTR"] == "D").sum()

    print(
        "Total points correct:",
        league_table["Points"].sum() == expected_total_points
    )

    print(
        league_table[
            ["Team", "Played", "Wins", "Draws", "Losses", "GF", "GA", "GD", "Points"]
        ].to_string(index=False)
    )

    # Number teams in their existing sorted order within each season.
    league_table["PerformanceRank"] = (
        league_table.groupby("Season").cumcount() + 1
    )

    # Start with the middle group, then identify the top and bottom five.
    league_table["Group"] = "Middle ten"

    league_table.loc[
        league_table["PerformanceRank"] <= 5, "Group"
    ] = "Top five"

    league_table.loc[
        league_table["PerformanceRank"] >= 16, "Group"
    ] = "Bottom five"

    print(
        league_table[
            ["PerformanceRank", "Team", "Points", "PPG", "Group"]
        ].to_string(index=False)
    )

    print(league_table["Group"].value_counts())

    group_summary = league_table.groupby(["Season", "Group"]).agg(
        Teams=("Team", "count"),
        AveragePoints=("Points", "mean"),
        TotalPoints=("Points", "sum"),
        TotalPlayed=("Played", "sum")
    ).reset_index()

    group_summary["PPG"] = (
        group_summary["TotalPoints"] / group_summary["TotalPlayed"]
    )

    print(group_summary.round(3).to_string(index=False))

    # Put each group's PPG into its own column, with one row per season.
    season_comparison = group_summary.pivot(
        index="Season",
        columns="Group",
        values="PPG"
    )

    # Calculate the difference between the top and bottom groups.
    season_comparison["PPG_Gap"] = (
        season_comparison["Top five"]
        - season_comparison["Bottom five"]
    )

    print(season_comparison.round(3).to_string())

    # Create a lookup containing each team's group for the season.
    group_lookup = league_table[["Season", "Team", "Group"]]

    # Add the team's own group.
    team_matches_grouped = team_matches.merge(
        group_lookup,
        on=["Season", "Team"],
        how="left",
        validate="many_to_one"
    )

    # Rename the lookup columns so we can also match opponents.
    opponent_lookup = group_lookup.rename(
        columns={
            "Team": "Opponent",
            "Group": "OpponentGroup"
        }
    )

    # Add the opponent's group.
    team_matches_grouped = team_matches_grouped.merge(
        opponent_lookup,
        on=["Season", "Opponent"],
        how="left",
        validate="many_to_one"
    )

    print(
        team_matches_grouped[
            ["Team", "Group", "Opponent", "OpponentGroup", "Points"]
        ].head(10).to_string(index=False)
    )

    print(
        "Missing group labels:",
        team_matches_grouped[["Group", "OpponentGroup"]].isna().sum()
    )

    # Select bottom-five teams playing against top-five opponents.
    bottom_vs_top = team_matches_grouped.loc[
        (team_matches_grouped["Group"] == "Bottom five")
        & (team_matches_grouped["OpponentGroup"] == "Top five")
    ].copy()

    # Summarise those encounters by season.
    head_to_head_summary = bottom_vs_top.groupby("Season").agg(
        Matches=("MatchID", "count"),
        Wins=("Win", "sum"),
        Draws=("Draw", "sum"),
        Losses=("Loss", "sum"),
        Points=("Points", "sum"),
        GF=("GF", "sum"),
        GA=("GA", "sum")
    )

    head_to_head_summary["PPG"] = (
        head_to_head_summary["Points"]
        / head_to_head_summary["Matches"]
    )

    print(head_to_head_summary.round(3).to_string())

    # Summarise from the bottom-five team's home or away perspective.
    venue_summary = bottom_vs_top.groupby(["Season", "Venue"]).agg(
        Matches=("MatchID", "count"),
        Wins=("Win", "sum"),
        Draws=("Draw", "sum"),
        Losses=("Loss", "sum"),
        Points=("Points", "sum"),
        GF=("GF", "sum"),
        GA=("GA", "sum")
    )

    venue_summary["PPG"] = (
        venue_summary["Points"] / venue_summary["Matches"]
    )

    venue_summary["GoalDifferencePerGame"] = (
        (venue_summary["GF"] - venue_summary["GA"])
        / venue_summary["Matches"]
    )

    print(venue_summary.round(3).to_string())

    validation = pd.DataFrame([{
        "Season": season,
        "Matches": len(matches),
        "Teams": teams.nunique(),
        "MissingValues": matches[required_columns].isna().sum().sum(),
        "DuplicateFixtures": duplicates.sum(),
        "ScoreResultMismatches": mismatches.sum(),
        "InvalidGoals": invalid_goals.sum(),
        "InvalidDates": invalid_dates.sum(),
        "IdenticalOpponents": same_team.sum()
    }])

    return {
        "fixtures": fixtures,
        "validation": validation,
        "league_table": league_table,
        "group_summary": group_summary,
        "season_comparison": season_comparison.reset_index(),
        "head_to_head_summary": head_to_head_summary.reset_index(),
        "venue_summary": venue_summary.reset_index(),
        "team_matches": team_matches_grouped
    }

folder = Path(__file__).parent
season_results = []

for year in range(2010, 2026):
    start = str(year)[-2:]
    end = str(year + 1)[-2:]

    csv_path = folder / f"{start}-{end} original.csv"
    season = f"{year}/{end}"

    print(f"\n========== {season} ==========")

    result = analyse_season(csv_path, season)
    season_results.append(result)

# Combine each type of table across all seasons.
combined = {
    name: pd.concat(
        [result[name] for result in season_results],
        ignore_index=True
    )
    for name in season_results[0]
}

comparison = combined["season_comparison"].copy()

comparison["StartYear"] = (
    comparison["Season"].str[:4].astype(int)
)

metrics = [
    "Top five",
    "Middle ten",
    "Bottom five",
    "PPG_Gap"
]

earlier = comparison.loc[
    comparison["StartYear"].between(2010, 2014),
    metrics
].mean()

recent = comparison.loc[
    comparison["StartYear"].between(2021, 2025),
    metrics
].mean()

window_comparison = pd.DataFrame({
    "Earlier": earlier,
    "Recent": recent
})

window_comparison["Change"] = (
    window_comparison["Recent"]
    - window_comparison["Earlier"]
)

window_comparison = (
    window_comparison
    .rename_axis("Metric")
    .reset_index()
)

combined["window_comparison"] = window_comparison

print(window_comparison.round(3))


# CHANGE 5: Bottom-five performance by opponent group

# Select every bottom-five team-match record.
bottom = combined["team_matches"].loc[
    combined["team_matches"]["Group"] == "Bottom five"
].copy()

bottom["StartYear"] = bottom["Season"].str[:4].astype(int)


# Calculate PPG against each opponent group in a given period.
def opponent_summary(start_year, end_year):
    selected = bottom.loc[
        bottom["StartYear"].between(start_year, end_year)
    ]

    summary = selected.groupby("OpponentGroup").agg(
        Matches=("Points", "size"),
        Points=("Points", "sum")
    )

    summary["PPG"] = summary["Points"] / summary["Matches"]

    return summary


# Compare the same five-season windows as the main analysis.
early = opponent_summary(2010, 2014)
recent = opponent_summary(2021, 2025)

opponent_comparison = pd.DataFrame({
    "EarlierMatches": early["Matches"],
    "RecentMatches": recent["Matches"],
    "EarlierPPG": early["PPG"],
    "RecentPPG": recent["PPG"]
})

# Check that the number of encounters is consistent.
if not (
    opponent_comparison["EarlierMatches"]
    == opponent_comparison["RecentMatches"]
).all():
    raise ValueError("Opponent-group match counts differ")


# Calculate the change in performance.
opponent_comparison["PPGChange"] = (
    opponent_comparison["RecentPPG"]
    - opponent_comparison["EarlierPPG"]
)

# Weight each group by its share of bottom-five matches.
total_matches = opponent_comparison["EarlierMatches"].sum()

if total_matches != 950:
    raise ValueError("Expected 950 bottom-five team appearances")

opponent_comparison["Weight"] = (
    opponent_comparison["EarlierMatches"] / total_matches
)

# Calculate each group's contribution to overall PPG change.
opponent_comparison["Contribution"] = (
    opponent_comparison["PPGChange"]
    * opponent_comparison["Weight"]
)

# Check against the main bottom-five PPG change.
expected_change = window_comparison.loc[
    window_comparison["Metric"] == "Bottom five",
    "Change"
].iloc[0]

actual_change = opponent_comparison["Contribution"].sum()

if abs(actual_change - expected_change) > 1e-10:
    raise ValueError("Opponent contributions do not reconcile")


opponent_comparison = (
    opponent_comparison
    .rename_axis("OpponentGroup")
    .reset_index()
)

combined["bottom_opponent_comparison"] = opponent_comparison

print("\n========== BOTTOM-FIVE OPPONENT ANALYSIS ==========")
print(opponent_comparison.round(3).to_string(index=False))


print("\n========== ALL-SEASON COMPARISON ==========")
print(combined["season_comparison"].round(3).to_string(index=False))

results_folder = folder / "results"
results_folder.mkdir(exist_ok=True)

for name, table in combined.items():
    output_path = results_folder / f"{name}.csv"
    table.to_csv(output_path, index=False)
    print("Saved:", output_path.name)



print("Team-match rows:", len(combined["team_matches"]))