import polars as pl
from pathlib import Path

# Define the relative path to the subfolder and file
file_path = Path.cwd() / 'STR_data' / 'metadata.xlsx'

# Read the Excel file 
df = pl.read_excel(file_path)

# Clean names: lowercase and replace whitespace/special chars with underscores
df_clean = df.rename({col: col.lower().replace(" ", "_").replace("(", "").replace(")", "") for col in df.columns})

print("Columns:", df_clean.columns)

# Drop rows where date_retrieved is null AND collected_by_... is 'N'
df_filtered = df_clean.filter(
    ~(pl.col('date_retrieved').is_null() & (pl.col('collected_by_esa_team__in_feb_2026?') == 'N'))
)
 
print(df_filtered)

# Converting height from feet to meters
df_filtered = df_filtered.with_columns(
    (pl.col("max_depth_ft") * 0.3048).alias("DEPTH_M")
)

# Write to CSV
df_filtered.write_csv("filtered_metadata.csv")