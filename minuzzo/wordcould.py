import csv
import json
import urllib.parse
import re

import numpy as np
import pandas as pd
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import matplotlib.pyplot as plt


def main():
    df = pd.read_csv("Articles_with_at_least_one_women.csv", index_col=0)
    tags = df.manualTags

    tags_set = {}
    for tag_collection in tags:
        tags_list = tag_collection.split('; ')

        for index, tag_unique in enumerate(tags_list):
            if ',' in tag_unique:
                tags_list.extend(tag_unique.split(', '))
                del tags_list[index]

        normalized_tags = [item.lower() for item in tags_list]
        for tag in normalized_tags:
            if tag in tags_set:
                tags_set[tag] += 1
            else:
                tags_set[tag] = 1

    sorted_keywords = {k: v for k, v in sorted(tags_set.items(), key=lambda item: item[1])}

    with open('commom_keywords.json', 'w+') as f:
        f.write(json.dumps(sorted_keywords))

    # Capitalize all the keywords for better visualization
    capitalized_keywords = {}
    for k, v in tags_set.items():
        capitalized_keywords[k.title()] = v

    # Create and generate a word cloud image:
    wordcloud = WordCloud(background_color="white",
                          prefer_horizontal=0.95,
                          max_words=200,
                          scale=5
                          ).generate_from_frequencies(capitalized_keywords)

    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    main()
