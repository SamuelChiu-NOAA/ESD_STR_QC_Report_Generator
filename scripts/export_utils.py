import math
import os
from pathlib import Path
import zipfile


def generate_readme(
    output_path: str, 
    total_rows: int, 
    file_prefix: str
) -> None:
    """
    Parses metadata from the input CSV file name and generates a standardized 
    readme.txt file in the production output directory.
    """

    # This is only ran when the final production output is generated, so we can safely assume the output_path is valid
    output_dir = Path(output_path).parent
    

    # Calculate chunk stats using the 1-million row production rule
    chunk_size = 1_000_000
    total_chunks = math.ceil(total_rows / chunk_size)


    # Safely extract Region and Year from the file_prefix naming convention
    # expected: 'NCRMP_ESD_TEMPERATURE_MARIAN_2025'
    parts = file_prefix.split('_')
    region = parts[3].title() if len(parts) >= 4 else "Unknown Region"  # 'MARIAN' -> 'Marian'
    year = parts[4] if len(parts) >= 5 else "Unknown Year"              # '2025'

    readme_path = output_dir / "readme.txt"

    readme_content = f"""\
        Total Records: {total_rows:,}
        Total Split Files: {total_chunks}

        Temperature data for the {region} collected in {year} are provided as a single data file in ZIP and CSV format. 
        Additionally, the single data file has been SPLIT into a series of {total_chunks} CSV files (1-million rows each, except for the last CSV file in the series).
        These split files are provided in a single zip file and as a series of CSV files.

        0-DATA contains: README, {file_prefix}.zip, and {file_prefix}_split.zip
        ===> 0-DATA > UNZIPPED contains: {file_prefix}.csv
            ===> 0-DATA > UNZIPPED > SPLIT contains: series of split CSV files ({file_prefix}_chunk_#.csv)
        
    """


    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.write(readme_content)


    print("\nParsing Complete!")
    print(f"readme written to: {readme_path}")


def zip_production_artifacts(output_dir: Path, split_sub_dir: Path, file_prefix: str, str_file: str) -> None:
    """
    Zips the master file and the isolated part subsections into their respective archives.
    """
    print("\n--- Compiling Production Zip Archives ---")
    
    # 1. Zip the original master CSV -> prefix.zip
    master_zip_path = output_dir / f"{file_prefix}.zip"

    print(f"Creating master data zip: {master_zip_path.name}")

    with zipfile.ZipFile(master_zip_path, 'w', zipfile.ZIP_DEFLATED) as master_zip:
        master_zip.write(str_file, arcname=f"{file_prefix}.csv")

    # 2. Zip all part files out of the deep folder -> prefix_split.zip
    split_zip_path = output_dir / f"{file_prefix}_split.zip"
    print(f"Creating split parts zip: {split_zip_path.name}")
    
    # Find the parts exactly where we hid them
    part_files = list(split_sub_dir.glob(f"{file_prefix}_part_*.csv"))
    
    with zipfile.ZipFile(split_zip_path, 'w', zipfile.ZIP_DEFLATED) as split_zip:
        for part in part_files:
            # arcname=part.name ensures the internal zip file structure stays flat
            split_zip.write(part, arcname=part.name)
            
    print("Zipping complete!")

    # 3. CLEANUP: Erase the temporary files and the folder itself
    print("Cleaning up temporary unzipped chunks and directories...")
    for part in part_files:
        part.unlink()  # Safely delete individual loose CSV parts
        
    # Remove the directory now that it's completely empty
    if split_sub_dir.exists():
        split_sub_dir.rmdir()
        print(f"Removed temporary directory: {split_sub_dir.name}")

