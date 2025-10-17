import sys
import traceback
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
import os
import argparse
import io
from contextlib import closing
from typing import Optional


repo_root = Path(__file__).resolve().parents[1]
data_dir = repo_root / "data"

# Reads latest CSV file and pushes the data into database
####################################
def find_latest_file(data_dir: Path) -> Path:
	files = sorted(data_dir.glob("trending_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
	if not files:
		raise FileNotFoundError(f"No trending_*.csv files found in {data_dir}")
	return files[0]


# Load the latest CSV into the database
####################################
def load_latest(dry_run: bool = False, database_url: Optional[str] = None) -> None:
	latest = find_latest_file(data_dir)
	DATABASE_URL = database_url or os.environ.get(
		"DATABASE_URL",
		"postgresql+psycopg2://airflow:airflow@postgres:5432/airflow",
	)
	engine = create_engine(DATABASE_URL)

	try:
		df = pd.read_csv(latest)
		if dry_run:
			print("Dry run: dataframe preview:")
			print(df.head())
			print(df.info())
			return

		print("Using DATABASE_URL=", DATABASE_URL)
		csv_buffer = io.StringIO()
		df.to_csv(csv_buffer, index=False)
		csv_buffer.seek(0)

		cols = [c.replace('"', '""') for c in df.columns]
		quoted_cols = ",".join(f'"{c}"' for c in cols)
		create_stmt = f'CREATE TABLE IF NOT EXISTS trending_videos ({", ".join(f"\"{c}\" TEXT" for c in cols)})'

		with closing(engine.raw_connection()) as raw_conn:
			with closing(raw_conn.cursor()) as cur:
				cur.execute(create_stmt)
				copy_stmt = f"COPY trending_videos ({quoted_cols}) FROM STDIN WITH CSV HEADER DELIMITER ','"
				cur.copy_expert(copy_stmt, csv_buffer)
				raw_conn.commit()
				print(f"Loaded data from {latest.name} to PostgreSQL via COPY")
	except Exception:
		print("Failed to load data to PostgreSQL:")
		traceback.print_exc()
		raise


def _cli_main():
	parser = argparse.ArgumentParser(description="Load latest trending CSV into Postgres")
	parser.add_argument("--dry-run", action="store_true", help="Do not write to the database; just print DataFrame info")
	args = parser.parse_args()

	try:
		load_latest(dry_run=args.dry_run)
	except Exception:
		sys.exit(1)


if __name__ == "__main__":
	_cli_main()