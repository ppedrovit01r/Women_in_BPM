
import os
import json
import sys


def generate_author_list(content, total_authors):
    # Concatenate first and last names and append to total_authors
    for author in content['authors']:
        total_authors.append(author.get('fistName', '') + ' ' + author.get('familyName', ''))


def main(year):
    directory = os.getcwd() + '\\assessed\\'
    total_authors = []

    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), 'r') as f:
            if filename == 'assessed.txt':
                continue

            content = json.loads(f.read())

            if content['publicationYear'] == year:
                generate_author_list(content, total_authors)
            elif year == 'all':
                generate_author_list(content, total_authors)

    # Remove the duplicated names
    distinct_authors = list(dict.fromkeys(total_authors))

    # Compare all the names to eliminate those which contain each other.
    # Example: Alice Smith with Alice Smith Davis
    for author in enumerate(distinct_authors):
        for index, author2 in enumerate(distinct_authors):
            if (author in author2 or author2 in author) and (author != author2):
                del distinct_authors[index]

    print(len(distinct_authors))


if __name__ == "__main__":
    main(str(sys.argv[1]))
