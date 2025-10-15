import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine


# Reads latest CSV file and pushes the data into database
####################################
repo_root = Path(__file__).resolve().parents[1]
data_dir = repo_root / "data"

files = sorted(data_dir.glob("trending_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
if not files:
	print(f"Error: no trending_*.csv files found in {data_dir}")
	sys.exit(1)

latest = files[0]

engine = create_engine("postgresql://yt_user:password@localhost:5432/youtube_data")
df = pd.read_csv(latest)
df.to_sql("trending_videos", engine, if_exists="append", index=False)
print(f"Loaded data from {latest.name} to PostgreSQL")