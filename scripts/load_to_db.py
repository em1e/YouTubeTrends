import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://yt_user:password@localhost:5432/youtube_data")
df = pd.read_csv("/Users/mie/Desktop/side_projects/YouTubeTrends/data/trending_US.csv")
df.to_sql("trending_videos", engine, if_exists="append", index=False)
print("Loaded data to PostgreSQL")