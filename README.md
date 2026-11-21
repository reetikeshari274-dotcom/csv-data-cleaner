![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

# CSV Data Cleaner CLI

A fast, zero-dependency Python command-line utility that sanitizes messy CSV files by stripping stray whitespace, dropping blank rows, and deduplicating records.

## Features
- **Whitespace Trimming:** Cleans leading and trailing spaces across column headers and individual cells.
- **Blank Row Removal:** Detects and skips completely empty or whitespace-only rows.
- **Smart Deduplication:** Identifies duplicate records *after* whitespace normalization using $O(1)$ hash lookups.
- **Excel BOM Safe:** Handles `utf-8-sig` encoding seamlessly so Excel-exported CSVs never break headers.
- **Zero External Dependencies:** Built purely with Python's standard library (`argparse`, `csv`, `pathlib`).

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/csv-data-cleaner.git](https://github.com/YOUR_USERNAME/csv-data-cleaner.git)
   cd csv-data-cleaner