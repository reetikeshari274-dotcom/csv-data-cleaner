import argparse
import csv
import sys
from pathlib import Path


def detect_delimiter(file_path: Path, sample_text: str) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".tsv":
        return "\t"
    try:
        dialect = csv.Sniffer().sniff(sample_text, delimiters=[",", "\t", ";", "|"])
        return dialect.delimiter
    except csv.Error:
        return ","


def validate_paths(input_path: Path) -> None:
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not input_path.is_file():
        print(f"Error: '{input_path}' is a directory, not a file.", file=sys.stderr)
        sys.exit(1)

    supported_exts = {".csv", ".tsv", ".txt"}
    if input_path.suffix.lower() not in supported_exts:
        print(
            f"Warning: '{input_path.name}' is not a standard .csv/.tsv/.txt file. "
            "Attempting to read as delimited text..."
        )


def clean_csv(input_path: Path, output_path: Path) -> None:
    validate_paths(input_path)

    seen_rows = set()
    cleaned_rows = []
    skipped_blank = 0
    skipped_duplicates = 0

    try:
        with input_path.open(mode="r", encoding="utf-8-sig", newline="") as infile:
            sample = infile.read(2048)
            infile.seek(0)
            delimiter = detect_delimiter(input_path, sample)

            reader = csv.DictReader(infile, delimiter=delimiter)

            if not reader.fieldnames:
                print("Error: File is empty or missing column headers.", file=sys.stderr)
                sys.exit(1)

            clean_headers = [
                header.strip() if header and header.strip() else f"column_{idx}"
                for idx, header in enumerate(reader.fieldnames)
            ]
            reader.fieldnames = clean_headers

            for row in reader:
                cleaned_row = {}
                for col in clean_headers:
                    raw_val = row.get(col)
                    cleaned_row[col] = raw_val.strip() if isinstance(raw_val, str) else ""

                if all(value == "" for value in cleaned_row.values()):
                    skipped_blank += 1
                    continue

                row_signature = tuple(cleaned_row[col] for col in clean_headers)

                if row_signature in seen_rows:
                    skipped_duplicates += 1
                    continue

                seen_rows.add(row_signature)
                cleaned_rows.append(cleaned_row)

    except UnicodeDecodeError:
        print(
            f"Error: Unable to decode '{input_path}' as UTF-8. "
            "If this is an Excel (.xlsx) file, export it as CSV UTF-8 first.",
            file=sys.stderr,
        )
        sys.exit(1)
    except csv.Error as err:
        print(f"File Format Error: Malformed data ({err}).", file=sys.stderr)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    out_delimiter = "\t" if output_path.suffix.lower() == ".tsv" else ","
    out_encoding = "utf-8-sig" if out_delimiter == "," else "utf-8"

    try:
        with output_path.open(mode="w", encoding=out_encoding, newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=clean_headers, delimiter=out_delimiter)
            writer.writeheader()
            writer.writerows(cleaned_rows)
    except PermissionError:
        print(
            f"Error: Permission denied writing to '{output_path}'. "
            "Close the file if it is open in another program.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Success! Cleaned data saved to '{output_path}'.")
    print(
        f"Rows kept: {len(cleaned_rows)} | "
        f"Blank rows removed: {skipped_blank} | "
        f"Duplicates removed: {skipped_duplicates}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean messy CSV/TSV/TXT files by stripping whitespace, removing blank rows, and deleting duplicates."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        type=Path,
        help="Path to the messy input file (.csv, .tsv, .txt)",
    )
    parser.add_argument(
        "-o", "--output",
        default=Path("cleaned_output.csv"),
        type=Path,
        help="Path to save the cleaned file (default: cleaned_output.csv)",
    )

    args = parser.parse_args()
    clean_csv(args.input, args.output)


if __name__ == "__main__":
    main()
