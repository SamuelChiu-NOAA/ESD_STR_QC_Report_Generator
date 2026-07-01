import html
import polars as pl
from datetime import datetime
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

styles = getSampleStyleSheet()

# --- Exportable Styles ---
title_style = ParagraphStyle(
    'ReportTitle',
    parent=styles['Heading1'],
    fontName='Times-Roman',
    fontSize=16,
    leading=22,
    spaceAfter=20,
    alignment=TA_CENTER,
    textColor=colors.black
)

h2_style = ParagraphStyle(
    'Heading2Custom',
    parent=styles['Heading2'],
    fontName='Times-Bold',
    fontSize=12,
    leading=16,
    spaceBefore=14,
    spaceAfter=8,
    textColor=colors.black
)

normal_style = ParagraphStyle(
    'NormalCustom',
    parent=styles['Normal'],
    fontName='Times-Roman',
    fontSize=10,
    leading=14,
    spaceAfter=6,
    textColor=colors.black
)

code_style = ParagraphStyle(
    'CodeLike',
    parent=styles['Code'],
    fontName='Courier',
    fontSize=10,
    leading=14,
    spaceBefore=4,
    spaceAfter=10,
    textColor=colors.black
)

# --- Exportable Table Function (Pure Polars) ---
def df_to_pdf_table(df: pl.DataFrame):
    # Polars makes it easy to get headers as a list
    data_list = [df.columns]
    
    # Iterate through rows efficiently
    for row in df.iter_rows():
        row_str = []
        for val in row:
            if isinstance(val, (datetime, pl.Datetime)):
                row_str.append(val.strftime('%Y-%m-%d %H:%M:%S'))
            elif val is None:
                row_str.append("")
            else:
                row_str.append(str(val))
        data_list.append(row_str)
    
    t = Table(data_list, hAlign='LEFT')
    ts = [
        ('LINEABOVE', (0, 0), (-1, 0), 1.0, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1.0, colors.black),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9.0),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]
    for i in range(1, len(data_list)):
        if i % 2 == 0:
            ts.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor("#F2F2F2")))
    t.setStyle(TableStyle(ts))
    return t