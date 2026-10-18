![Premier League Competitive Balance Dashboard](images/dashboard-preview.png)

# Premier League Competitive Balance Analysis

**An end-to-end sports analytics project using Python, SQL and Tableau | 2010/11–2025/26**

[**View Interactive Tableau Dashboard**](https://public.tableau.com/app/profile/cameron.sullivan.davis/viz/Premier_League_Competitive_Balance/Dashboard1)

## Project Overview

Has the Premier League become less competitive, and if so, which teams are driving the change?

This project investigates competitive balance across 16 Premier League seasons (2010/11–2025/26), analysing 6,080 matches to understand how performance differences between teams have evolved.

Rather than relying solely on league tables or championship outcomes, the analysis examines points per game (PPG), opponent-level performance, home and away results, alternative team groupings and league-wide performance dispersion.

The objective was to develop a reproducible analytical workflow, test whether the initial findings were robust, and communicate the results through an interactive Tableau dashboard.

## Key Findings

**1. The gap between the strongest and weakest teams has widened.**

The average PPG difference between top-five and bottom-five teams increased from 1.082 in 2010/11–2014/15 to 1.197 in 2021/22–2025/26, representing an increase of approximately 10.6%.

**2. The widening was driven primarily by declining bottom-five performance.**

Across the two comparison periods:

| Performance group | Earlier PPG | Recent PPG |
|---|---:|---:|
| Top five | 1.999 | 2.004 |
| Middle ten | 1.288 | 1.355 |
| Bottom five | 0.917 | 0.807 |

Top-five performance remained relatively stable, while bottom-five teams experienced a decline of approximately 0.11 PPG.

**3. Bottom-five teams lost ground particularly against middle-ten opponents.**

Their PPG against middle-ten opposition fell from 0.992 to 0.822. This contributed substantially to their overall decline, suggesting the deterioration was not confined to matches against the league's strongest teams.

**4. Home advantage against top-five opponents weakened for bottom-five teams.**

Bottom-five home PPG against top-five opponents declined from 0.600 to 0.392, while their away performance changed comparatively little. Heavy home defeats against these opponents also became more frequent.

**5. Alternative team groupings supported the wider conclusion.**

Sensitivity analysis tested whether the widening was dependent on the original top-five and bottom-five definitions. The alternative groupings provided additional evidence that the result was not simply an artefact of one classification choice.

**6. League-wide performance dispersion increased.**

The standard deviation of team-season PPG increased from approximately 0.429 to 0.473, representing an increase of around 10.2%.

This provides a complementary measure of competitive imbalance beyond comparisons between selected team groups.

## Tools and Analytical Workflow

### Python — Data Collection and Validation

Python was used to acquire historical match data, inspect dataset structure, perform quality checks and conduct sensitivity analysis.

The workflow included checking data consistency and preparing the underlying information for subsequent analysis.

### SQL — Analytical Modelling

SQL was used to structure and aggregate match results, calculate points-per-game metrics, segment teams by league position and compare performance between periods.

The analytical process involved conditional aggregation, joins, grouping and common table expressions (CTEs).

### Tableau — Data Visualisation

Tableau was used to develop an interactive, six-finding dashboard presenting the results and accompanying interpretation.

The dashboard combines trend analysis, performance-group comparisons, opponent-level breakdowns, home-and-away analysis, sensitivity testing and distributional measures.

## Methodology

**Data source:** [Football-Data.co.uk](https://www.football-data.co.uk/englandm.php)

**Coverage:** 16 Premier League seasons, 2010/11–2025/26 (6,080 matches).

**Comparison periods:**
- Earlier: 2010/11–2014/15
- Recent: 2021/22–2025/26

**Performance groups:** Teams were classified using their final league positions in each season:
- Top five: positions 1–5
- Middle ten: positions 6–15
- Bottom five: positions 16–20

**Primary measure:** Points per game (PPG), calculated as points earned divided by matches played.

The analysis compares performance between defined periods and examines whether the observed changes remain consistent across different measures and grouping choices.

## Validation and Sensitivity Analysis

To improve confidence in the findings, the project included:

- Data quality and consistency checks during preparation.
- Cross-validation of analytical results using Python and SQL.
- Checks on match totals and aggregated performance metrics.
- Sensitivity analysis using alternative performance-group definitions.
- Comparison of the primary group-level findings with league-wide dispersion measures.

These checks were intended to identify calculation errors, assess the dependence of the results on methodological choices and avoid relying on a single indicator.

## Limitations

This is a descriptive, observational analysis rather than a causal study.

Several limitations should be considered:

- Team group membership changes between seasons, so the analysis measures performance by league position rather than following a fixed set of clubs.
- Earlier-versus-recent comparisons may be sensitive to the selected periods.
- PPG and dispersion capture important dimensions of competitive balance but do not measure every aspect of league competitiveness.
- The analysis does not establish the causes of widening performance differences, such as financial resources, recruitment strategies or tactical developments.

Further research could incorporate club finances, wage expenditure and transfer spending to investigate potential explanatory factors.

## Repository Structure

- **`python/`** — Data acquisition, inspection and sensitivity analysis scripts.
- **`sql/`** — Analytical queries, aggregations and validation.
- **`tableau/`** — Tableau workbook and dashboard materials.
- **`README.md`** — Project overview, findings and methodology.

The scripts and workbook document the analytical approach. Reproducing the complete workflow may require downloading the source data and configuring local file paths and database connections.

## How to Reproduce

This repository contains the Python scripts, SQL queries and Tableau workbook used to investigate Premier League competitive balance across 16 seasons (2010/11–2025/26).

### 1. Prerequisites

The analysis uses:

- **Python 3** — data collection, inspection and sensitivity analysis.
- **MySQL and MySQL Workbench** — data storage, transformation and analytical queries.
- **Tableau Desktop or Tableau Public Edition** — dashboard visualisation.

The original match data comes from [Football-Data.co.uk](https://www.football-data.co.uk/englandm.php).

### 2. Download the Repository

Clone the repository or download it as a ZIP file.

```bash
git clone https://github.com/Magnolia-bit/premier-league-competitive-balance.git
cd premier-league-competitive-balance
```

### 3. Python — Data Collection and Inspection

Set up a Python environment and install the external libraries imported by the scripts.

The intended execution order is:

```bash
python python/download_seasons.py
python python/inspect_seasons.py
```

The first script retrieves historical Premier League data. The second inspects the downloaded files and supports data quality checks.

Ensure that the scripts' input and output paths match your local directory structure.

### 4. SQL — Data Preparation and Analysis

1. Create a local MySQL database.
2. Import the prepared Premier League data into the tables referenced by the SQL scripts.
3. Run the scripts in the `sql/` folder, executing any table-creation and transformation queries before downstream analytical queries.
4. Execute the validation queries to check the calculated metrics and aggregated results.

The SQL analysis calculates points-per-game measures, classifies teams by performance group and compares historical periods.

### 5. Python — Sensitivity Analysis

Run the sensitivity analysis script once its required input datasets have been prepared.

```bash
python python/sensitivity_analysis.py
```

This tests how the analytical conclusions respond to alternative performance-group definitions.

### 6. Tableau — Visualisation

Open the packaged Tableau workbook (`.twbx`) from the `tableau/` folder.

The workbook contains the published dashboard and packaged data extracts. To regenerate the visualisations using newly calculated results, update the relevant Tableau data sources and refresh the extracts.

The completed dashboard can also be viewed online:

[**View Interactive Dashboard**](https://public.tableau.com/app/profile/cameron.sullivan.davis/viz/Premier_League_Competitive_Balance/Dashboard1)

### Reproducibility Notes

The repository documents the principal stages of the analytical process. A complete independent rerun has not yet been verified from a fresh environment.

The exact Python package requirements, database import specifications, script dependencies and local file paths should be confirmed before treating the workflow as fully reproducible.

## AI-Assisted Development Disclosure

This was an independently directed, AI-assisted analytics project.

ChatGPT provided substantial assistance with code generation, debugging, technical guidance, Tableau development and analytical review.

I directed the research questions, selected and assessed the methodology, executed and tested the code, cross-validated results using Python and SQL, interpreted the findings and developed the final Tableau visualisations.

AI assistance was used to accelerate implementation and support learning, with analytical outputs subject to review and validation.

## Project Outcome

The project demonstrates an end-to-end analytics workflow, from data acquisition and quality checks to analytical modelling, sensitivity testing and communication of findings.

The central conclusion is that Premier League performance inequality has increased across the periods examined, with declining results among bottom-five teams explaining much of the widening gap.

The analysis also illustrates the importance of investigating *why a metric has changed*, validating findings across alternative approaches and recognising the limitations of descriptive analysis.
