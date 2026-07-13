import numpy as np
import pandas as pd


def cast_cols(df1, df2, cols_int_2_str=[], cols_float_2_str=[], cols_dt_2_str=[]):

    # --- Sub-functions ---

    def cast_int_2_str(series):
        return (
            series
            .replace("<NA>", np.nan)
            .pipe(lambda s: pd.to_numeric(s, errors="coerce"))
            .astype("Int64")
            .astype(str)
            .str.strip()
        )

    def cast_float_2_str(series):
        if pd.api.types.is_string_dtype(series):
            series = (
                series
                .str.replace("'", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
        return series.astype(float).map("{:.2f}".format).str.strip()

    def cast_dt_2_str(series):
        if pd.api.types.is_string_dtype(series):
            try:
                series = pd.to_datetime(series, format="%d.%m.%Y")
            except (ValueError, TypeError):
                return series.str.strip()
        return series.astype(str).str.strip()

    # --- Main logic ---

    explicit_cols = set(cols_int_2_str) | set(cols_float_2_str) | set(cols_dt_2_str)

    for df in [df1, df2]:

        # --- explicit casts ---
        for col in cols_int_2_str:
            print(f"  [int -> str] {col}")
            df[col] = cast_int_2_str(df[col])

        for col in cols_float_2_str:
            print(f"  [float -> str] {col}")
            df[col] = cast_float_2_str(df[col])

        for col in cols_dt_2_str:
            print(f"  [dt -> str] {col}")
            df[col] = cast_dt_2_str(df[col])

        # --- auto-route remaining columns ---
        for col in [c for c in df.columns if c not in explicit_cols]:
            series = df[col]

            if pd.api.types.is_integer_dtype(series):
                print(f"  [auto int -> str] {col} ({series.dtype})")
                df[col] = cast_int_2_str(series)

            elif pd.api.types.is_float_dtype(series):
                print(f"  [auto float -> str] {col} ({series.dtype})")
                df[col] = cast_float_2_str(series)

            elif pd.api.types.is_datetime64_any_dtype(series):
                print(f"  [auto dt -> str] {col} ({series.dtype})")
                df[col] = cast_dt_2_str(series)

            else:
                print(f"  [auto -> str] {col} ({series.dtype})")
                df[col] = series.astype(str).str.strip()

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
  

def filter_and_sort(df1, df2, filter_dict, select_cols=None, 
                    max_rows_to_display=3, sort_cols=None,
                    sort_cols_ordering=None, ):
    """
    Filter and sort two DataFrames in the same way, then display and return them.

    Parameters
    ----------
    df1, df2            : DataFrames to process.
    filter_dict         : Dict of {col: value} filters passed to filter_rows_by_dict.
    max_rows_to_display : Max rows shown (default 3).
    sort_cols           : Columns to sort by.
    sort_cols_ordering  : List of booleans (True=asc). Defaults to all True.
    select_cols         : str or list of str - columns to keep before displaying.
                          If a single column is selected, prints value + type per row
                          instead of a DataFrame display.
    """
    if (sort_cols_ordering is None) and (sort_cols is not None):
        sort_cols_ordering = [True] * len(sort_cols)

    # --- normalize select_cols ---
    if isinstance(select_cols, str):
        select_cols = [select_cols]

    def _process(df, label):
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

        # --- apply column selection ---
        if select_cols:
            missing = [c for c in select_cols if c not in df_sorted.columns]
            if missing:
                print(f"  [WARNING] Columns not found and skipped: {missing}")
            valid_cols = [c for c in select_cols if c in df_sorted.columns]
            df_display = df_sorted[valid_cols]
        else:
            df_display = df_sorted

        df_head = df_display.head(max_rows_to_display)
        print(f"[{label}] Displaying max {max_rows_to_display} of {len(df_sorted)} row(s)")

        # --- single-column: show value + type per row ---
        if select_cols and len(valid_cols) == 1:
            col = valid_cols[0]
            print(f"  Column: '{col}'")
            for i, val in enumerate(df_head[col]):
                print(f"  row {i} -> repr : {repr(val)}")
                print(f"          type : {type(val).__name__}")
        else:
            display(df_head)

        return df_sorted

    df1_out = _process(df1, "df1")
    df2_out = _process(df2, "df2")

    return df1_out, df2_out

def rename_columns(df, rename_dict):
    missing = [col for col in rename_dict if col not in df.columns]
    if missing:
        print(f"  Warning: these columns were not found and skipped -> {missing}")

    df = df.rename(columns=rename_dict)
    print(f"  Successfully renamed {len(rename_dict) - len(missing)} column(s).")
    return df