import numpy as np
import pandas as pd


# --- Sub-functions ---

def _cast_int_2_str(series):
    return (
        series
        .replace("<NA>", np.nan)
        .pipe(lambda s: pd.to_numeric(s, errors="coerce"))
        .astype("Int64")
        .astype(str)
    )


def _cast_float_2_str(series):
    if pd.api.types.is_string_dtype(series):
        series = (
            series
            .str.replace("'", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
    return series.astype(float).map("{:.2f}".format)


def _cast_dt_2_str(series):
    if pd.api.types.is_string_dtype(series):
        try:
            series = pd.to_datetime(series, format="%d.%m.%Y")
        except (ValueError, TypeError):
            return series   # leave untouched if parse fails
    return series.astype(str)



def cast_cols(df1, df2, cols_int_2_str=[], cols_float_2_str=[], cols_dt_2_str=[]):
    df_list = [df1, df2]
    explicit_cols = set(cols_int_2_str) | set(cols_float_2_str) | set(cols_dt_2_str)

    for df in df_list:

        # --- explicit casts ---
        for col in cols_int_2_str:
            print(f"  [int -> str] {col}")
            df[col] = _cast_int_2_str(df[col])

        for col in cols_float_2_str:
            print(f"  [float -> str] {col}")
            df[col] = _cast_float_2_str(df[col])

        for col in cols_dt_2_str:
            print(f"  [dt -> str] {col}")
            df[col] = _cast_dt_2_str(df[col])

        # --- auto-route remaining columns ---
        for col in [c for c in df.columns if c not in explicit_cols]:
            series = df[col]

            if pd.api.types.is_integer_dtype(series):
                print(f"  [auto int -> str] {col} ({series.dtype})")
                df[col] = _cast_int_2_str(series)

            elif pd.api.types.is_float_dtype(series):
                print(f"  [auto float -> str] {col} ({series.dtype})")
                df[col] = _cast_float_2_str(series)

            elif pd.api.types.is_datetime64_any_dtype(series):
                print(f"  [auto dt -> str] {col} ({series.dtype})")
                df[col] = _cast_dt_2_str(series)

            else:
                print(f"  [auto -> str] {col} ({series.dtype})")
                df[col] = series.astype(str)

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
  

def filter_and_sort(df1, df2, filter_dict, max_rows_to_display=3, sort_cols=None,
                    sort_cols_ordering=None):
    """
    Filter and sort two DataFrames in the same way, then display and return them.
    """
    if (sort_cols_ordering is None) and (sort_cols is not None):
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