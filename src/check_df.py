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