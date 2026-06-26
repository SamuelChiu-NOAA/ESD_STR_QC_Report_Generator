## 📋 Repository Purpose Overview

This project is a high-performance, Python-based STR data automation pipeline for the **PIFSC Ecosystem Sciences Division (ESD)**. It automates raw NCRMP STR file processing, metadata validation, streaming logical QC checks, and PDF report generation for archive-ready oceanographic survey outputs.

The architecture leverages a lightweight runtime footprint, utilizing streaming data frameworks to process large oceanographic datasets efficiently without exceeding memory constraints.

---

## 🛠️ Tech Stack & Runtime Dependencies

* **Language:** Python
* **Data processing:** `polars` for memory-efficient, lazy evaluation and streaming operations
* **Visualization:** `matplotlib` for time-series plotting
* **PDF generation:** `reportlab` for formatted, structured QC report outputs
* **Path handling & filesystem:** built-in `pathlib` and `os`

---

## 🗂️ Core Pipeline Components

The core repository follows a strict separation of concerns between data processing, presentation layout, and orchestration:

* **`generate_qc_report.py`** — The main orchestrator and entry point. Manages environment configurations, file paths, and output behaviors based on runtime flags.
* **`qc_validation.py`** — The computational engine. Applies data quality control validation rules to structured STR data streams.
* **`pdf_content_builder.py`** — The presentation layer builder. Downsamples high-frequency streaming data, dynamically renders time-series charts, and appends tables/text to the document layout structure.
* **`pdf_report_utils.py`** — Formatting utility layer. Converts Polars dataframes into ReportLab-friendly tables and defines global typographic styles.

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
* **Output Destination:** The final PDF report is dropped directly into whichever directory is currently executing the script (`current working directory`). No filesystem changes are made, and no dataset chunking occurs.

### 2. Production & Archive Mode (`final=True`)
* **Behavior:** Validates the dataset, compiles the final PDF report, and automatically safely creates missing production directories if they don't exist.
* **Output Destination:** The PDF report is saved directly to the configured `output_path`. Simultaneously, the pipeline triggers a memory-efficient, sequential `.slice()` routine to stream out uniform 1,000,000-row CSV file partitions directly into that production folder using zero-RAM overhead `sink_csv` execution.

---

## 🔧 Requirements & Setup

Install the runtime dependencies with:

```bash
pip install -r requirements.txt
```

---

## How do I run this?

1. Make a data folder and add your data files to said folder.
2. Adjust the configuration which is detailed in the repoistory_schema.md!
3. Run generate_qc_report.py!

Cheers, 

Samuel Chiu ✌️
