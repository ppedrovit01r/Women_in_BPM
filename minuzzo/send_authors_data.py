import os
import requests
import json

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('ELK_TOKEN')


def register_sent(entry):
    '''Register all the already sent files in a .txt'''
    with open('sent.txt', 'a') as f:
        f.write(entry + '\n')


def verify_if_already_sent(entry):
    with open('sent.txt') as f:
        if entry in f.read():
            return True
        else:
            return False


def main():
    directory = os.getcwd() + '\\assessed\\'

    index = 'authors'
    url = 'http://localhost:9200/{}/_doc'.format(index)
    headers = {
        'content-type': "application/json",
        'authorization': f"Basic {TOKEN}",
        'cache-control': "no-cache",
        'postman-token': "cba44088-3606-ffcf-ec77-358c9cd915db"
    }

    authors_set = set()
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), 'r') as f:  # open in readonly mode
            if verify_if_already_sent(filename) or filename == 'assessed.txt':
                continue

            data = json.loads(f.read())
            for author in data['authors']:
                fullname = author['fistName'].strip() + ' ' + author['familyName'].strip()
                if fullname not in authors_set:
                    response = requests.request("POST", url, data=json.dumps(author), headers=headers)

                    if response.status_code == 200 or response.status_code == 201:
                        register_sent(filename)
                        authors_set.add(fullname)

                print('response from ElasticSearch: ', response, filename)

if __name__ == "__main__":
    main()
