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


def compare_dfs_rows(df1, df2, name1="df_old", name2="df_new", exclude_cols=[]):

    # --- 1. Common columns in df_old order, minus excluded ones ---
    excluded = set(exclude_cols)
    common_cols = [col for col in df1.columns if col in set(df2.columns) - excluded]

    a = df1[common_cols].copy()
    b = df2[common_cols].copy()  # df_new is now reordered to match df_old

    # --- 2. Fix dtype mismatches (e.g. pyarrow vs object) ---
    for col in common_cols:
        if a[col].dtype != b[col].dtype:
            a[col] = a[col].astype(str)
            b[col] = b[col].astype(str)

    # --- 3. Sort both (by common cols, in df_old order) ---
    a = a.sort_values(common_cols).reset_index(drop=True)
    b = b.sort_values(common_cols).reset_index(drop=True)

    # --- 4. Compare rows ---
    merged = pd.merge(a, b, on=common_cols, how="outer", indicator=True)
    common = merged[merged["_merge"] == "both"].drop(columns="_merge")
    only_a = merged[merged["_merge"] == "left_only"].drop(columns="_merge")
    only_b = merged[merged["_merge"] == "right_only"].drop(columns="_merge")

    # --- 5. Print report ---
    n1, n2, nc = len(a), len(b), len(common)
    if exclude_cols:
        print(f"Excluded columns: {exclude_cols}")
    print(f"Common columns ({len(common_cols)}) in {name1} order: {common_cols}")
    print(f"\n{name1}: {n1} rows  |  {name2}: {n2} rows")
    print(f"Common rows:  {nc}  ({nc/n1*100:.1f}% of {name1}  |  {nc/n2*100:.1f}% of {name2})")
    print(f"Only in {name1}: {len(only_a)}  |  Only in {name2}: {len(only_b)}")

    print(f"\n--- 5 rows only in {name1} ---")
    print(only_a[common_cols].head(5).to_string(index=False) if len(only_a) else "none")

    print(f"\n--- 5 rows only in {name2} ---")
    print(only_b[common_cols].head(5).to_string(index=False) if len(only_b) else "none")



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