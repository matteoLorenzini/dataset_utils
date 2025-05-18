import pandas as pd
import re
import string
import unicodedata
from sklearn.preprocessing import StandardScaler, LabelEncoder
from nltk.corpus import stopwords

# Download necessary NLTK resources (run this once)
import nltk
try:
    stopwords.words('italian')
except LookupError:
    nltk.download('stopwords')

# Define Italian stopwords globally
ITALIAN_STOPWORDS = set(stopwords.words('italian'))

def fix_encoding(text):
    """
    Fixes encoding issues in a string by attempting to re-encode and decode it.

    Args:
        text (str): The input string with potential encoding issues.

    Returns:
        str: The fixed string.
    """
    try:
        return text.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        # In case it's already correctly encoded or cannot be fixed
        return text

def clean_italian_description(text):
    """
    Cleans a single Italian description string by removing noise, handling contractions,
    punctuation, and Italian stopwords.

    Args:
        text (str): The input Italian description string.

    Returns:
        str: The cleaned Italian description string.
    """
    if pd.isna(text):  # Handle NaN values
        return ""

    # Fix encoding issues
    text = fix_encoding(text)

    # Convert to lowercase
    text = text.lower()

    # Remove parentheses and their content
    text = re.sub(r'\([^)]*\)', '', text)

    # Handle missing spaces around apostrophes and contractions
    text = re.sub(r"(\b[a-zA-Z])'([a-z])", r"\1 \2", text)  # Replace apostrophe with a space between words

    # Normalize text to remove accents
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')

    # Remove punctuation and replace with spaces
    text = re.sub(r'[^\w\s]', ' ', text)

    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Tokenize and remove stopwords
    text_tokens = text.split()
    filtered_tokens = [word for word in text_tokens if word not in ITALIAN_STOPWORDS]

    # Join tokens back into a single string
    cleaned_text = " ".join(filtered_tokens).strip()

    return cleaned_text

def transform_data(df):
    """
    Transforms the data for machine learning, including scaling numerical features
    and encoding categorical variables.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The transformed DataFrame.
    """
    # Scale numerical features
    scaler = StandardScaler()
    if 'numerical_feature' in df.columns:  # Replace with actual numerical column names
        df['numerical_feature_scaled'] = scaler.fit_transform(df[['numerical_feature']])

    # Encode categorical variables
    encoder = LabelEncoder()
    if 'categorical_feature' in df.columns:  # Replace with actual categorical column names
        df['categorical_feature_encoded'] = encoder.fit_transform(df['categorical_feature'])

    return df

def validate_data(df):
    """
    Validates the data to ensure accuracy and consistency.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        bool: True if the data is valid, False otherwise.
    """
    # Check for missing values
    if df.isnull().sum().any():
        print("Warning: Missing values detected.")
        return False

    # Check for duplicate rows
    if df.duplicated().any():
        print("Warning: Duplicate rows detected.")
        return False

    # Additional validation checks can be added here
    return True

def load_and_clean_italian_descriptions_from_csv(file_paths):
    """
    Loads Italian text data from multiple CSV files, performs cleaning on the 'descrizione' column
    (and 'titolo' if present), removes duplicate descriptions, transforms the data, validates it,
    and saves the DataFrame with cleaned and transformed columns.

    Args:
        file_paths (list of str): A list containing the paths to the CSV files.
    """
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path)
            print(f"\nFirst 5 rows of the DataFrame from {file_path}:")
            print(df.head())

            # Ensure the required column exists
            if 'descrizione' not in df.columns:
                print(f"Warning: 'descrizione' column not found in {file_path}. Skipping this file.")
                continue

            # Debug: Check for missing values
            print(f"\nMissing values in {file_path}:")
            print(df.isnull().sum())

            # Drop rows with missing descrizione
            drop_cols = ['descrizione']
            # If titolo exists, drop rows with missing titolo as well
            if 'titolo' in df.columns:
                drop_cols.append('titolo')
            df = df.dropna(subset=drop_cols)
            print(f"Rows remaining after dropping missing values in {drop_cols}: {len(df)}")

            # Clean the 'descrizione' column
            df['descrizione'] = df['descrizione'].apply(clean_italian_description)

            # Clean the 'titolo' column if it exists
            if 'titolo' in df.columns:
                df['titolo'] = df['titolo'].apply(clean_italian_description)

            # Remove duplicate descriptions
            df = df.drop_duplicates(subset=['descrizione'], keep='first')

            # Transform the data
            df = transform_data(df)

            # Validate the data
            if not validate_data(df):
                print(f"Validation failed for {file_path}. Proceeding to save the cleaned data.")

            # Save the DataFrame with cleaned and transformed columns
            output_file = file_path.replace('.csv', '_cleaned_transformed.csv')
            df.to_csv(output_file, index=False)
            print(f"Cleaned and transformed data saved to: {output_file}")

        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    # Updated file paths
    file_paths = [
        '../../../dataset/CH_IT/architettura/architettura.csv',
        '../../../dataset/CH_IT/architettura/A.csv',
        '../../../dataset/CH_IT/archeologia/archeologia.csv',
        '../../../dataset/CH_IT/archeologia/Ar.csv',
        '../../../dataset/CH_IT/dea/demoetnoantropologici.csv',
        '../../../dataset/CH_IT/opere_arte_visiva/opere_arte_visiva.csv',
        '../../../dataset/CH_IT/opere_arte_visiva/museid_oa_parthenos.csv',
        '../../../dataset/CH_IT/opere_arte_visiva/vaw.csv',
        '../../../dataset/CH_IT/total/all.csv'      
    ]
    load_and_clean_italian_descriptions_from_csv(file_paths)