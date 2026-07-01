## 📋 Repository Purpose Overview

This project is a high-performance, Python-based STR data automation pipeline for the **PIFSC Ecosystem Sciences Division (ESD)**. It automates raw NCRMP STR file processing, metadata validation, streaming logical QC checks, and PDF report generation for archive-ready oceanographic survey outputs.

The architecture leverages a lightweight runtime footprint, utilizing streaming data frameworks to process large oceanographic datasets efficiently without exceeding memory constraints.

---

## 🛠️ Tech Stack & Runtime Dependencies

* **Language:** Python
* **Data processing:** `polars` for memory-efficient, lazy evaluation and streaming operations
* **Visualization:** `matplotlib` for time-series plotting
* **PDF generation:** `reportlab` for formatted, structured QC report outputs
* **Path handling & filesystem:** built-in `pathlib`, `os`, and `zipfile`

---

## 🗂️ Core Pipeline Components

The core repository follows a strict separation of concerns between data processing, presentation layout, export formatting, and orchestration:

* **`generate_qc_report.py`** — The main orchestrator and entry point. Manages environment configurations and dynamically shifts file generation logic between development and production runs based on the runtime flag.
* **`qc_validation.py`** — The computational engine. Applies data quality control validation rules (including 15°C - 40°C biological threshold checking) to structured STR data streams.
* **`pdf_content_builder.py`** — The presentation layer builder. Downsamples high-frequency streaming data, dynamically renders time-series charts, and appends tables/text to the document layout structure.
* **`pdf_report_utils.py`** — Formatting utility layer. Converts Polars dataframes into ReportLab-friendly tables and defines global typographic styles.
* **`export_utils.py`** — Archive bundling automation. Generates structural text descriptions via the `README` file, packages data partitions, and automatically compresses outputs into production ZIP archives.

---

## ⚠️ Extension Modules (Archived / Non-NCRMP / Separate Workflow)

These legacy scripts are maintained outside the core NCRMP processing flow. They handle a separate ESA dataset workflow and are completely **optional** and unnecessary for standard NCRMP pipeline execution.

### `Station_wrangle.py`
* Cleans and standardizes legacy ESA station metadata records.
* Prepares auxiliary cruise deployment parameters for localized matching.

### `STR_file_Wrangle.py`
* Ingests, parses, and reformats raw ESA source CSV files.
* Handles legacy measurement merges to output intermediate combined CSV files.

---

## 📌 Runtime Workflows & Output Configurations

The pipeline executes entirely through `generate_qc_report.py`. The output behavior is determined by the `final` boolean parameter configured inside the function call:

### 1. Development & Quality Assurance Mode (`final=False`)
* **Behavior:** Validates the dataset and generates the QC report PDF.
* **Output Destination:** The final PDF report is dropped directly into whichever directory is currently executing the script (`current working directory`). No filesystem partitions are made, and no dataset chunking occurs.

### 2. Production & Archive Mode (`final=True`)
* **Behavior:** Validates the dataset, compiles the final PDF report, and automatically safely creates an isolated directory matching the `file_prefix`. 
* **Output Destination:** Streams out uniform 1,000,000-row CSV file partitions (`*_part_#.csv`) into a localized staging subdirectory (`UNZIPPED_SPLIT`), compiles an official asset layout metadata `README`, creates standalone compressed data ZIP archives, and safely handles temporary file deletions to leave a clean, structured package.

---

## 🔧 Requirements & Setup

Install the runtime dependencies with:

```bash
pip install -r requirements.txt
```

---

## How do I run this?

Please read the instructions in instructions.md. 

Cheers, 

Samuel Chiu ✌️

--- 
## Disclaimer
This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration, or the United States Department of Commerce. All NOAA GitHub project code is provided on an ‘as is’ basis and the user assumes responsibility for its use. Any claims against the Department of Commerce or Department of Commerce bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or
favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.
