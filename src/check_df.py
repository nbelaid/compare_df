import pandas as pd

def compare_dfs_stats(df_old, df_new):

    # --- Row stats ---
    rows_old = len(df_old)
    rows_new = len(df_new)
    row_diff = rows_new - rows_old
    row_pct  = ((rows_new - rows_old) / rows_old * 100) if rows_old != 0 else float('inf')

    # --- Column stats ---
    cols_old = set(df_old.columns)
    cols_new = set(df_new.columns)

    only_in_old = cols_old - cols_new
    only_in_new = cols_new - cols_old
    in_both     = cols_old & cols_new

    # --- Report ---
    print("=" * 40)
    print("ROW STATISTICS")
    print("=" * 40)
    print(f"  df_old rows : {rows_old:,}")
    print(f"  df_new rows : {rows_new:,}")
    print(f"  Difference  : {row_diff:+,}  ({row_pct:+.2f}%)")

    print()
    print("=" * 40)
    print("COLUMN STATISTICS")
    print("=" * 40)
    print(f"  df_old columns : {len(cols_old)}")
    print(f"  df_new columns : {len(cols_new)}")
    print(f"  In common      : {len(in_both)}")
    print(f"  Only in df_old : {len(only_in_old)} -> {sorted(only_in_old) or 'none'}")
    print(f"  Only in df_new : {len(only_in_new)} -> {sorted(only_in_new) or 'none'}")


def compare_dfs_rows(df1: pd.DataFrame, df2: pd.DataFrame,
                       df1_name: str = "DataFrame 1",
                       df2_name: str = "DataFrame 2") -> dict:
    """
    Compare two pandas DataFrames:
      - Keeps only common columns
      - Sorts both by common columns
      - Reports common rows count and percentage
      - Shows up to 5 rows exclusive to each DataFrame

    Parameters
    ----------
    df1       : First  DataFrame
    df2       : Second DataFrame
    df1_name  : Label for df1 (used in display)
    df2_name  : Label for df2 (used in display)

    Returns
    -------
    dict with keys:
        'common_columns'   : list of shared column names
        'common_rows'      : DataFrame of rows present in both
        'only_in_df1'      : DataFrame of rows only in df1
        'only_in_df2'      : DataFrame of rows only in df2
        'stats'            : dict with counts and percentages
    """

    # ------------------------------------------------------------------
    # 1. Common columns
    # ------------------------------------------------------------------
    common_cols = sorted(set(df1.columns) & set(df2.columns))

    if not common_cols:
        raise ValueError("The two DataFrames share NO common columns.")

    dropped_df1 = [c for c in df1.columns if c not in common_cols]
    dropped_df2 = [c for c in df2.columns if c not in common_cols]

    df1_c = df1[common_cols].copy()
    df2_c = df2[common_cols].copy()

    # ------------------------------------------------------------------
    # 2. Sort both by all common columns
    # ------------------------------------------------------------------
    df1_c = df1_c.sort_values(by=common_cols).reset_index(drop=True)
    df2_c = df2_c.sort_values(by=common_cols).reset_index(drop=True)

    # ------------------------------------------------------------------
    # 3. Find common / exclusive rows  (merge-based, handles duplicates)
    # ------------------------------------------------------------------
    df1_c["_src"] = "df1"
    df2_c["_src"] = "df2"

    merged = pd.merge(
        df1_c.drop(columns="_src"),
        df2_c.drop(columns="_src"),
        on=common_cols,
        how="outer",
        indicator=True
    )

    common_rows  = merged[merged["_merge"] == "both"].drop(columns="_merge")
    only_in_df1  = merged[merged["_merge"] == "left_only"].drop(columns="_merge")
    only_in_df2  = merged[merged["_merge"] == "right_only"].drop(columns="_merge")

    df1_c = df1_c.drop(columns="_src")
    df2_c = df2_c.drop(columns="_src")

    # ------------------------------------------------------------------
    # 4. Stats
    # ------------------------------------------------------------------
    n_df1    = len(df1_c)
    n_df2    = len(df2_c)
    n_common = len(common_rows)
    n_only1  = len(only_in_df1)
    n_only2  = len(only_in_df2)

    pct_of_df1 = (n_common / n_df1  * 100) if n_df1  else 0.0
    pct_of_df2 = (n_common / n_df2  * 100) if n_df2  else 0.0
    pct_of_union = (n_common / (n_df1 + n_df2 - n_common) * 100) \
                   if (n_df1 + n_df2 - n_common) else 0.0

    stats = {
        f"rows_in_{df1_name}"  : n_df1,
        f"rows_in_{df2_name}"  : n_df2,
        "common_rows"          : n_common,
        f"pct_of_{df1_name}"   : round(pct_of_df1,   2),
        f"pct_of_{df2_name}"   : round(pct_of_df2,   2),
        "pct_of_union"         : round(pct_of_union, 2),
        f"only_in_{df1_name}"  : n_only1,
        f"only_in_{df2_name}"  : n_only2,
    }

    # ------------------------------------------------------------------
    # 5. Pretty print
    # ------------------------------------------------------------------
    sep = "=" * 60

    print(sep)
    print("  DATAFRAME COMPARISON REPORT")
    print(sep)

    print(f"\n{'COLUMNS':}")
    print(f"  Common columns ({len(common_cols)})  : {common_cols}")
    if dropped_df1:
        print(f"  Dropped from {df1_name}  : {dropped_df1}")
    if dropped_df2:
        print(f"  Dropped from {df2_name}  : {dropped_df2}")

    print(f"\nROW COUNTS")
    print(f"  {df1_name:<20}: {n_df1:>6} rows")
    print(f"  {df2_name:<20}: {n_df2:>6} rows")
    print(f"  Common rows         : {n_common:>6} rows  "
          f"({pct_of_df1:.1f}% of {df1_name} | "
          f"{pct_of_df2:.1f}% of {df2_name} | "
          f"{pct_of_union:.1f}% of union)")

    print(f"\n  Only in {df1_name:<15}: {n_only1:>6} rows")
    print(f"  Only in {df2_name:<15}: {n_only2:>6} rows")

    # Sample exclusive rows
    sample = 5
    print(f"\n{sep}")
    print(f"  UP TO {sample} ROWS ONLY IN '{df1_name.upper()}'")
    print(sep)
    print(only_in_df1.head(sample).to_string(index=False)
          if n_only1 else "  (none)")

    print(f"\n{sep}")
    print(f"  UP TO {sample} ROWS ONLY IN '{df2_name.upper()}'")
    print(sep)
    print(only_in_df2.head(sample).to_string(index=False)
          if n_only2 else "  (none)")

    print(f"\n{sep}\n")

    return {
        "common_columns" : common_cols,
        "df1_sorted"     : df1_c,
        "df2_sorted"     : df2_c,
        "common_rows"    : common_rows,
        "only_in_df1"    : only_in_df1,
        "only_in_df2"    : only_in_df2,
        "stats"          : stats,
    }


def check_primary_key(df, columns, verbose=False):
    if isinstance(columns, str):
        columns = [columns]
    else:
        columns = list(columns)
    
    total_rows = len(df)

    # Create mask for null values
    null_mask = df[columns].isna().any(axis=1)
    null_count = null_mask.sum()

    # Create null dataframe
    null_df = df[null_mask].copy()
    if null_count > 0:
        null_df = null_df.sort_values(by=columns, na_position='first')

    # Create mask for duplicate values
    duplicate_mask = df.duplicated(subset=columns, keep=False)
    duplicate_count = duplicate_mask.sum()
    unique_count = df[columns].drop_duplicates().shape[0]
    
    # Create duplicate dataframe
    duplicates_df = df[duplicate_mask].copy()
    
    if duplicate_count > 0:
        duplicates_df = duplicates_df.sort_values(by=columns)
    
    is_valid_pk = (null_count == 0) and (duplicate_count == 0)
    
    analysis_dict = {
        'is_valid_pk': is_valid_pk,
        'total_rows': total_rows,
        'unique_count': unique_count,
        'duplicate_count': duplicate_count,
        'null_count': null_count,
    }

    if verbose:
        for key, value in analysis_dict.items():
            print(f"{key}: {value}")

    return (
        analysis_dict, 
        duplicates_df if duplicate_count > 0 else None,
        null_df if null_count > 0 else None
    )