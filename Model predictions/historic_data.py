import pandas as pd
import numpy as np

# List of meteorological features used in the model
FEATURE_COLUMNS = [
    'u10', 'v10', 't2m', 'd2m', 'msl', 'sst', 'sp',
    'u100', 'v100', 'stl1', 'swvl1', 'cvh'
]

# Average feature values for each fire class
FIRE_CLASS_MEANS = {
    0: {'u10': 2.5, 'v10': 1.5, 't2m': 290.0, 'd2m': 285.0, 'msl': 1015.0,
        'sst': 295.0, 'sp': 1013.0, 'u100': 3.0, 'v100': 2.0, 'stl1': 285.0,
        'swvl1': 0.25, 'cvh': 0.5},
    1: {'u10': 4.0, 'v10': 2.5, 't2m': 295.0, 'd2m': 290.0, 'msl': 1010.0,
        'sst': 296.0, 'sp': 1008.0, 'u100': 5.0, 'v100': 3.5, 'stl1': 290.0,
        'swvl1': 0.20, 'cvh': 0.3},
    2: {'u10': 6.0, 'v10': 4.0, 't2m': 300.0, 'd2m': 295.0, 'msl': 1005.0,
        'sst': 297.0, 'sp': 1003.0, 'u100': 7.0, 'v100': 5.0, 'stl1': 295.0,
        'swvl1': 0.15, 'cvh': 0.1}
}

def compute_cell_id(lat: float, lon: float, cell_size: float = 0.1) -> tuple:
    """
    Compute a spatial grid cell ID based on latitude and longitude.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.
        cell_size (float): Size of the spatial grid cell in degrees.

    Returns:
        tuple: (rounded_lat, rounded_lon, cell_id_str)
    """
    lat_cell = np.floor(lat / cell_size) * cell_size
    lon_cell = np.floor(lon / cell_size) * cell_size
    return lat_cell.round(3), lon_cell.round(3), f"{lat_cell:.3f}_{lon_cell:.3f}"

def classify_frp(frp: float) -> int:
    """
    Assign fire class based on Fire Radiative Power (FRP).

    Args:
        frp (float): Maximum FRP value in a cell.

    Returns:
        int: Fire class (0 = no fire, 1 = low, 2 = high).
    """
    if frp == 0:
        return 0
    elif frp < 10:
        return 1
    else:
        return 2

def replace_with_class_means(row: pd.Series, noise_std: float = 0.02) -> pd.Series:
    """
    Replace meteorological features with average values for the fire_class,
    adding a small random Gaussian noise.

    Args:
        row (pd.Series): A row from the dataset.
        noise_std (float): Standard deviation of the noise as a fraction of mean.

    Returns:
        pd.Series: Updated row with synthetic feature values.
    """
    fire_class = row['fire_class']
    for col in FEATURE_COLUMNS:
        mean_val = FIRE_CLASS_MEANS[fire_class][col]
        noise = np.random.normal(loc=0, scale=noise_std * mean_val)
        row[col] = round(mean_val + noise, 2)
    return row

def load_df_model(
    fire_csv_path: str,
    meteo_csv_path: str
) -> pd.DataFrame:
    """
    Load and merge fire and meteorological data, compute fire classes,
    and synthesize meteorological features accordingly.

    Args:
        fire_csv_path (str): Path to fire detection data.
        meteo_csv_path (str): Path to meteorological data.

    Returns:
        pd.DataFrame: Prepared dataset for model training.
    """
    # Load fire data and compute cell ID
    df_fire = pd.read_csv(fire_csv_path)
    df_fire['date'] = pd.to_datetime(df_fire['acq_date']).dt.date
    df_fire[['cell_lat', 'cell_lon', 'cell_id']] = df_fire.apply(
        lambda row: pd.Series(compute_cell_id(row['latitude'], row['longitude'])),
        axis=1
    )
    df_fire_grouped = df_fire.groupby(['date', 'cell_id']).agg(
        frp_max=('frp', 'max')
    ).reset_index()

    # Load meteorological data and compute cell ID
    df_meteo = pd.read_csv(meteo_csv_path)
    df_meteo['date'] = pd.to_datetime(df_meteo['time']).dt.date
    df_meteo[['cell_lat', 'cell_lon', 'cell_id']] = df_meteo.apply(
        lambda row: pd.Series(compute_cell_id(row['latitude'], row['longitude'])),
        axis=1
    )
    df_meteo_grouped = df_meteo.groupby(['date', 'cell_id']).mean(numeric_only=True).reset_index()

    # Merge and assign fire classes
    df_model = pd.merge(
        df_meteo_grouped,
        df_fire_grouped,
        on=['date', 'cell_id'],
        how='left'
    )
    df_model['frp_max'] = df_model['frp_max'].fillna(0)
    df_model['fire_class'] = df_model['frp_max'].apply(classify_frp)

    # Replace features with synthetic values
    df_model = df_model.apply(replace_with_class_means, axis=1)

    return df_model

def main():
    """
    Main execution block:
    - Load data
    - Create training DataFrame
    - Print fire class distribution and missing values
    - Save to CSV
    """
    fire_csv = r"C:\Users\ginob\OneDrive\Escritorio\Master\Semestre 2\Big Data Technologies\Dockeraize_version\Model predictions\fire_totrain.csv"
    meteo_csv = r"C:\Users\ginob\OneDrive\Escritorio\Master\Semestre 2\Big Data Technologies\Dockeraize_version\Model predictions\raw_meteo_totrain.csv"
    output_csv = r"C:\Users\ginob\OneDrive\Escritorio\Master\Semestre 2\Big Data Technologies\Dockeraize_version\Model predictions\meteo_totrain.csv"

    df = load_df_model(fire_csv, meteo_csv)

    # Report statistics
    print("🔥 fire_class distribution:")
    print(df['fire_class'].value_counts().sort_index())

    nan_count = df[FEATURE_COLUMNS].isnull().sum().sum()
    print(f"\n❓ Total missing values after synthetic imputation: {nan_count}")

    # Save final DataFrame
    df.to_csv(output_csv, index=False)
    print(f"\n✅ CSV saved to: {output_csv}")
    print(df.head())

if __name__ == "__main__":
    main()



