import csv
import argparse
from collections import defaultdict
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_barplot(frequencies, output_path, top_n=20):
    # Sort tags by frequency
    sorted_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)[:top_n]
    tags, counts = zip(*sorted_freq)

    # Create horizontal bar plot
    plt.figure(figsize=(10, 8))
    bars = plt.barh(tags, counts, color='skyblue')
    plt.xlabel('Frequency')
    plt.title(f'Top {top_n} Tags')
    plt.gca().invert_yaxis()  # Most frequent on top

    # Add frequency labels inside bars
    for bar in bars:
        width = bar.get_width()
        plt.text(width - 0.5, bar.get_y() + bar.get_height()/2,
                 f'{int(width)}', ha='right', va='center', color='black', fontsize=9)

    plt.tight_layout()

    # Save as JPEG
    if '.' in output_path:
        output_barplot = output_path.rsplit('.', 1)[0] + '_barplot.jpeg'
    else:
        output_barplot = output_path + '_barplot.jpeg'

    plt.savefig(output_barplot, format='jpeg')
    print(f"Bar plot saved to {output_barplot}")
    plt.close()


def get_year_range(input_csv):
    """Scan CSV to find min and max publication years"""
    years = []
    with open(input_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            year = row.get("Publication Year", "").strip()
            if year.isdigit():
                years.append(int(year))
    if not years:
        raise ValueError("No valid 'Publication Year' entries found.")
    return min(years), max(years)

def process_tags(input_csv, gender_csv, year_start, year_end, gender_filter):
    """Process CSV and return tag frequencies based on year and optional gender filter"""
    tag_frequencies = defaultdict(int)
    gender_titles = set()

    # Load titles matching the gender filter (if any)
    if gender_filter.lower() in ['male', 'female']:
        with open(gender_csv, 'r', encoding='utf-8') as gfile:
            reader = csv.DictReader(gfile)
            for row in reader:
                if gender_filter.lower() == 'male' and int(row.get('Male Authors', 0)) > 0:
                    gender_titles.add(row['Title'].strip().lower())
                elif gender_filter.lower() == 'female' and int(row.get('Female Authors', 0)) > 0:
                    gender_titles.add(row['Title'].strip().lower())

    # Process main CSV
    with open(input_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            title = row.get('Title', '').strip().lower()
            try:
                year = int(row.get('Publication Year', 0))
            except ValueError:
                continue

            if year_start <= year <= year_end:
                if gender_filter.lower() == 'total' or title in gender_titles:
                    if 'Manual Tags' in row and row['Manual Tags']:
                        tags = [tag.strip().lower()
                                for tag in row['Manual Tags'].replace(',', ';').split(';')
                                if tag.strip()]
                        for tag in tags:
                            tag_frequencies[tag] += 1
    return tag_frequencies

def save_tag_frequencies(tag_frequencies, output_csv):
    sorted_tags = sorted(tag_frequencies.items(), key=lambda x: x[1], reverse=True)
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Tag', 'Frequency'])
        for tag, count in sorted_tags:
            writer.writerow([tag, count])
    print(f"Tag frequencies saved to {output_csv}")

def generate_wordcloud(tag_frequencies, output_image, colormap='viridis'):
    capitalized_tags = {k.title(): v for k, v in tag_frequencies.items()}
    wordcloud = WordCloud(
        width=1200,
        height=800,
        background_color='white',
        colormap=colormap,
        max_words=100,
        prefer_horizontal=0.9
    ).generate_from_frequencies(capitalized_tags)
    
    wordcloud.to_file(output_image)
    print(f"Word cloud saved to {output_image} (colormap: {colormap})")
    
    plt.figure(figsize=(12, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

def main():
    parser = argparse.ArgumentParser(
        description='Generate tag frequency CSV and word cloud from manual tags.'
    )
    parser.add_argument('-i', '--input', required=True, help='Input CSV file path (e.g., select.csv)')
    parser.add_argument('-g', '--gender-data', required=True, help='CSV with gender author info (LibAssessed)')
    parser.add_argument('-o', '--output-csv', default='tag_frequencies.csv', help='Output CSV filename')
    parser.add_argument('-w', '--wordcloud', default='wordcloud.png', help='Output word cloud image')
    parser.add_argument('--colormap', default='viridis', help='Matplotlib colormap name')

    args = parser.parse_args()

    # Detect year range
    with open(args.input, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        years = [int(row['Publication Year']) for row in reader if row['Publication Year'].isdigit()]
        min_year, max_year = min(years), max(years)

    print(f"Detected publication year range: {min_year} to {max_year}")
    year_start = int(input(f"Enter start year (>= {min_year}): "))
    year_end = int(input(f"Enter end year (<= {max_year}): "))

    # Gender selection
    gender_filter = input("Filter by gender? (Total / Male / Female): ").strip().lower()
    if gender_filter not in ['total', 'male', 'female']:
        print("Invalid choice. Defaulting to total.")
        gender_filter = 'total'

    # Process and save
    frequencies = process_tags(args.input, args.gender_data, year_start, year_end, gender_filter)
    save_tag_frequencies(frequencies, args.output_csv)

    if args.wordcloud:
        generate_wordcloud(frequencies, args.wordcloud, args.colormap)
        generate_barplot(frequencies, args.wordcloud)


if __name__ == "__main__":
    main()
