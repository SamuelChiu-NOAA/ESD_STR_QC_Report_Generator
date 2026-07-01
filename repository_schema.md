### 🗂️ Updated `repository_schema.md`


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
├── export_utils.py                   # Archive builder: README text generator & ZIP compilation
│
│   # --- EXTENSION MODULES (NON-NCRMP / ARCHIVED) ---
├── Station_wrangle.py                # ESA station metadata wrangling (Not required for NCRMP)
└── STR_file_Wrangle.py               # ESA raw source file formatting (Not required for NCRMP)
```

## Diagram of Repo Flow
``` text
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
                     |  - Validates 15°C - 40°C thresholds   |
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
|  - Compiles PDF Document / Dispatches structural exports to export_utils.py    |
+----------------------------------------+---------------------------------------+
                                         |
                     +-------------------+-------------------+
                     |                                       |
                     v (final=False)                         v (final=True)
       +---------------------------+            +------------------------------------------+
       | Current Running Directory |            | Isolate Target Folder (file_prefix/)     |
       | - QC Report PDF Only      |            |  Managed by export_utils.py pipeline:    |
       +---------------------------+            |  - QC Report PDF                         |
                                                |  - Structural README File                |
                                                |  - Master Data Archive (*.zip)           |
                                                |  - Sliced Partition Archive (*_split.zip)|
                                                +------------------------------------------+

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


### 1. Runtime Metadata & File Paths

``` python
initiative = "NCRMP"
organization = "ESD"
data_type = "TEMPERATURE"
region = "MARIAN"
year = "2025"

file_prefix = f"{initiative}_{organization}_{data_type}_{region}_{year}"
str_file = rf"C:\Users\...\NCRMP_STR_DATA\NCRMP_ESD_TEMPERATURE_MARIAN_2025.csv"

```

#### Metadata Strings & file_prefix
**What it is:** Parameters used to auto-construct file configurations and output folder hierarchies.
**Why change it:** Change this whenever you step into a new survey season or different geographical region to allow file engines to cleanly target text formatting metrics.

#### str_file
**What it is:** The absolute local path targeting your raw input subsurface temperature dataset.
**Why change it:** Point this to your new local CSV file whenever running new source data.


### 2. Runtime Execution Controls

``` python

generate_qc_report(str_file, file_prefix, final=False)

```

#### The Execution Mode Flag(**Final**)

**final=False** 
(Development/Review Mode): Keeps your local filesystem clean by dropping only the target draft validation PDF report directly into your current running directory. No data parsing or archiving takes place.


**final=True** 
(Production/Archival Mode): Used when data validation has passed without discrepancies. Generates the designated output directory matching **file_prefix**, creates the master and partition ZIP assets via export_utils.py, writes the template-compliant **README**, and removes intermediate staging targets automatically.