import pandas as pd


def read_csv(file):
    """
    Reads the uploaded CSV file and returns a DataFrame.
    """
    return pd.read_csv(file)


def get_feature_summary(dataframe):

    numerical = dataframe.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    categorical = dataframe.select_dtypes(
        include=["object"]
    ).columns.tolist()

    boolean_like = []

    for column in dataframe.columns:
        unique_values = dataframe[column].dropna().unique()

        if len(unique_values) == 2:
            boolean_like.append(column)

    return {
        "numerical": numerical,
        "categorical": categorical,
        "boolean_like": boolean_like
    }



def get_dataset_summary(dataframe):
    """
    Returns basic information about the dataset.
    """
    feature_summary = get_feature_summary(dataframe)
    summary = {
        
        "rows": len(dataframe),
        "columns": len(dataframe.columns),

        "column_names": dataframe.columns.tolist(),

        "data_types": dataframe.dtypes.astype(str).to_dict(),
        "feature_summary": feature_summary,
        "missing_values": dataframe.isnull().sum().to_dict(),

        "preview": dataframe.head().to_dict(orient="records"),

        "dataset_quality": {
            "duplicate_rows": int(dataframe.duplicated().sum()),

            "total_missing_values": int(dataframe.isnull().sum().sum()),

            "missing_percentage": round(
                (
                    dataframe.isnull().sum().sum()
                    / (dataframe.shape[0] * dataframe.shape[1])
                ) * 100,
                2,
            ),

            "memory_usage_mb": round(
                dataframe.memory_usage(deep=True).sum() / (1024 * 1024),
                2,
            ),
        },
    }

    return summary