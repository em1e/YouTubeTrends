SELECT 
  channel_title,
  COUNT(*) AS video_count,
  SUM(view_count::bigint) AS total_views
FROM trending_videos
GROUP BY channel_title
ORDER BY total_views DESC
LIMIT 10