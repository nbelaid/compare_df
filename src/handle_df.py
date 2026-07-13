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


def filter_and_sort(df1, df2, filter_dict, select_cols=None,
                    max_rows_to_display=3, sort_cols=None, sort_cols_ordering=None):
    """
    Filter and sort two DataFrames in the same way, then display and return them.

    Parameters
    ----------
    df1, df2            : DataFrames to process.
    filter_dict         : {col: value} or {col: [values]} - scalar values are auto-wrapped.
    select_cols         : str or list of str - columns to display.
                          Single column -> prints repr + type per row instead of DataFrame.
    max_rows_to_display : Max rows shown (default 3).
    sort_cols           : Column(s) to sort by.
    sort_cols_ordering  : List of booleans (True=asc). Defaults to all True.
    """

    # --- sub-function: filter rows ---
    def _filter(df, filter_dict):
        mask = pd.Series(True, index=df.index)
        for col, val in filter_dict.items():
            if not isinstance(val, (list, tuple, set)):  # auto-wrap scalars
                val = [val]
            mask &= df[col].isin(val)
        return df[mask].reset_index(drop=True)

    # --- normalize inputs ---
    if sort_cols is not None and sort_cols_ordering is None:
        sort_cols_ordering = [True] * len(sort_cols)
    if isinstance(select_cols, str):
        select_cols = [select_cols]

    def _process(df, label):
        try:
            df = df.reset_index(drop=True)
        except Exception:
            pass

        df_out = _filter(df, filter_dict)

        if sort_cols:
            df_out = df_out.sort_values(by=sort_cols, ascending=sort_cols_ordering)

        # --- column selection ---
        valid_cols = None
        if select_cols:
            missing = [c for c in select_cols if c not in df_out.columns]
            if missing:
                print(f"  [WARNING] Columns not found and skipped: {missing}")
            valid_cols = [c for c in select_cols if c in df_out.columns]

        df_display = df_out[valid_cols] if valid_cols else df_out
        df_head    = df_display.head(max_rows_to_display)

        print(f"[{label}] Displaying max {max_rows_to_display} of {len(df_out)} row(s)")

        # --- single column: show repr + type ---
        if valid_cols and len(valid_cols) == 1:
            col = valid_cols[0]
            print(f"  Column: '{col}'")
            for i, val in enumerate(df_head[col]):
                print(f"  row {i} -> repr: {repr(val)}")
                print(f"           type: {type(val).__name__}")
        else:
            display(df_head)

        return df_out

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