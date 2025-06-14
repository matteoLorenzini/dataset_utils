# Active Learning Data Preparation & Workflow

## Overview

This document explains the workflow and usage of the `active_learning_annotation.py` script for preparing datasets for active learning in text classification tasks.  
It covers how to create a balanced or diverse initial training set, generate unlabelled test batches, and how to use these files in an active learning loop.

---

## 1. Script Purpose

- **Creates a balanced initial training set** (`dataset_active_learning.csv`) from your annotated data, ensuring fair representation of each `(label, dominio)` group.
- **Optionally creates a diverse initial training set** using clustering (see `select_diverse_subset`).
- **Trains a simple model** (TF-IDF + Logistic Regression) on this initial set (for demonstration).
- **Creates an unlabelled test set** (`unlabelled_batch_1.csv`, etc.) by sampling batches from your domain datasets. This simulates the pool of unlabelled data you will use for querying in active learning.

---

## 2. Sampling Strategies

- **Balanced Sampling:**  
  Uses `select_balanced_subset` to randomly sample the same number of records from each `(label, dominio)` group.
- **Diverse Sampling:**  
  Uses `select_diverse_subset` to select a diverse set of records from each group using KMeans clustering on TF-IDF vectors.

### Other possible improvements:
- **Length/Quality Filtering:** Prefer longer or more informative texts.
- **Keyword/Topic Filtering:** Prefer records containing certain keywords or belonging to certain topics.
- **Uncertainty Sampling:** (after initial model) Select records where the model is least confident.

---

## 3. Workflow Diagram

```plaintext
   ┌──────────────────────────────┐
   │  Annotated Dataset (CSV)     │
   └─────────────┬────────────────┘
                 │
                 ▼
   ┌─────────────────────────────┐
   │ load_annotated_data()       │
   └─────────────┬───────────────┘
                 │
                 ▼
   ┌─────────────────────────────┐
   │ select_balanced_subset()    │
   │ or select_diverse_subset()  │
   │  (by label & dominio)       │
   └─────────────┬───────────────┘
                 │
                 ├───────────────► Save as
                 │                dataset_active_learning.csv
                 │
                 ▼
   ┌─────────────────────────────┐
   │ Train model (TF-IDF + LR)   │
   └─────────────┬───────────────┘
                 │
                 ▼
   ┌─────────────────────────────┐
   │ Remaining data (pool)       │
   │ for active learning         │
   └─────────────┬───────────────┘
                 │
                 ▼
   ┌─────────────────────────────┐
   │ create_unlabelled_test_     │
   │ dataset()                   │
   │ (batch from each domain)    │
   └─────────────┬───────────────┘
                 │
                 ▼
   ┌─────────────────────────────┐
   │ Save as                     │
   │ unlabelled_batch_{n}.csv    │
   └─────────────────────────────┘
```

---

## 4. How to Use in Active Learning

### A. Initial Run
- Run the script to create:
  - `dataset_active_learning.csv` (your initial labelled set)
  - `unlabelled_batch_1.csv` (your first unlabelled pool)

### B. Active Learning Loop
1. **Train your model** on `dataset_active_learning.csv`.
2. **Query**: Select the most informative samples from `unlabelled_batch_1.csv`.
3. **Annotate**: Manually label the queried samples.
4. **Update**: Append newly labelled samples to `dataset_active_learning.csv`.
5. **Remove**: Remove those samples from `unlabelled_batch_1.csv`.
6. **Repeat**: For the next round, generate `unlabelled_batch_2.csv` by setting `batch_num = 1` in the script.

### C. Important!
- **Do NOT overwrite** `dataset_active_learning.csv` after the initial run.  
- Only use the batch creation function for new unlabelled pools in subsequent rounds.

---

## 5. Example: Appending New Labels

```python
# After annotation
new_labels_df = pd.DataFrame([...])  # Your newly labelled records
train_set_path = '../../../dataset/CH_IT/active_learning_label/dataset_active_learning.csv'
train_df = pd.read_csv(train_set_path)
updated_train_df = pd.concat([train_df, new_labels_df], ignore_index=True)
updated_train_df.to_csv(train_set_path, index=False)
```

---

## 6. Improving Subset Selection

- **Random sampling** is used by default for balanced subsets.
- **Diverse sampling** (via `select_diverse_subset`) uses clustering to pick more representative and varied records.
- You can further filter for quality (e.g., minimum text length) or use other strategies as needed.

---

## 7. Summary Table

| Step                        | Action                                                                 |
|-----------------------------|------------------------------------------------------------------------|
| Initial script run          | Creates `dataset_active_learning.csv` and first unlabelled batch       |
| Each AL iteration           | Train, query, annotate, append to `dataset_active_learning.csv`        |
| Need more unlabelled data   | Only run batch creation for new unlabelled batch, do NOT overwrite training set |

---
