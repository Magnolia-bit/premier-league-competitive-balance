
from pathlib import Path
from urllib.request import urlopen
from datetime import datetime, timezone
import hashlib
import csv

folder = Path(__file__).parent
manifest_path = folder / "source_manifest.csv"

# Preserve any previously recorded download dates.
existing_dates = {}

if manifest_path.exists():
    with manifest_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            existing_dates[row["Season"]] = row["RetrievedAtUTC"]

records = []

for year in range(2010, 2026):
    start = str(year)[-2:]
    end = str(year + 1)[-2:]
    season = f"{year}/{end}"

    file_path = folder / f"{start}-{end} original.csv"
    url = f"https://football-data.co.uk/mmz4281/{start}{end}/E0.csv"

    retrieved_at = existing_dates.get(season, "")

    if file_path.exists():
        print("Already saved:", file_path.name)
    else:
        try:
            with urlopen(url, timeout=30) as response:
                data = response.read()

            file_path.write_bytes(data)
            retrieved_at = datetime.now(timezone.utc).isoformat()
            print("Downloaded:", file_path.name)

        except Exception as error:
            print("Download failed:", file_path.name, error)
            continue

    # Calculate a digital fingerprint of each source file.
    file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()

    records.append({
        "Season": season,
        "SourceURL": url,
        "Filename": file_path.name,
        "RetrievedAtUTC": retrieved_at,
        "SHA256": file_hash
    })

# Export the source manifest.
with manifest_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "Season", "SourceURL", "Filename",
            "RetrievedAtUTC", "SHA256"
        ]
    )
    writer.writeheader()
    writer.writerows(records)

print("Saved:", manifest_path.name)
