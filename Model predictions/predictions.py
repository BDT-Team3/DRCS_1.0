import pandas as pd
from datetime import datetime, timedelta
from predictive_model import FEATURE_COLUMNS, train_and_return_model

def load_meteorological_data(csv_path: str) -> pd.DataFrame:
    """
    Load meteorological data from a CSV file and parse the time column.

    Args:
        csv_path (str): Path to the input CSV file.

    Returns:
        pd.DataFrame: DataFrame with parsed time column.
    """
    df = pd.read_csv(csv_path)
    df['time'] = pd.to_datetime(df['time'])
    return df

def remap_time_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace the time column with a new range of dates starting from today.

    Args:
        df (pd.DataFrame): Input DataFrame with a 'time' column.

    Returns:
        pd.DataFrame: DataFrame with updated 'time' column.
    """
    unique_times = sorted(df['time'].unique())
    start_date = datetime.today().date()
    new_times = [start_date + timedelta(days=i) for i in range(len(unique_times))]
    time_map = dict(zip(unique_times, new_times))
    df['time'] = df['time'].map(time_map)
    return df

def prepare_features(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    """
    Select and clean feature columns by dropping rows with missing values.

    Args:
        df (pd.DataFrame): Input DataFrame.
        feature_cols (list): List of feature column names.

    Returns:
        pd.DataFrame: Cleaned DataFrame with only the feature columns.
    """
    return df[feature_cols].dropna()

def add_predictions(df: pd.DataFrame, features: pd.DataFrame, model) -> pd.DataFrame:
    """
    Add predictions to the original DataFrame as a new column.

    Args:
        df (pd.DataFrame): Original DataFrame.
        features (pd.DataFrame): Clean feature DataFrame used for predictions.
        model: Trained classification model.

    Returns:
        pd.DataFrame: DataFrame with added 'fire_prediction' column.
    """
    valid_indices = features.index
    predictions = model.predict(features)
    df.loc[valid_indices, 'fire_prediction'] = predictions
    return df

def save_forecast(df: pd.DataFrame, output_path: str) -> None:
    """
    Save the final DataFrame with predictions to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame to be saved.
        output_path (str): File path for saving the CSV.
    """
    df.to_csv(output_path, index=False)

def main():
    input_csv = r"C:\Users\ginob\OneDrive\Escritorio\Master\Semestre 2\Big Data Technologies\Model predictions\meteo_df_ok.csv"
    output_csv = r"C:\Users\ginob\OneDrive\Escritorio\Master\Semestre 2\Big Data Technologies\Model predictions\meteo_forecast_predictions.csv"

    # Load and preprocess data
    df_meteo = load_meteorological_data(input_csv)
    df_meteo = remap_time_column(df_meteo)
    
    # Prepare features and predict
    df_features = prepare_features(df_meteo, FEATURE_COLUMNS)
    clf = train_and_return_model()
    df_meteo = add_predictions(df_meteo, df_features, clf)

    # Save results
    save_forecast(df_meteo, output_csv)

if __name__ == "__main__":
    main()
