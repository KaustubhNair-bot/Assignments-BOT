import pandas as pd
import re


def clean_medical_data(file_path):
    """The Ultimate Professional Medical Data Cleaner."""
    # Load the data
    df = pd.read_csv(file_path)

    # 1. CRITICAL VALIDATION: Remove rows that are literally useless.
    # No note (transcription) and no summary (description)
    df = df.dropna(subset=["description", "transcription"])

    # 2. COLUMN-BY-COLUMN SANITIZATION
    # We fix the 'Unknowns' so the UI looks professional (No 'NaN' text).
    df["medical_specialty"] = (
        df["medical_specialty"].fillna("Uncategorized").str.strip()
    )
    df["sample_name"] = df["sample_name"].fillna("Untitled Medical Report").str.strip()
    df["keywords"] = df["keywords"].fillna("general, patient notes").str.lower()

    # 3. TEXTUAL SMOOTHING (Deep Cleaning)
    # Medical notes often have \n (newlines) or \t (tabs) from old hospital systems.
    # These 'invisible' characters confuse AI models. We must remove them.
    def deep_clean_text(text):
        if not isinstance(text, str):
            return ""
        # Remove newlines and tabs
        text = text.replace("\n", " ").replace("\t", " ")
        # Remove extra white spaces (change '  ' to ' ')
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # Apply smoothing to the main columns
    df["transcription"] = df["transcription"].apply(deep_clean_text)
    df["description"] = df["description"].apply(deep_clean_text)

    # 4. DATA ENGINEERING FOR AI
    # We create a 'clean_transcription' column for the AI to 'read'.
    df["clean_transcription"] = df["transcription"].str.lower()

    # 5. FINAL SAFETY THRESHOLD
    # Drop any row that is now too short to be useful (less than 20 characters)
    df = df[df["clean_transcription"].str.len() > 20]

    return df
