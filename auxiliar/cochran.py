import pandas as pd
import math
import random

def simple_sampling(input_file, output_file, precision=0.85, confidence_z=1.96):
    """
    Performs simple random sampling based on Cochran's formula.
    
    Parameters:
    - input_file: Path to the source CSV file.
    - output_file: Path where the sample will be saved.
    - precision: Desired precision level (default 0.85 for 85%).
    - confidence_z: Z-score for the confidence level (default 1.96 for 95%).
    """
    try:
        # 1. Load the intermediate file
        # Pandas reads based on the fixed header, even with variable column counts
        df = pd.read_csv(input_file)
        N = len(df)

        if N == 0:
            print("The file is empty.")
            return

        # 2. Cochran Parameters
        p = 0.5             # Maximum proportion (conservative approach)
        e = 1 - precision   # Margin of error (e.g., 0.15 for 85% precision)
        Z = confidence_z    # Z-score (e.g., 1.96 for 95% confidence)

        # 3. Cochran Calculation
        # Step 1: n0 for infinite population
        n0 = (Z**2 * p * (1 - p)) / (e**2)

        # Step 2: Adjustment for finite population (N)
        n = n0 / (1 + ((n0 - 1) / N))
        final_sample_size = math.ceil(n)

        # 4. Calculation breakdown for human verification
        print("--- Calculation Breakdown (Cochran) ---")
        print(f"Total Population (N): {N}")
        print(f"Confidence Level (Z): {Z} (95%)")
        print(f"Margin of Error (e): {e:.2f} ({(1-e)*100:.0f}% precision)")
        print(f"1. n0 Calculation: ({Z}² * {p} * {1-p}) / {e}² = {n0:.4f}")
        print(f"2. Finite Adjustment: {n0:.4f} / (1 + ({n0:.4f} - 1) / {N}) = {n:.4f}")
        print(f"3. Final Sample Size (rounded up): {final_sample_size}")
        print("-" * 43)

        # 5. Simple Random Selection
        if final_sample_size > N:
            print("Warning: Calculated sample size is larger than the population. Returning all records.")
            sample_df = df
        else:
            # random_state for reproducibility
            sample_df = df.sample(n=final_sample_size, random_state=42) 

        # 6. Save Result
        sample_df.to_csv(output_file, index=False)
        print(f"Success! Sample of {len(sample_df)} records saved to '{output_file}'.")

    except Exception as err:
        print(f"Error during processing: {err}")

if __name__ == '__main__':
    # Execute with the requested parameters
    simple_sampling("inter_women.csv", "final_women_sample.csv") # add values for precision and confidence if needed, separeted by colons.