# STR_automation Repository Schema

This schema describes the repository-only contents of the `STR_automation` project. It excludes untracked or local-only files such as generated `*.pdf` reports and temporary outputs.

## Repository Map

```text
STR_automation/
│
├── .devcontainer/                    # Dev Container Configuration
│   ├── devcontainer.json             # Container environment setup
│   └── devcontainer-lock.json        # Dependency lock file
│
├── .gitignore                        # Git ignore rules
│
├── README.md                         # Project documentation
├── repository_schema.md              # Project repository layout and diagram
├── requirements.txt                  # Python runtime dependencies
│
│   # --- CORE NCRMP PIPELINE MODULES ---
├── generate_qc_report.py             # Orchestration script (Main Entry Point)
├── qc_validation.py                  # Polars-driven data validation & QC rule engine
├── pdf_content_builder.py            # Presentation layer: PDF story builder & chart generator
├── pdf_report_utils.py               # Document styles & table formatting helpers
│
│   # --- EXTENSION MODULES (NON-NCRMP / ARCHIVED) ---
├── Station_wrangle.py                # ESA station metadata wrangling (Not required for NCRMP)
└── STR_file_Wrangle.py               # ESA raw source file formatting (Not required for NCRMP)
```

## Diagram of Repo Flow

```text
                     +---------------------------------------+
                     |        NCRMP Source Data CSV          |
                     |  (e.g., NCRMP_ESD_TEMPERATURE_2025)   |
                     +-------------------+-------------------+
                                         |
                                         | Streams data into
                                         v
                     +---------------------------------------+
                     |           qc_validation.py            |
                     |  - Runs streaming rules on LazyFrame  |
                     |  - Flags range & timeline anomalies   |
                     +-------------------+-------------------+
                                         |
                                         | Passes metrics dict & stream
                                         v
                     +---------------------------------------+
                     |        pdf_content_builder.py         |
                     |  - Downsamples data & plots charts    |
                     |  - Structures document flow (story)   |
                     +-------------------+-------------------+
                                         |
                                         | Returns fully built story
                                         v
+----------------------------------------+---------------------------------------+
|                         generate_qc_report.py                                  |
|  - Main Orchestrator / Entry Point                                             |
|  - Controls output target directories dynamically via `final` switch           |
|  - Compiles PDF Document / Conditionally streams out sequential CSV chunks     |
+----------------------------------------+---------------------------------------+
                                         |
                     +-------------------+-------------------+
                     |                                       |
                     v (final=False)                         v (final=True)
       +---------------------------+            +---------------------------+
       | Current Running Directory |            | Production Directory Path |
       | - QC Report PDF Only      |            | - QC Report PDF           |
       +---------------------------+            | - Sliced Subsections (CSV)|
                                                +---------------------------+

===================================================================================
  [EXTENSIONS / SEPARATE DATASET WORKFLOW] (Not required for core NCRMP pipeline)
===================================================================================
  +-------------------------+               +-------------------------+
  |   Station_wrangle.py    | ------------> |  STR_file_Wrangle.py    |
  |   (ESA Metadata Setup)  |               | (ESA CSV Aggregator)    |
  +-------------------------+               +-------------------------+
```

## ⚙️ Configuration Guide: What to Change and Why
All user-configurable variables are isolated at the bottom of generate_qc_report.py within the if __name__ == "__main__": block, or inside the generate_qc_report function definition itself.


### 1. File Paths (if __name__ == "__main__":)
``` python
str_file = r"C:\Users\Samuel.Chiu\Documents\Repositories\STR_automation\NCRMP_STR_DATA\NCRMP_ESD_TEMPERATURE_MARIAN_2025.csv"
output_path = r"C:\Users\Samuel.Chiu\Documents\Repositories\STR_automation\QC_Reports\NCRMP_ESD_TEMPERATURE_MARIAN_2025_QC.pdf"
```

#### str_file **Line 145, generate_qc_report.py**
What it is: The absolute system path to your raw subsurface temperature dataset.

Why change it: Change this whenever you receive a new year of survey data or a different regional dataset (e.g., Marianas vs. American Samoa).



#### output_path ***Line 151, generate_qc_report.py***
What it is: The intended final resting place for your production PDF report. Also what name you give the generated file. 

Why change it: Update this to match the specific project folder naming conventions. Note: If final=False, only the file name at the end of this path is extracted to name your local file.




### 2. Runtime Execution Controls (generate_qc_report.py)
``` Python
generate_qc_report(str_file, output_path, final=False)
final=False (Development/Review Mode)
```

#### The Execution Mode Flag (final) ***Line 157, generate_qc_report.py*** 
Why use it: Use this during initial data exploration or when adjusting QC logic thresholds. It keeps your workspace clean by outputting only the PDF report directly into your current running terminal directory—preventing you from accidentally polluting archive directories with draft PDFs.

final=True (Production/Archival Mode)

Why use it: Use this when data validation is complete and you are ready to archive the outputs. It automatically builds any missing directories specified in your output_path, saves the final report there, and initiates the data-splitting pipeline.

Slicing Partition Size (chunk_size)
Located inside the if final: block:

Python
chunk_size = 1_000_000  # Sets row count per split file
chunk_size

What it is: The exact number of rows allocated to each sub-CSV file during production export.

Why change it: If your database import tools or end-user software (like Excel or specialized GIS tools) crash when loading monolithic multi-gigabyte CSVs, lower this threshold (e.g., to 500_000) to generate smaller, more manageable data packets.

## Notes

* `Station_wrangle.py` and `STR_file_Wrangle.py` are maintained as nonstandard, auxiliary helpers. They are useful for preparing input data, but the core report-generation flow is centered on `qc_validation.py` and `generate_qc_report.py`.
* `requirements.txt` now reflects only the runtime dependencies required by the tracked Python scripts.
