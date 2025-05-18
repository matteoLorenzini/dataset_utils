import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def load_annotated_data(file_path, text_column, label_column, domain_column):
    """Loads the annotated dataset from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        return df[[text_column, label_column, domain_column]].dropna()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None

def select_balanced_subset(df, label_column, domain_column, text_column, n_samples=None, min_samples_per_group=5):
    """Selects a balanced subset for initial active learning training across (label, dominio) groups."""
    group_sizes = df.groupby([label_column, domain_column]).size()
    if group_sizes.empty:
        print("No groups found for balancing.")
        return pd.DataFrame()
    min_count = group_sizes.min()
    if n_samples:
        min_count = min(min_count, n_samples)
    min_count = max(min_count, min_samples_per_group)
    print(f"Sampling {min_count} samples per (label, dominio) group.")

    balanced_df = (
        df.groupby([label_column, domain_column], group_keys=False)
        .apply(lambda x: x.sample(min(len(x), min_count), random_state=42))
        .reset_index(drop=True)
    )
    print("Balanced group sizes:")
    print(balanced_df.groupby([label_column, domain_column]).size())
    return balanced_df

def select_meaningful_subset(
    df,
    label_column,
    text_column,
    domain_column=None,
    strategy='stratified',
    n_samples=None,
    min_samples_per_class=10
):
    """
    Selects a meaningful subset of the annotated data for initial active learning training.

    Args:
        df (pandas.DataFrame): Annotated DataFrame with text and labels.
        label_column (str): Name of the label column.
        text_column (str): Name of the text column.
        domain_column (str, optional): Name of the domain column to consider for balancing.
        strategy (str, optional): Strategy for subset selection.
            'stratified': Maintains the class distribution of the original dataset.
            'balanced': Selects an equal number of samples per class (up to n_samples).
            'random': Selects a random subset.
            Defaults to 'stratified'.
        n_samples (int, optional): Maximum number of samples to select. If None, selects based on the strategy. Defaults to None.
        min_samples_per_class (int, optional): Minimum number of samples to select per class for 'balanced' and 'stratified'. Defaults to 10.

    Returns:
        pandas.DataFrame: Subset of the annotated data.
    """
    if df is None or df.empty:
        print("Error: Input DataFrame is empty.")
        return pd.DataFrame()

    if domain_column:
        group_cols = [label_column, domain_column]
    else:
        group_cols = [label_column]

    group_counts = df.groupby(group_cols).size()
    unique_groups = group_counts.index.tolist()

    if strategy == 'stratified':
        stratified_samples = []
        for group in unique_groups:
            group_df = df
            if isinstance(group, tuple):
                for col, val in zip(group_cols, group):
                    group_df = group_df[group_df[col] == val]
            else:
                group_df = group_df[group_df[group_cols[0]] == group]
            n = max(min_samples_per_class, int(len(group_df) * 0.1))
            if n_samples is not None:
                n = min(n, int(n_samples * (len(group_df) / len(df))))
            stratified_samples.append(group_df.sample(n=min(n, len(group_df)), random_state=42))
        subset_df = pd.concat(stratified_samples).sample(frac=1, random_state=42).reset_index(drop=True)
        print(f"Selected {len(subset_df)} samples using stratified sampling.")

    elif strategy == 'balanced':
        balanced_samples = []
        n_per_group = n_samples // len(unique_groups) if n_samples else min(group_counts)
        n_per_group = max(n_per_group, min_samples_per_class)
        for group in unique_groups:
            group_df = df
            if isinstance(group, tuple):
                for col, val in zip(group_cols, group):
                    group_df = group_df[group_df[col] == val]
            else:
                group_df = group_df[group_df[group_cols[0]] == group]
            balanced_samples.append(group_df.sample(n=min(n_per_group, len(group_df)), random_state=42))
        subset_df = pd.concat(balanced_samples).sample(frac=1, random_state=42).reset_index(drop=True)
        print(f"Selected {len(subset_df)} samples using balanced sampling (up to {n_per_group} per group).")

    elif strategy == 'random':
        n = n_samples if n_samples is not None else int(0.1 * len(df))
        subset_df = df.sample(n=min(n, len(df)), random_state=42).reset_index(drop=True)
        print(f"Selected {len(subset_df)} samples using random sampling.")

    else:
        print(f"Warning: Unknown selection strategy '{strategy}'. Using stratified sampling.")
        return select_meaningful_subset(
            df, label_column, text_column, domain_column, strategy='stratified',
            n_samples=n_samples, min_samples_per_class=min_samples_per_class
        )

    if subset_df.empty:
        print("Warning: Could not select any meaningful samples based on the criteria.")

    return subset_df

if __name__ == "__main__":
    # --- Configuration ---
    file_path = '../../dataset/CH_IT/total/all_cleaned_transformed.csv'
    text_column = 'descrizione'
    label_column = 'label'
    domain_column = 'dominio'
    num_initial_samples = 100  # Set to None to use the minimum group size, or set a max per group
    min_samples_per_group = 5

    # --- Load the annotated data ---
    annotated_df = load_annotated_data(file_path, text_column, label_column, domain_column)

    if annotated_df is not None and not annotated_df.empty:
        print(f"Loaded {len(annotated_df)} annotated samples.")
        print("Label/domain distribution:")
        print(annotated_df.groupby([label_column, domain_column]).size())

        # --- Select the balanced subset ---
        initial_train_df = select_balanced_subset(
            annotated_df,
            label_column,
            domain_column,
            text_column,
            n_samples=num_initial_samples,
            min_samples_per_group=min_samples_per_group
        )

        if not initial_train_df.empty:
            print("\nInitial training subset:")
            print(f"Selected {len(initial_train_df)} samples for initial training.")
            print("Label/domain distribution in the initial subset:")
            print(initial_train_df.groupby([label_column, domain_column]).size())

            # --- Example: Train a simple model on the initial subset (for demonstration) ---
            vectorizer = TfidfVectorizer()
            X_train = vectorizer.fit_transform(initial_train_df[text_column])
            y_train = initial_train_df[label_column]

            model = LogisticRegression()
            model.fit(X_train, y_train)

            # --- Example: Prepare remaining data for active learning (as the unlabeled pool) ---
            remaining_df = annotated_df[~annotated_df.index.isin(initial_train_df.index)]
            print(f"\n{len(remaining_df)} samples remaining for active learning.")

            # Save the balanced initial training set
            initial_train_df.to_csv('../../dataset/CH_IT/active_learning_label/dataset_active_learning.csv', index=False)
            print("Balanced initial training set saved to: dataset_active_learning.csv")
        else:
            print("Could not create an initial balanced training subset.")
    else:
        print("No annotated data loaded.")