# STR Data Pipeline Execution Instructions

This pipeline automates raw NCRMP STR data processing, logical quality control checks, PDF report generation, and archival package formatting.

With all of the aforementioned instructions, check the repository_schema.md file to check location. 

---

### Step 1: Pre-Execution Environment Check

First, ensure you have activated your virtual environment inside your terminal using your standard activation command. Second, confirm all dependencies are installed up to date by running a dependency synchronization command targeting your requirements file. Finally, drop your raw subsurface data files into your designated data directory, ensuring the file name matches your expected regional conventions.

---

### Step 2: Configure Your Run Parameters

Open the main script orchestrator file and scroll down to the absolute bottom of the script inside the main block. Update the isolated strings to match your current dataset parameters. You will need to modify the string tags for the initiative, organization, data type, region, and year. The script will use these to auto-construct your file prefix and path schemas. You must also update the source file path string to point directly to the absolute local filesystem path of your raw input data sheet.

---

### Step 3: Choose Your Execution Mode and Run

The pipeline runs in two distinct states depending on how you toggle the final boolean parameter inside the main quality control report function call:

#### Option A: Development and Review Mode (final is set to False)
Use this mode during initial data triage, general exploration, or when checking for unexpected data spikes. To trigger it, set the final variable to False in the function parameters. This state keeps your local filesystem clean by generating only the draft validation PDF report and dropping it right into your current active terminal execution directory. No data files are split, zipped, or shifted into archive hierarchies.

#### Option B: Production and Archival Mode (final is set to True)
Use this mode once your initial review pass is complete, all quality control parameter warnings are accounted for, and the dataset is ready to be zipped for official archive delivery. To trigger it, change the final variable to True in the function parameters. This state automatically builds an isolated production directory named after your dataset prefix and orchestrates the complete archive package assembly.

#### To Run:
In the Repository, run the following command from the terminal

```
python .\generate_qc_report.py
```

---

### Production Package Architecture

When executed in full production mode, the pipeline automatically processes your dataset and leaves your target directory in a perfectly organized, archive-ready layout:

The main directory is named after your unique file prefix. Inside this folder, you will find a standardized asset manifest README file that details total records and partition steps. You will also find the final compiled data audit quality control report PDF. Alongside these documentation assets, the pipeline deposits two compressed archive files: a master data archive zip containing the raw master dataset and a split data archive zip containing your sequential one-million-row data parts.

To keep your workspace clutter-free, the pipeline provisions a temporary unzipped split subdirectory to safely stream data slices, packages those slices into the target split zip file, and completely destroys the unzipped intermediate loose partitions upon successful completion.
