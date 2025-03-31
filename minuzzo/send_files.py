import os
import requests

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('ELK_TOKEN')


def register_sent(entry):
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

    index = 'articles_4'
    url = 'http://localhost:9200/{}/_doc'.format(index)
    headers = {
        'content-type': "application/json",
        'authorization': f"Basic {TOKEN}",  # hide token
        'cache-control': "no-cache",
        'postman-token': "cba44088-3606-ffcf-ec77-358c9cd915db"
    }

    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), 'r') as f:
            if verify_if_already_sent(filename):
                continue

            response = requests.request("POST", url, data=f.read(), headers=headers)

            if response.status_code == 200 or response.status_code == 201:  # response OK
                register_sent(filename)

            print('response from ElasticSearch: ', response, filename)


if __name__ == "__main__":
    main()
