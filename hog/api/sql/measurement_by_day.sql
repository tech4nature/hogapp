-- aggregate measurements
WITH measurements AS
  (SELECT MAX(id) AS id,
          date_trunc(%s, observed_at) AS observed_at_trunc,
          MAX(measurement) AS measurement,
          MAX(video) AS video,
          measurement_type
   FROM api_measurement
   WHERE {conditions}
   GROUP BY observed_at_trunc, measurement_type
   ORDER BY observed_at_trunc),

-- create a table for every day including ones without measurements
all_days AS
  (SELECT generate_series(min_day, max_day, interval %s)::{date_type} AS date_increment
   FROM
     (SELECT MAX(observed_at_trunc) AS max_day,
             MIN(observed_at_trunc) AS min_day
      FROM measurements) d)

-- return a value for every day with nulls wbhere no measurements
SELECT m.id,
       all_days.date_increment::timestamp AS observed_at,
       m.measurement,
       m.video,
       %s AS hog_id,
       %s AS location_id,
       COALESCE(m.measurement_type, %s) AS measurement_type
FROM measurements AS m
RIGHT JOIN all_days ON m.observed_at_trunc = all_days.date_increment
