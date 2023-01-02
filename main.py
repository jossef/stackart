import os
import re
import shutil
from hashlib import sha1

import dateutil.parser
import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, 'images')


def get_blog_posts(max_page=75):
    for page in range(1, max_page):
        r = requests.get(f'https://stackoverflow.blog/page/{page}/', allow_redirects=True)
        r.raise_for_status()

        soup = BeautifulSoup(r.content, "lxml")
        article_elements = soup.find_all("article")
        for article_element in article_elements:
            image_element = article_element.find('img')
            if not image_element:
                continue

            date_elements = article_element.find('header').find('span')
            if not date_elements:
                continue

            image_url = image_element['src']
            date = date_elements.text.strip()
            date = dateutil.parser.parse(date)
            yield image_url, date


def normalize_url(url):
    url = re.sub(r"(.*)(-\d+x\d+)(.(jpe?g|png))$", r"\1\3", url)
    return url


def download_file(url, file_path):
    with requests.get(url, stream=True) as r:
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def main():
    files_exist = 0
    for image_url, date in get_blog_posts():
        date = date.strftime("%Y-%m-%d")
        image_url = normalize_url(image_url)
        file_name = image_url.split('/')[-1]
        file_extension = file_name.split('.')[-1]
        file_name_sha1 = sha1(file_name.encode()).hexdigest()
        if len(file_extension) > 4:
            continue

        output_file_name = f'{date}_{file_name_sha1}.{file_extension}'
        output_file_path = os.path.join(IMAGES_DIR, output_file_name)

        if os.path.isfile(output_file_path):
            files_exist += 1
        else:
            download_file(image_url, output_file_path)
            print(output_file_path)

        if files_exist > 10:
            break


if __name__ == '__main__':
    main()
