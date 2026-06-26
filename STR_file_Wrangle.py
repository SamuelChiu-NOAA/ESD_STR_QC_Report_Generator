import os
import glob
import polars as pl

folder_path = "./STR_data"
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
meta_data_path = "./filtered_metadata.csv"
output_filename = "combined_output.csv"

# Load master metadata once
metadata_master_df = pl.read_csv(meta_data_path)

# Ensure site_deployed column matches the format we will join against
metadata_master_df = metadata_master_df.with_columns(
    pl.col('site_deployed').cast(pl.String)
)

is_first_file = True
num_processed_files = 0

for file_path in csv_files:
    filename = os.path.basename(file_path)
    esa_site_id = filename[:11].replace('_', '-') 

    if esa_site_id == "ESA-TUT-003":
        continue

    print(f"Processing: {filename}")
    num_processed_files += 1

    # Extract short text headers quickly
    with open(file_path, 'r', encoding='utf-8') as f:
        instrument_type = f.readline().strip()[-5:] 
        serial_number = f.readline().strip()[-8:] 
        INSTFIELDSUMMARYID = "4" + serial_number[-4:]

    # 1. Read data lazily to optimize memory usage
    df_lazy = pl.scan_csv(file_path, skip_rows=11)

    # 2. Build tracking columns lazily
    df_lazy = df_lazy.with_columns([
        (pl.col('Date').cast(pl.String) + 'T' + pl.col('Time').cast(pl.String) + 'Z').alias('TIMESTAMP'),
        pl.col('Temperature').alias('TEMP_C'),
        pl.lit(esa_site_id).alias('OCC_SITEID')
    ])

    # 3. Vectorized join with master metadata on our unique identifier
    df_lazy = df_lazy.join(
        metadata_master_df.lazy(),
        left_on="OCC_SITEID",
        right_on="site_deployed",
        how="left"
    )

    # 4. Normalize columns from join or provide fallback defaults if missing
    df_lazy = df_lazy.with_columns([
        pl.col('latitude').fill_null(pl.lit("UNKNOWN")).alias('LATITUDE'),
        pl.col('longitude').fill_null(pl.lit("UNKNOWN")).alias('LONGITUDE'),
        pl.col('DEPTH_M').fill_null(pl.lit("UNKNOWN")).alias('DEPTH_M'),
        pl.col('2026_mission_id').fill_null(pl.lit("UNKNOWN")).alias('RETRIEVE_CRUISE'),
        pl.col('date_retrieved').fill_null(pl.lit("UNKNOWN")).alias('RETRIEVE_UTC'),
        pl.col('2025_mission_id').fill_null(pl.lit("UNKNOWN")).alias('DEPLOY_CRUISE'),
        pl.col('date_deployed').fill_null(pl.lit("UNKNOWN")).alias('DEPLOY_UTC'),
    ])

    # 5. Apply time cutoffs safely in lazy mode
    df_datetime = pl.col('TIMESTAMP').str.to_datetime("%Y-%m-%dT%H:%M:%SZ")
    deploy_date = pl.datetime(
        pl.col('DEPLOY_UTC').str.to_datetime().dt.year(),
        pl.col('DEPLOY_UTC').str.to_datetime().dt.month(),
        pl.col('DEPLOY_UTC').str.to_datetime().dt.day(),
        16, 0, 0
    )
    retrieve_cutoff = pl.col('RETRIEVE_UTC').str.to_datetime()
    
    df_lazy = df_lazy.filter((df_datetime >= deploy_date) & (df_datetime <= retrieve_cutoff))

    # 6. Set Valid Range Bounds using pure lazy expressions
    df_lazy = df_lazy.with_columns([
        pl.col('TIMESTAMP').min().alias('VALID_DATA_START'),
        pl.col('TIMESTAMP').max().alias('VALID_DATA_END'),
        pl.col('Date').str.to_date("%Y-%m-%d").dt.year().alias('YEAR'),
        pl.col('Date').str.to_date("%Y-%m-%d").dt.month().alias('MONTH'),
        pl.col('Date').str.to_date("%Y-%m-%d").dt.day().alias('DAY'),
        pl.col('Time').str.to_time("%H:%M:%S").dt.hour().alias('HOUR'),
        pl.col('Time').str.to_time("%H:%M:%S").dt.minute().alias('MINUTE'),
        pl.col('Time').str.to_time("%H:%M:%S").dt.second().alias('SECOND'),
        pl.lit(filename).alias('File'),
        pl.lit(instrument_type).alias('INSTRUMENT_TYPE'),
        pl.lit(serial_number).alias('INSTRUMENTSN'),
        pl.lit("SAMOA").alias('REGION'),
        pl.lit("TUTUILA").alias('LOCATION'),
        pl.lit(INSTFIELDSUMMARYID).alias('INSTFIELDSUMMARYID')
    ])

    # Select final layout columns
    columns_ordered = [
        'OCC_SITEID', 'LATITUDE', 'LONGITUDE', 'DEPTH_M', 'REGION', 'LOCATION', 
        'INSTRUMENT_TYPE', 'INSTRUMENTSN', 'DEPLOY_CRUISE', 'DEPLOY_UTC', 
        'RETRIEVE_CRUISE', 'RETRIEVE_UTC', 'VALID_DATA_START', 'INSTFIELDSUMMARYID', 
        'VALID_DATA_END', 'YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND', 'TIMESTAMP', 'TEMP_C'
    ]
    df_lazy = df_lazy.select(columns_ordered)

    # 7. Collect this individual frame eagerly to dump to disk
    df_processed = df_lazy.collect()
    if df_processed.is_empty():
        continue

    # 8. Append to target output file incrementally to save system RAM entirely
    if is_first_file:
        df_processed.write_csv(output_filename, include_header=True)
        is_first_file = False
    else:
        with open(output_filename, "ab") as f:
            df_processed.write_csv(f, include_header=False)

print(f"\nSuccess! Processing complete. Combined output sent to '{output_filename}'")