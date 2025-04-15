import csv
import argparse
from collections import defaultdict

def process_tags(input_csv, output_csv):
    # Dictionary to store tag frequencies
    tag_frequencies = defaultdict(int)
    
    with open(input_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            if 'Manual Tags' in row and row['Manual Tags']:
                # Split tags by ';' or ',' and strip whitespace
                tags = [tag.strip().lower() 
                       for tag in row['Manual Tags'].replace(',', ';').split(';') 
                       if tag.strip()]
                
                # Count each tag
                for tag in tags:
                    tag_frequencies[tag] += 1
    
    # Sort tags by frequency (descending)
    sorted_tags = sorted(tag_frequencies.items(), key=lambda x: x[1], reverse=True)
    
    # Write to output CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Tag', 'Frequency'])  # Header row
        
        for tag, count in sorted_tags:
            writer.writerow([tag, count])
    
    print(f"Tag frequencies saved to {output_csv}")

def main():
    parser = argparse.ArgumentParser(description='Process manual tags from CSV and generate frequency report.')
    parser.add_argument('-i', '--input', required=True, help='Input CSV file path')
    parser.add_argument('-o', '--output', default='tag_frequencies.csv', 
                       help='Output CSV file path (default: tag_frequencies.csv)')
    
    args = parser.parse_args()
    
    process_tags(args.input, args.output)

if __name__ == "__main__":
    main()