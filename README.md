# dataset_utils

## Overview

`dataset_utils` is a collection of scripts and utilities for preparing, cleaning, balancing, and managing datasets for active learning and text classification tasks, with a focus on Italian cultural heritage datasets.

---

## Features

- **Data Cleaning:**  
  Scripts for cleaning and transforming raw CSV datasets (e.g., removing duplicates, handling missing values, text normalization).

- **Balanced Subset Creation:**  
  Functions to create balanced or diverse initial training sets for active learning, ensuring fair representation across label and domain combinations.

- **Active Learning Support:**  
  Utilities to generate unlabelled test batches for iterative active learning experiments.

- **Model Training Examples:**  
  Example scripts for training baseline models (e.g., TF-IDF + Logistic Regression) and integrating with modern NLP models (e.g., BERT via Hugging Face).

---

## Usage

### 1. Data Cleaning

Use `cleaning_it.py` to clean and transform your raw CSV files:

```bash
python dataset_creation/data_cleaning/cleaning_it.py
```

### 2. Create Balanced/Diverse Training Set

Use `active_learning_annotation.py` to create a balanced or diverse initial training set and generate unlabelled test batches:

```bash
python dataset_creation/data_subset/active_learning_annotation.py
```

- The script will save:
  - `dataset_active_learning.csv` (initial labelled set)
  - `unlabelled_batch_1.csv`, `unlabelled_batch_2.csv`, ... (unlabelled pools for active learning)

### 3. Active Learning Loop

- Train your model on `dataset_active_learning.csv`.
- Query and annotate samples from the unlabelled batches.
- Append newly labelled samples to `dataset_active_learning.csv`.
- Repeat as needed, generating new unlabelled batches for each iteration.

---

## Sampling Strategies

- **Balanced Sampling:** Randomly samples the same number of records from each `(label, dominio)` group.
- **Diverse Sampling:** Uses clustering (KMeans on TF-IDF vectors) to select a diverse set of records from each group.
- **Custom Filtering:** You can further filter for text length, keywords, or model uncertainty.

---

## Example: Appending New Labels

```python
import pandas as pd

# After annotation
new_labels_df = pd.DataFrame([...])  # Your newly labelled records
train_set_path = '../../../dataset/CH_IT/active_learning_label/dataset_active_learning.csv'
train_df = pd.read_csv(train_set_path)
updated_train_df = pd.concat([train_df, new_labels_df], ignore_index=True)
updated_train_df.to_csv(train_set_path, index=False)
```

---

## Notes

- Do **not** overwrite `dataset_active_learning.csv` after the initial run; always append new labels.
- Only use the batch creation function for new unlabelled pools in subsequent rounds.
- For best results in text classification, consider using BERT-based models with Hugging Face Transformers.

---

## License

This project is licensed under the [GNU GPL-3.0 License](https://www.gnu.org/licenses/gpl-3.0.html).

---

## Contact

For questions or contributions, open an issue or pull request on GitHub.