import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
from historic_data import load_df_model

# Configuration - Input file paths
FIRE_CSV = r"C:\Users\ginob\OneDrive\Escritorio\Master\Semestre 2\Big Data Technologies\Dockeraize_version\Model predictions\fire_totrain.csv"
METEO_CSV = r"C:\Users\ginob\OneDrive\Escritorio\Master\Semestre 2\Big Data Technologies\Dockeraize_version\Model predictions\raw_meteo_totrain.csv"

# List of meteorological features used for training
FEATURE_COLUMNS = [
    'u10', 'v10', 't2m', 'd2m', 'msl', 'sst', 'sp',
    'u100', 'v100', 'stl1', 'swvl1', 'cvh'
]

def prepare_data(df: pd.DataFrame, feature_cols: list) -> tuple:
    """
    Extract the feature matrix (X) and target vector (y) from the dataset.
    Drops rows with missing values in any of the feature columns.

    Args:
        df (pd.DataFrame): Input DataFrame containing features and target.
        feature_cols (list): List of column names to use as features.

    Returns:
        tuple: A tuple (X, y) with the features and labels.
    """
    X = df[feature_cols].dropna()
    y = df.loc[X.index, 'fire_class']
    return X, y

def check_class_distribution(y: pd.Series) -> None:
    """
    Print the number of samples in each fire class.

    Args:
        y (pd.Series): Target vector with fire class labels.
    """
    print("\nSample count per fire_class:")
    print(y.value_counts().sort_index())

def split_and_resample(X: pd.DataFrame, y: pd.Series) -> tuple:
    """
    Split the dataset into training and testing sets, and apply SMOTE 
    to balance the classes in the training set.

    Args:
        X (pd.DataFrame): Feature matrix.
        y (pd.Series): Target vector.

    Returns:
        tuple: (X_train_resampled, X_test, y_train_resampled, y_test)
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    return X_train_resampled, X_test, y_train_resampled, y_test

def train_random_forest(X_train: pd.DataFrame, y_train: pd.Series, n_estimators: int = 100) -> RandomForestClassifier:
    """
    Train a Random Forest classifier using the training data.

    Args:
        X_train (pd.DataFrame): Training feature matrix.
        y_train (pd.Series): Training labels.
        n_estimators (int): Number of trees in the forest (default: 100).

    Returns:
        RandomForestClassifier: The trained classifier.
    """
    clf = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
    clf.fit(X_train, y_train)
    return clf

def evaluate_model(clf: RandomForestClassifier, X_test: pd.DataFrame, y_test: pd.Series) -> None:
    """
    Evaluate the trained classifier on the test set and print evaluation metrics.

    Args:
        clf (RandomForestClassifier): Trained model.
        X_test (pd.DataFrame): Test feature matrix.
        y_test (pd.Series): True labels for the test set.
    """
    y_pred = clf.predict(X_test)
    #print("\nConfusion Matrix:")
    #print(confusion_matrix(y_test, y_pred))
    #print("\nClassification Report:")
    #print(classification_report(y_test, y_pred))

def train_and_return_model(fire_csv: str, meteo_csv: str) -> RandomForestClassifier:
    """
    Load data, preprocess, train a Random Forest model, and return it.

    Args:
        fire_csv (str): Path to fire dataset.
        meteo_csv (str): Path to meteorological dataset.

    Returns:
        RandomForestClassifier: The trained classifier.
    """
    df_model = load_df_model(fire_csv, meteo_csv)
    X, y = prepare_data(df_model, FEATURE_COLUMNS)
    X_train, _, y_train, _ = split_and_resample(X, y)
    clf = train_random_forest(X_train, y_train)
    return clf

def main():
    """
    Main execution flow:
    - Load and prepare data
    - Check class distribution
    - Train and evaluate Random Forest classifier
    """
    df_model = load_df_model(FIRE_CSV, METEO_CSV)
    X, y = prepare_data(df_model, FEATURE_COLUMNS)
    check_class_distribution(y)
    X_train, X_test, y_train, y_test = split_and_resample(X, y)
    clf = train_random_forest(X_train, y_train)
    evaluate_model(clf, X_test, y_test)

if __name__ == "__main__":
    main()





