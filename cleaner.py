import argparse
import csv
import sys
from pathlib import Path


def validate_paths(input_path: Path) -> None:
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not input_path.is_file():
        print(f"Error: '{input_path}' is a directory, not a file.", file=sys.stderr)
        sys.exit(1)

    if input_path.suffix.lower() != ".csv":
        print(f"Warning: '{input_path.name}' does not have a .csv extension. Attempting to read anyway...")


def clean_csv(input_path: Path, output_path: Path) -> None:
    validate_paths(input_path)

    seen_rows = set()
    cleaned_rows = []
    skipped_blank = 0
    skipped_duplicates = 0

    try:
        # utf-8-sig handles standard UTF-8 as well as Excel-exported CSVs with BOM
        with input_path.open(mode="r", encoding="utf-8-sig", newline="") as infile:
            reader = csv.DictReader(infile)

            if not reader.fieldnames:
                print("Error: CSV file is empty or missing column headers.", file=sys.stderr)
                sys.exit(1)

            # Strip whitespace from headers and fallback safely if a header cell is blank
            clean_headers = [
                header.strip() if header and header.strip() else f"column_{idx}"
                for idx, header in enumerate(reader.fieldnames)
            ]
            reader.fieldnames = clean_headers

            for row in reader:
                # 1. Strip leading/trailing whitespace from each cell (handle None safely)
                cleaned_row = {}
                for col in clean_headers:
                    raw_val = row.get(col)
                    cleaned_row[col] = raw_val.strip() if isinstance(raw_val, str) else ""

                # 2. Skip completely blank rows
                if all(value == "" for value in cleaned_row.values()):
                    skipped_blank += 1
                    continue

                # 3. Create an immutable tuple fingerprint for O(1) duplicate detection
                row_signature = tuple(cleaned_row[col] for col in clean_headers)

                if row_signature in seen_rows:
                    skipped_duplicates += 1
                    continue

                seen_rows.add(row_signature)
                cleaned_rows.append(cleaned_row)

    except UnicodeDecodeError:
        print(f"Error: Unable to decode '{input_path}' as UTF-8. Please check file encoding.", file=sys.stderr)
        sys.exit(1)
    except csv.Error as err:
        print(f"CSV Format Error: Malformed CSV file ({err}).", file=sys.stderr)
        sys.exit(1)

    # Create parent directories for output if they do not exist yet
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with output_path.open(mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=clean_headers)
            writer.writeheader()
            writer.writerows(cleaned_rows)
    except PermissionError:
        print(f"Error: Permission denied writing to '{output_path}'. Close the file if it is open in another program.", file=sys.stderr)
        sys.exit(1)

    print(f"Success! Cleaned data saved to '{output_path}'.")
    print(f"Rows kept: {len(cleaned_rows)} | Blank rows removed: {skipped_blank} | Duplicates removed: {skipped_duplicates}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean a messy CSV file by stripping whitespace, removing blank rows, and deleting duplicates."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        type=Path,
        help="Path to the messy input CSV file"
    )
    parser.add_argument(
        "-o", "--output",
        default=Path("cleaned_output.csv"),
        type=Path,
        help="Path to save the cleaned CSV file (default: cleaned_output.csv)"
    )

    args = parser.parse_args()
    clean_csv(args.input, args.output)


if __name__ == "__main__":
    main()