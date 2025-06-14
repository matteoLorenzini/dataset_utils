import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

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

def select_diverse_subset(df, label_column, domain_column, text_column, n_samples_per_group=10):
    """Selects a diverse subset from each (label, dominio) group using clustering."""
    selected = []
    for (label, domain), group in df.groupby([label_column, domain_column]):
        if len(group) <= n_samples_per_group:
            selected.append(group)
            continue
        # Compute TF-IDF vectors
        tfidf = TfidfVectorizer()
        X = tfidf.fit_transform(group[text_column])
        # Cluster and select closest to centers
        kmeans = KMeans(n_clusters=n_samples_per_group, random_state=42)
        kmeans.fit(X)
        centers = kmeans.cluster_centers_
        closest, _ = pairwise_distances_argmin_min(centers, X)
        selected.append(group.iloc[closest])
    return pd.concat(selected).reset_index(drop=True)

def create_unlabelled_test_dataset(
    source_files,
    batch_num=0,
    batch_size=100,
    output_dir='../../../dataset/CH_IT/active_learning_label/unlabelled_batches'
):
    """
    Creates an unlabelled test dataset by taking a batch of rows from each source file.

    Args:
        source_files (list of str): List of CSV file paths to sample from.
        batch_num (int): Which batch to extract (0 = first 100, 1 = 101-200, ...).
        batch_size (int): Number of rows per batch per file.
        output_dir (str): Directory to save the batch CSV.
    """
    os.makedirs(output_dir, exist_ok=True)
    batch_dfs = []
    start = batch_num * batch_size
    end = start + batch_size

    for file_path in source_files:
        try:
            df = pd.read_csv(file_path)
            batch_df = df.iloc[start:end].copy()
            batch_df['source_file'] = os.path.basename(file_path)
            batch_dfs.append(batch_df)
            print(f"Selected rows {start+1} to {end} from {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    if batch_dfs:
        combined = pd.concat(batch_dfs, ignore_index=True)
        output_path = os.path.join(output_dir, f'unlabelled_batch_{batch_num+1}.csv')
        combined.to_csv(output_path, index=False)
        print(f"Saved batch {batch_num+1} to {output_path}")
    else:
        print("No data to save for this batch.")

if __name__ == "__main__":
    # --- Configuration ---
    file_path = '../../../dataset/CH_IT/total/all_cleaned_transformed.csv'
    text_column = 'descrizione'
    label_column = 'label'
    domain_column = 'dominio'
    num_initial_samples = 250  # Set to None to use the minimum group size, or set a max per group
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
            train_set_path = '../../../dataset/CH_IT/active_learning_label/dataset_active_learning.csv'
            if not os.path.exists(train_set_path):
                initial_train_df.to_csv(train_set_path, index=False)
                print("Balanced initial training set saved to: dataset_active_learning.csv")
            else:
                print("Initial training set already exists. Not overwriting.")

            # --- Create unlabelled test dataset batch ---
            unlabelled_sources = [
                '../../../dataset/CH_IT/architettura/architettura_cleaned_transformed.csv',
                '../../../dataset/CH_IT/archeologia/archeologia_cleaned_transformed.csv',
                '../../../dataset/CH_IT/opere_arte_visiva/opere_arte_visiva_cleaned_transformed.csv'
            ]
            # Set the batch number here (0 for first 100, 1 for 101-200, etc)
            batch_num = 0
            create_unlabelled_test_dataset(unlabelled_sources, batch_num=batch_num)

        else:
            print("Could not create an initial balanced training subset.")
    else:
        print("No annotated data loaded.")