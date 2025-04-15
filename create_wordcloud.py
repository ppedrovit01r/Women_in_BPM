import csv
import argparse
from collections import defaultdict
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def process_tags(input_csv):
    """Process CSV and return tag frequencies"""
    tag_frequencies = defaultdict(int)
    
    with open(input_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            if 'Manual Tags' in row and row['Manual Tags']:
                tags = [tag.strip().lower() 
                       for tag in row['Manual Tags'].replace(',', ';').split(';') 
                       if tag.strip()]
                
                for tag in tags:
                    tag_frequencies[tag] += 1
    return tag_frequencies

def save_tag_frequencies(tag_frequencies, output_csv):
    """Save sorted tag frequencies to CSV"""
    sorted_tags = sorted(tag_frequencies.items(), key=lambda x: x[1], reverse=True)
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Tag', 'Frequency'])
        for tag, count in sorted_tags:
            writer.writerow([tag, count])
    print(f"Tag frequencies saved to {output_csv}")

def generate_wordcloud(tag_frequencies, output_image, colormap='viridis'):
    """Generate and save word cloud image"""
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
    
    # Display
    plt.figure(figsize=(12, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

def main():
    parser = argparse.ArgumentParser(
        description='Generate tag frequency CSV and word cloud from manual tags.'
    )
    parser.add_argument(
        '-i', '--input', 
        required=True, 
        help='Input CSV file path (e.g., select.csv)'
    )
    parser.add_argument(
        '-o', '--output-csv', 
        default='tag_frequencies.csv',
        help='Output CSV filename (default: tag_frequencies.csv)'
    )
    parser.add_argument(
        '-w', '--wordcloud', 
        default='wordcloud.png',
        help='Generate word cloud (specify output image name, e.g., wordcloud.png)'
    )
    parser.add_argument(
        '--colormap', 
        default='viridis',
        help='Matplotlib colormap name (default: viridis)'
    )
    
    args = parser.parse_args()
    
    # Process tags and save CSV (always)
    frequencies = process_tags(args.input)
    save_tag_frequencies(frequencies, args.output_csv)
    
    # Generate word cloud if requested
    if args.wordcloud:
        generate_wordcloud(frequencies, args.wordcloud, args.colormap)

if __name__ == "__main__":
    main()