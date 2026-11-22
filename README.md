![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none%20(CLI)-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

# CSV Data Cleaner

A fast Python utility (CLI + Browser App) that sanitizes messy tabular files (**CSV, TSV, TXT**) by stripping stray whitespace, dropping blank rows, and deduplicating records.

## 🌐 Use Directly in Browser (No Clone Needed)
Open the live web app, upload your `.csv` / `.tsv` / `.txt` file, and download the cleaned output:
👉 **[Launch Data Cleaner App](https://csv-data-cleaner-m5szwbq7maankeappg5inoy.streamlit.app/)**

*(Note: If your data is in an `.xlsx` Excel file, save/export it as **CSV UTF-8** first.)*

## Features
- **Whitespace Trimming:** Cleans leading and trailing spaces across column headers and individual cells.
- **Blank Row Removal:** Detects and skips completely empty or whitespace-only rows.
- **Smart Deduplication:** Identifies duplicate records *after* whitespace normalization using $O(1)$ hash lookups.
- **Excel BOM Safe:** Handles `utf-8-sig` encoding seamlessly so Excel-exported CSVs never break headers.
- **Multi-Delimiter Support:** Works with comma (`,`), tab (`\t`), semicolon (`;`), and pipe (`|`) separated files.
- **Zero External Dependencies for CLI:** `cleaner.py` uses only Python's standard library (`argparse`, `csv`, `pathlib`).

## Quick Start (CLI)

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/reetikeshari274-dotcom/csv-data-cleaner.git](https://github.com/reetikeshari274-dotcom/csv-data-cleaner.git)
   cd csv-data-cleaner
