import pandas as pd

def compare_dfs(df_old, df_new):

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