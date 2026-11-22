import csv
import io
import streamlit as st
from cleaner import detect_delimiter

st.set_page_config(page_title="Data Cleaner Web", page_icon="🧹", layout="centered")

st.title("🧹 Data Cleaner (No Clone Required)")
st.caption("Upload a CSV, TSV, or TXT file to trim spaces, remove blank rows, and deduplicate records.")

uploaded_file = st.file_uploader(
    "Choose your file",
    type=["csv", "tsv", "txt"],
    help="Supports comma, tab, semicolon, or pipe separated text files."
)

if uploaded_file is not None:
    raw_bytes = uploaded_file.getvalue()

    try:
        text_data = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        st.error("Unable to decode file as UTF-8. Please save your file as UTF-8 and try again.")
        st.stop()

    delimiter = detect_delimiter(uploaded_file.name if hasattr(uploaded_file, "name") else st.session_state, text_data[:2048]) if False else None

    # Detect delimiter cleanly from filename + sample
    fname = uploaded_file.name.lower()
    if fname.endswith(".tsv"):
        delimiter = "\t"
    else:
        try:
            delimiter = csv.Sniffer().sniff(text_data[:2048], delimiters=[",", "\t", ";", "|"]).delimiter
        except csv.Error:
            delimiter = ","

    reader = csv.DictReader(io.StringIO(text_data), delimiter=delimiter)

    if not reader.fieldnames:
        st.error("File appears to be empty or has no header row.")
        st.stop()

    clean_headers = [
        h.strip() if h and h.strip() else f"column_{idx}"
        for idx, h in enumerate(reader.fieldnames)
    ]

    seen_rows = set()
    cleaned_rows = []
    skipped_blank = 0
    skipped_duplicates = 0

    for row in reader:
        cleaned_row = {}
        for col in clean_headers:
            raw_val = row.get(col)
            cleaned_row[col] = raw_val.strip() if isinstance(raw_val, str) else ""

        if all(val == "" for val in cleaned_row.values()):
            skipped_blank += 1
            continue

        signature = tuple(cleaned_row[col] for col in clean_headers)
        if signature in seen_rows:
            skipped_duplicates += 1
            continue

        seen_rows.add(signature)
        cleaned_rows.append(cleaned_row)

    st.success("Cleaning complete!")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows Kept", len(cleaned_rows))
    c2.metric("Blank Rows Removed", skipped_blank)
    c3.metric("Duplicates Removed", skipped_duplicates)

    st.subheader("Preview (First 20 Rows)")
    st.dataframe(cleaned_rows[:20], use_container_width=True)

    # Prepare downloadable output
    out_io = io.StringIO()
    out_delimiter = "\t" if fname.endswith(".tsv") else ","
    writer = csv.DictWriter(out_io, fieldnames=clean_headers, delimiter=out_delimiter)
    writer.writeheader()
    writer.writerows(cleaned_rows)

    out_bytes = (
        out_io.getvalue().encode("utf-8-sig")
        if out_delimiter == ","
        else out_io.getvalue().encode("utf-8")
    )
    out_name = "cleaned_output.tsv" if fname.endswith(".tsv") else "cleaned_output.csv"
    mime_type = "text/tab-separated-values" if fname.endswith(".tsv") else "text/csv"

    st.download_button(
        label=f"⬇️ Download {out_name}",
        data=out_bytes,
        file_name=out_name,
        mime=mime_type,
    )
