import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def process_curated_results(input_file):
    try:
        # 1. Load the original dataset
        df = pd.read_csv(input_file)

        # 2. Define categories based on 0.75 probability
        # Create a temporary column to facilitate counting and grouping
        def categorize(row):
            if row['Probability'] < 0.75:
                return 'unknown'
            elif str(row['Gender']).lower() == 'female':
                return 'female'
            elif str(row['Gender']).lower() == 'male':
                return 'male'
            else:
                return 'unknown'

        df['Category'] = df.apply(categorize, axis=1)

        # 3. Group by author to consolidate metadata and the list of articles
        # We use the defined 'Category' to ensure the author is counted correctly
        grouped = df.groupby('Author Name').agg({
            'First Name': 'first',
            'Gender': 'first', # Keep the original for the CSV
            'Probability': 'first',
            'Reliable': 'first',
            'Category': 'first', # Category based on the user's criterion
            'Article Title': list
        }).reset_index()

        grouped['Publication_Count'] = grouped['Article Title'].apply(len)

        # 4. Prepare rows for the CSV in the requested format
        # Format: [Base Data] + [Article 1, Article 2...] + [$]
        rows_for_csv = []
        for _, row in grouped.iterrows():
            base_info = [
                row['Author Name'], row['First Name'], row['Gender'],
                row['Probability'], row['Reliable'], row['Publication_Count']
            ]
            articles = row['Article Title']
            rows_for_csv.append(base_info + articles + ["$"])

        # Create dynamic header
        max_articles = grouped['Publication_Count'].max()
        header = ['Author Name', 'First Name', 'Gender', 'Probability', 'Reliable', 'Publication_Count']
        header += [f'Article_{i+1}' for i in range(max_articles)] + ['End_Marker']

        # Generate the Final CSV
        curated_df = pd.DataFrame(rows_for_csv)
        curated_df.to_csv('curated_authors.csv', index=False, header=header)

        # 5. Calculate the requested final statistics
        total_authors = len(grouped)
        males = len(grouped[grouped['Category'] == 'male'])
        females = len(grouped[grouped['Category'] == 'female'])
        unknowns = len(grouped[grouped['Category'] == 'unknown'])

        print("-" * 30)
        print("SUMMARY STATISTICS")
        print("-" * 30)
        print(f"Total Unique Authors: {total_authors}")
        print(f"Males (Prob >= 75%):  {males}")
        print(f"Females (Prob >= 75%): {females}")
        print(f"Unknown (Prob < 75%):  {unknowns}")
        print("-" * 30)
        print("File 'curated_authors.csv' has been generated successfully.")

        # 6. Generate a bar chart for gender distribution
        gender_counts = pd.Series({
            'Males': males,
            'Females': females,
            'Unknown': unknowns
        })

        plt.figure(figsize=(8, 6))
        ax = sns.barplot(x=gender_counts.index, y=gender_counts.values, palette='viridis')

        # Add numbers and percentages on top of the bars
        for p in ax.patches:
            height = p.get_height()
            if total_authors > 0:
                percentage = 100 * height / total_authors
            else:
                percentage = 0
            ax.annotate(f'{int(height)} ({percentage:.1f}%)',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=10,
                        xytext=(0, 5), textcoords='offset points')

        plt.title('Distribution of Authors by Gender Category (1997-2024)')
        plt.xlabel('Gender Category')
        plt.ylabel('Number of Authors')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig('gender_distribution_chart.png')
        plt.show()
        print("Gender distribution chart saved as 'gender_distribution_chart.png'.")

    except Exception as e:
        print(f"Error during processing: {e}")

if __name__ == '__main__':
    process_curated_results('authors_data.csv')
