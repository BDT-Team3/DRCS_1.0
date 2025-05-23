import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
from historic_data import load_df_model

# List of meteorological features used for training
FEATURE_COLUMNS = [
    'u10', 'v10', 't2m', 'd2m', 'msl', 'sst', 'sp',
    'u100', 'v100', 'stl1', 'swvl1', 'cvh'
]

def prepare_data(df: pd.DataFrame, feature_cols: list) -> tuple:
    """
    Extract features and target variable from the input DataFrame.

    Args:
        df (pd.DataFrame): Input dataset with meteorological variables.
        feature_cols (list): List of column names to be used as features.

    Returns:
        tuple: Features (X) and target (y) as pandas DataFrames/Series.
    """
    X = df[feature_cols].dropna()
    y = df.loc[X.index, 'fire_class']
    return X, y

def check_class_distribution(y: pd.Series) -> None:
    """
    Print the distribution of fire_class values.

    Args:
        y (pd.Series): Target variable containing fire class labels.
    """
    print("\nSample count per fire_class:")
    print(y.value_counts().sort_index())

def split_and_resample(X: pd.DataFrame, y: pd.Series) -> tuple:
    """
    Split the dataset into training and testing sets and apply SMOTE to balance classes.

    Args:
        X (pd.DataFrame): Feature matrix.
        y (pd.Series): Target variable.

    Returns:
        tuple: Resampled training set and original test set.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    return X_train_resampled, X_test, y_train_resampled, y_test

def train_random_forest(X_train: pd.DataFrame, y_train: pd.Series, n_estimators: int = 100) -> RandomForestClassifier:
    """
    Train a Random Forest classifier on the training data.

    Args:
        X_train (pd.DataFrame): Training features.
        y_train (pd.Series): Training labels.
        n_estimators (int): Number of trees in the forest.

    Returns:
        RandomForestClassifier: Trained classifier.
    """
    clf = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
    clf.fit(X_train, y_train)
    return clf

def evaluate_model(clf: RandomForestClassifier, X_test: pd.DataFrame, y_test: pd.Series) -> None:
    """
    Evaluate the trained model on the test set and print metrics.

    Args:
        clf (RandomForestClassifier): Trained classifier.
        X_test (pd.DataFrame): Test features.
        y_test (pd.Series): True labels for the test set.
    """
    y_pred = clf.predict(X_test)
    #print("Confusion Matrix:")
    #print(confusion_matrix(y_test, y_pred))
    #print("\nClassification Report:")
    #print(classification_report(y_test, y_pred))

def train_and_return_model() -> RandomForestClassifier:
    """
    Convenience function that trains the model and returns it.

    Returns:
        RandomForestClassifier: Trained Random Forest model.
    """
    df_model = load_df_model()
    X, y = prepare_data(df_model, FEATURE_COLUMNS)
    X_train, _, y_train, _ = split_and_resample(X, y)
    clf = train_random_forest(X_train, y_train)
    return clf

def main():
    """
    Run the full training pipeline:
    - Load data
    - Prepare features
    - Check class balance
    - Split and resample
    - Train model
    - Evaluate on test set
    """
    df_model = load_df_model()
    X, y = prepare_data(df_model, FEATURE_COLUMNS)
    check_class_distribution(y)
    X_train, X_test, y_train, y_test = split_and_resample(X, y)
    clf = train_random_forest(X_train, y_train)
    evaluate_model(clf, X_test, y_test)

if __name__ == "__main__":
    main()




