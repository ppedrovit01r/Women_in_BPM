import csv
import json
import urllib.parse
import re

import requests
import unidecode

json_object = {
    "key": "",
    "type": "a",
    "publicationYear": "a",
    "author": "a",
    "title": "x",
    "publicationTitle": "a",
    "isbn": "a",
    "issn": "a",
    "doi": "y",
    "url": "url",
    "date": "a",
    "place": "a",
    "manualTags": "",
    "automaticTags": "",
    "authors": [],
    "citationCount": 0,
    "hasWomenAuthor": False,
    "publisherLocation": ""
}


def fill_json_data(content):
    '''Fill json data based on .csv exported from Zotero tool'''
    json_object["authors"].clear()
    json_object["key"] = content[0]
    json_object["type"] = content[1]
    json_object["publicationYear"] = content[2]
    json_object["author"] = content[3]
    json_object["title"] = content[4]
    json_object["publicationTitle"] = content[5]
    json_object["isbn"] = content[6]
    json_object["issn"] = content[7]
    json_object["doi"] = content[8]
    json_object["url"] = content[9]
    json_object["date"] = content[11]
    json_object["place"] = content[27]
    json_object["manualTags"] = content[39]
    json_object["automaticTags"] = content[40]
    return json_object


def write_json(entry):
    json_name = entry["key"] + '.json'
    with open('assessed/' + json_name, 'w') as f:
        json.dump(entry, f)

    with open('assessed/assessed.txt', 'a') as f:
        f.write(entry["key"] + '\n')


def add_to_not_assessed_list(entry):
    with open('not_assessed.txt', 'a') as f:
        if not 'Key' in entry:
            f.write(entry + '\n')


def verify_if_already_assessed(entry):
    with open('assessed/assessed.txt') as f:
        if entry in f.read():
            return True
        else:
            return False


def try_to_find_doi_extra_data(entry):
    doi = ''
    if entry != '' and 'DOI' in entry:
        doi = entry.split('DOI: ')[1]
    return doi


def parse_valid_name(name):
    if ' ' in name:
        return unidecode.unidecode(name.split()[0])
    return unidecode.unidecode(name)


def verify_if_has_complete_name(entry):
    names = entry[3].split(';')
    regex = "[A-Z][.]"  # regex to exclude entries that has, for example "L." or "L.H."
    if ',' in names[0] and re.search(regex, names[0].split(', ')[1].split(' ')[0]) is None:
        json_object = fill_json_data(entry)
        women = False
        first_iteration = True
        for name in names:
            first_name = name.split(', ')[1].split(' ')[0]
            last_name = name.split(', ')[0]
            genderize_response = requests.get(
                'https://api.genderize.io?name=' +
                parse_valid_name(first_name) + '&apikey=58b45a60539fc8bbbf2252f697c00698'
            )

            parsed_gender = json.loads(genderize_response.content)
            gender_assessed = False

            if parsed_gender['probability'] < 0.75 or parsed_gender['count'] < 2:
                print('Could not determine gender properly', parsed_gender['probability'], parsed_gender['count'])
            else:
                gender_assessed = True
                if parsed_gender['gender'] == 'female':
                    women = True
                print('Gender assessed: ', parsed_gender['gender'])

            author_assessed = {
                "fistName": unidecode.unidecode(first_name),
                "familyName": unidecode.unidecode(last_name),
                "gender": parsed_gender['gender'] if gender_assessed else 'NA',
                "probability": parsed_gender['probability'],
                "count": parsed_gender['count'],
                "affiliation": [],
                "sequence": 'first' if first_iteration is True else 'additional'
            }
            first_iteration = False
            json_object["authors"].append(author_assessed)

        json_object["hasWomenAuthor"] = women

        write_json(json_object)
        return True
    else:
        add_to_not_assessed_list(entry[0])
        return False


def main():
    with open('womenLib.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile)

        for row in spamreader:
            doi = row[8]

            if verify_if_already_assessed(row[0]):
                continue

            if doi == '':
                doi = try_to_find_doi_extra_data(row[35])
                if doi == '':
                    verify_if_has_complete_name(row)
                    continue

            response = requests.get('https://api.crossref.org/works/' + urllib.parse.quote(doi.encode('utf8')))
            if response.status_code == 200:
                parsed_response = json.loads(response.content)
                if 'author' in parsed_response['message']:
                    authors = parsed_response['message']['author']
                elif 'editor' in parsed_response['message']:
                    authors = parsed_response['message']['editor']
                else:
                    add_to_not_assessed_list(row[0])
                    continue

                json_object = fill_json_data(row)

                women = False
                for author in authors:
                    if not 'given' in author and not 'family' in author:
                        continue
                    if not 'given' in author:
                        author_assessed = {
                            "fistName": 'None',
                            "familyName": unidecode.unidecode(author.get('family', 'None')),
                            "gender": 'NA',
                            "probability": 0,
                            "count": 0,
                            "affiliation": author.get('affiliation', 'None'),
                            "sequence": author.get('sequence', 'None')
                        }
                        json_object["authors"].append(author_assessed)
                        continue

                    first_name = author['given']
                    if '-' in first_name:
                        first_name = first_name.split('-')[0]
                    if 'Dr.' in first_name or 'Mr.' in first_name:
                        first_name = first_name.split('. ')[1]
                    if ' ' in first_name:
                        first_name = first_name.split(' ')[0]
                    genderize_response = requests.get(
                        'https://api.genderize.io?name=' +
                        parse_valid_name(first_name) + '&apikey=58b45a60539fc8bbbf2252f697c00698'
                    )

                    if genderize_response.status_code == 429:
                        print("Maximum requests today.")
                        exit()

                    parsed_gender = json.loads(genderize_response.content)
                    gender_assessed = False

                    if parsed_gender['probability'] < 0.75 or parsed_gender['count'] < 2:
                        print('Could not determine gender properly',
                              parsed_gender['probability'], parsed_gender['count'])
                    else:
                        gender_assessed = True
                        if parsed_gender['gender'] == 'female':
                            women = True
                        print('Gender assessed: ', parsed_gender['gender'])

                    author_assessed = {
                        "fistName": unidecode.unidecode(first_name),
                        "familyName": unidecode.unidecode(author['family']),
                        "gender": parsed_gender['gender'] if gender_assessed else 'NA',
                        "probability": parsed_gender['probability'],
                        "count": parsed_gender['count'],
                        "affiliation": author['affiliation'],
                        "sequence": author['sequence']
                    }

                    json_object["authors"].append(author_assessed)

                json_object["hasWomenAuthor"] = women
                message = parsed_response["message"]
                json_object["citationCount"] = message.get("is-referenced-by-count", -1)
                json_object["publisherLocation"] = message.get("publisher-location", "")

                write_json(json_object)

            else:
                print('Could not find DOI for article named: ' + row[4])
                add_to_not_assessed_list(row[0])

            print(row)


if __name__ == "__main__":
    main()
