from pathlib import Path
import os
from google.colab import files
import pandas as pd

def read_sample_file(
    country, sf_folder_prefix, sf_name_prefix,
    file_match_number=0, download=False, display_number_rows=1):

    # Build folder path
    folder_path_object = Path(f"{sf_folder_prefix}{country.lower()}")

    # Get the first CSV whose name starts with the prefix
    matches = list(folder_path_object.glob(f"{sf_name_prefix}*.txt"))
    if not matches:
        raise FileNotFoundError(f"No CSV files starting with '{sf_name_prefix}' found.")

    csv_path = matches[file_match_number]
    print(f"Reading file: {csv_path}")

    # Read the CSV
    df = pd.read_csv(
        csv_path,
        sep="\t",          # or sep="," / "\t" depending on what you see
        engine="python"   # more forgiving parser
    )
    display(df.head(display_number_rows))

    if download:
      excel_path = f"Temporary/{sf_name_prefix}.xlsx"

      excel_dir = os.path.dirname(excel_path)
      if excel_dir:  # Only create if there's a directory path
        os.makedirs(excel_dir, exist_ok=True)

      df.to_excel(excel_path, index=False)
      files.download(excel_path)

    return df