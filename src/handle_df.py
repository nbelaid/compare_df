import numpy as np
import pandas as pd


def cast_cols(df1, df2, cols_int_2_str=[], cols_float_2_str=[], cols_dt_2_str=[]):
    df_list = [df1, df2]
    for df in df_list:
        # Column cast int to str
        for col in cols_int_2_str:
            print(f"Trying to cast col: {col}.")
            df[col] = df[col].replace('<NA>', np.nan)
            df[col] = df[col].astype(float)
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            df[col] = df[col].astype(str)

        # Column cast float to str
        for col in cols_float_2_str:
            print(f"Trying to cast col: {col}.")
            if pd.api.types.is_string_dtype(df[col]):
                df[col] = (
                    df[col]
                    .str.replace("'", "", regex=False)
                    .str.replace(" ", "", regex=False)
                    .str.replace(",", ".", regex=False)
                )
            df[col] = df[col].astype(float).map("{:.2f}".format)

        # Column cast to date
        for col in cols_dt_2_str:
            print(f"Trying to cast col: {col}.")
            if pd.api.types.is_string_dtype(df[col]):
                try: # try to convert using the given format
                    df[col] = pd.to_datetime(df[col], format="%d.%m.%Y")
                except (ValueError, TypeError):
                    continue
            df[col] = df[col].astype(str)

    return df1, df2


def filter_rows_by_dict(df, filter_dict, reset_index=True):
    """
    Filter df where each column in filter_dict is in its allowed values.
    filter_dict: {col_name: [allowed_vals, ...]}
    """
    mask = pd.Series(True, index=df.index)

    for col, allowed_vals in filter_dict.items():
        mask &= df[col].isin(allowed_vals)

    result = df[mask]
    return result.reset_index(drop=True) if reset_index else result
  

def filter_and_sort(df1, df2, filter_dict, sort_cols,
                    sort_cols_ordering=None, max_rows_to_display=10):
    """
    Filter and sort two DataFrames in the same way, then display and return them.
    """
    if sort_cols_ordering is None:
        sort_cols_ordering = [True] * len(sort_cols)

    def _process(df):
        # BigFrames DataFrames may have no index
        try:
            df = df.reset_index(drop=True)
        except Exception:
            pass  # Already has a valid index - skip

        df_filtered = filter_rows_by_dict(df, filter_dict)

        # Guard against empty sort_cols, as can raise in BigFrames
        if sort_cols:
            df_sorted = df_filtered.sort_values(by=sort_cols, ascending=sort_cols_ordering)
        else:
            df_sorted = df_filtered

        print(f"Display a maximum of {max_rows_to_display}")
        display(df_sorted.head(max_rows_to_display))
        return df_sorted

    df1_out = _process(df1)
    df2_out = _process(df2)

    return df1_out, df2_out


def rename_columns(df, rename_dict):
    missing = [col for col in rename_dict if col not in df.columns]
    if missing:
        print(f"  Warning: these columns were not found and skipped -> {missing}")

    df = df.rename(columns=rename_dict)
    print(f"  Successfully renamed {len(rename_dict) - len(missing)} column(s).")
    return df