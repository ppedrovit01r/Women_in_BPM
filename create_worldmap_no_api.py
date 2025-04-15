import pandas as pd
import plotly.express as px
import re
import argparse
from collections import defaultdict

def extract_country(text):
    """Extracts country from strings with 3 possible formats:
    Type 1: 'event-place: Erlangen, Germany' → 'Germany'
    Type 2: 'event-place: Montreal, QC, Canada' → 'Canada'
    Type 3: 'Place: New York, NY, USA Publisher: ...' → 'USA'
    Returns None if no valid country is found.
    """
    if not isinstance(text, str):
        return None
    
    # Normalize text (remove "event-place:" or "Place:" prefixes)
    normalized_text = re.sub(r'^(event-place:|Place:)\s*', '', text, flags=re.IGNORECASE)
    
    # Split into parts and clean
    if "Publisher" in normalized_text:
        normalized_text = normalized_text.split("Publisher")[0].strip()
    parts = [p.strip() for p in normalized_text.split(",")]
    
    # Case 1: Last part is a country (e.g., "..., Germany" or "..., QC, Canada")
    if len(parts) >= 1:
        last_part = parts[-1]
        # Check if the last part is a valid country (simplified)
        if re.fullmatch(r'([A-Za-z\s]+)', last_part):
            country = last_part
            # Standardize country names
            country_mapping = {
                "USA": "United States",
                "US": "United States",
                "UK": "United Kingdom",
                "U.K.": "United Kingdom",
            }
            print("Raw:", text, "→ Extracted:", normalized_text, "→ COUNTRY:", country)
            return country_mapping.get(country, country)
    
    # Case 2: Handle strings with "Publisher" (e.g., "..., USA Publisher...")
    if "Publisher" in normalized_text:
        match = re.search(r',\s*([A-Za-z\s]+)\s*Publisher', normalized_text)
        if match:
            return match.group(1).strip()
    
    return None

def main(input_file):
    # Read CSV (force "Extra" sheet or fallback to first sheet)
    try:
        df = pd.read_csv(input_file, sheet_name="Extra")
    except:
        df = pd.read_csv(input_file)  # Fallback
    
    # Focus ONLY on columns named "Extra" or containing "event-place"
    target_columns = [
        col for col in df.columns 
        if "extra" in col.lower() or "event-place" in col.lower()
    ]
    
    if not target_columns:
        print("ERROR: No column named 'Extra' or containing 'event-place' found!")
        return
    
    print(f"Target columns for country extraction: {target_columns}")
    
    # Extract countries from target columns only
    countries = []
    for col in target_columns:
        countries.extend(df[col].apply(extract_country).dropna())
    
    # Count frequencies
    freq = defaultdict(int)
    for country in countries:
        if country:
            freq[country] += 1
    
    # Save to CSV
    freq_df = pd.DataFrame(list(freq.items()), columns=["country", "frequency"])
    freq_df.to_csv("place_frequency.csv", index=False)
    print("File 'place_frequency.csv' generated successfully!")
    
    # Generate map (if data exists)
    if not freq_df.empty:
        fig = px.scatter_geo(
            freq_df,
            locations="country",
            locationmode="country names",
            size="frequency",
            hover_name="country",
            projection="natural earth",
            title="Scatter World Map by Country Frequency"
        )
        fig.show()
    else:
        print("No valid countries found to generate the map.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Input CSV file")
    args = parser.parse_args()
    main(args.input)