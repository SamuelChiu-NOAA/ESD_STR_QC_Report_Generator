import os
import io
import html
import math
import time
from datetime import datetime
from pathlib import Path
import polars as pl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak

# Custom report utilities and logic layout imports
from pdf_report_utils import title_style, h2_style, normal_style, code_style, df_to_pdf_table, ParagraphStyle
from qc_validation import run_quality_control

# Import the extracted presentation layer function
from pdf_content_builder import build_pdf_story


def generate_qc_report(str_file, output_path, final=False): 
    # Start the global script timer immediately
    script_start_time = time.time()

    print("="*60)
    print(f"STARTING QC REPORT GENERATION: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    if not os.path.exists(str_file):
        raise FileNotFoundError(f"Please provide a valid path for str_file. Current: {str_file}")

    # --- PATH Configuration & Folder Management ---
    base_output = Path(output_path)

    if final:
        # Production mode: Save to the specific path provided and ensure the directory exists
        OUTPUT_PDF = output_path
        output_dir = Path(OUTPUT_PDF).parent
        if not output_dir.exists():
            print(f"Creating missing production directory: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)
    else:
        # Dev mode: Save the QC report directly to the current working directory running the script
        OUTPUT_PDF = Path(output_path).name  # Just the filename, e.g., 'NCRMP_ESD_TEMPERATURE_MARIAN_2025_QC.pdf'
        print(f"Dev mode active. Saving report directly to current working directory.")

    # 1. Read everything purely as a streaming source (LazyFrame)
    STR_lazy = pl.scan_csv(
        str_file, 
        schema_overrides={"INSTRUMENTSN": pl.String},
        try_parse_dates=True
    )

    # 2. Run QC metrics using the streaming architecture
    print("Running Quality Control metrics...")
    qc = run_quality_control(STR_lazy)

    # 3. Initialize PDF layout template
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    story = []

    # --- Evaluation Banner Block ---
    all_checks_passed = (
        qc['problems_id'].is_empty() and 
        qc['problems_sn'].is_empty() and 
        len(qc['duplicates']) == 0 and
        len(qc['validstart_errors']) == 0 and 
        len(qc['validend_errors']) == 0 and
        len(qc['time_start_errors']) == 0 and 
        len(qc['time_end_errors']) == 0 and
        qc['intervals_problems_table'].is_empty()
    )

    if all_checks_passed:
        success_banner_style = ParagraphStyle(
            'SuccessBanner', parent=normal_style, fontName='Times-Bold', fontSize=11,
            textColor=colors.HexColor("#2F855A"), alignment=TA_CENTER, spaceAfter=15
        )
        story.append(Paragraph("✔ STATUS: All Quality Control Checks Passed Successfully", success_banner_style))
        story.append(Spacer(1, 5))

    # Pack UI formatting layout references to pass to external builder
    report_styles = {
        'title_style': title_style,
        'h2_style': h2_style,
        'normal_style': normal_style,
        'code_style': code_style,
        'df_to_pdf_table': df_to_pdf_table
    }

    # Call external file layout code to construct headers, tables, and charts
    build_pdf_story(story, qc, STR_lazy, report_styles, str_file)

    # 4. Save and compile document structure
    print("All plots rendered. Compiling final PDF document...")
    doc.build(story)
    print(f"Report successfully compiled: {OUTPUT_PDF}")

    # --- Memory-Efficient Row-Count Slice Chunking (Production Only) ---
    if final:
        print("\n--- Generating Sequential CSV Subsections (Production Architecture) ---")
        
        total_rows = qc['total_records']
        chunk_size = 1_000_000  # 1 Million row limit per file partition
        total_chunks = math.ceil(total_rows / chunk_size)
        
        print(f"Streaming {total_rows:,} rows across {total_chunks} sequential files into {output_dir}...")

        for i in range(total_chunks):
            offset = i * chunk_size
            chunk_filename = output_dir / f"output_chunk_{i}.csv"
            
            print(f" Writing chunk {i+1}/{total_chunks}: {chunk_filename.name}")
            
            (
                STR_lazy
                .slice(offset, chunk_size)
                .sink_csv(str(chunk_filename))
            )

    total_execution_time = time.time() - script_start_time

    # Convert seconds to a clean minutes:seconds format if it takes longer
    minutes = int(total_execution_time // 60)
    seconds = total_execution_time % 60

    print("\n" + "="*60)
    if minutes > 0:
        print(f"✔ PROCESS COMPLETED TOTAL RUNTIME: {minutes} min {seconds:.2f} seconds")
    else:
        print(f"✔ PROCESS COMPLETED TOTAL RUNTIME: {total_execution_time:.2f} seconds")
    print("="*60 + "\n")


if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # 1. UPDATE INPUT FILE PATH HERE
    # Change this whenever you have a new year or region of data.
    # -------------------------------------------------------------------------
    str_file = r"C:\Users\Samuel.Chiu\Documents\Repositories\STR_automation\NCRMP_STR_DATA\NCRMP_ESD_TEMPERATURE_MARIAN_2025.csv"
    
    # -------------------------------------------------------------------------
    # 2. UPDATE DESIRED OUTPUT DESTINATION HERE
    # Change this to point to the official network drive or regional folder.
    # -------------------------------------------------------------------------
    output_path = r"C:\Users\Samuel.Chiu\Documents\Repositories\STR_automation\QC_Reports\NCRMP_ESD_TEMPERATURE_MARIAN_2025_QC.pdf"

    # -------------------------------------------------------------------------
    # 3. TOGGLE EXECUTION MODE HERE
    # Change final=False to final=True when you are ready to archive.
    # -------------------------------------------------------------------------
    generate_qc_report(str_file, output_path, final=False)