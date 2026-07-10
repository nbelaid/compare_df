from xmlrpc import client

from google.cloud import storage
from pathlib import Path
import os
from google.colab import files

import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def load_sample_files(bucket_name, sub_bucket, country, sf_folder_prefix):
    folder_path = f"{sub_bucket}/{sf_folder_prefix}{country.lower()}"

    extract_dir = f"{sf_folder_prefix}{country.lower()}"  # local subfolder to download into
    os.makedirs(extract_dir, exist_ok=True)

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # List all blobs (files) in the folder
    blobs = bucket.list_blobs(prefix=folder_path + "/")

    # Download each file
    for blob in blobs:
        # Skip if it's the folder itself (empty name after prefix)
        if blob.name.endswith('/'):
            continue

        # Get the filename (without the folder path)
        filename = blob.name.split('/')[-1]
        local_path = os.path.join(extract_dir, filename)

        # print(f"Downloading {blob.name} to {local_path}...")
        blob.download_to_filename(local_path)
        # print(f"Downloaded {filename}")

    print(f"All files downloaded to {extract_dir}")


def read_sample_file(
    country, sf_folder_prefix, sf_name_prefix,
    file_match_number=0, download=False, display_number_rows=3):

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
    print(f"Length: {len(df)} rows.")
    display(df.head(display_number_rows))

    if download:
      excel_path = f"Temporary/{sf_name_prefix}.xlsx"

      excel_dir = os.path.dirname(excel_path)
      if excel_dir:  # Only create if there's a directory path
        os.makedirs(excel_dir, exist_ok=True)

      df.to_excel(excel_path, index=False)
      files.download(excel_path)

    return df