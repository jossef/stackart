import os
import shutil
from hashlib import sha1
import dateutil.parser
import requests

SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, 'images')
SO_PRODUCTION_ID = "jo7n4k8s"


def get_blog_posts(max_page=75, page_size=100):
    for page in range(0, max_page):
        query = f'''*[_type == "blogPost" &&
        !("podcast" in tags[]->slug.current) &&
        !("newsletter" in tags[]->slug.current) && 
        !(_id in *[_type == "blogSettings"].sticky[]->_id) &&
        visible == true 
        ] | order(publishedAt desc) [{page + page * page_size}...{page_size + page * page_size}] {{
        _id,
        title,
        publishedAt,
        image
        }}'''

        r = requests.get(f'https://{SO_PRODUCTION_ID}.api.sanity.io/v2021-10-21/data/query/production', allow_redirects=True, params={"query": query})
        r.raise_for_status()
        data = r.json()

        items = data['result']

        for item in items:
            item_image = item.get('image', {})
            if not item_image:
                continue

            item_image_asset = item_image.get('asset', {})
            if not item_image_asset:
                continue

            image_url = item_image_asset.get('_ref')
            if not image_url:
                continue

            _, image_id, image_size, image_extension = image_url.split('-')
            image_url = f"https://cdn.stackoverflow.co/images/{SO_PRODUCTION_ID}/production/{image_id}-{image_size}.{image_extension}"
            date = item['publishedAt']
            date = dateutil.parser.parse(date)
            yield image_url, date

        if len(items) != page_size:
            break


def download_file(url, file_path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def main():
    files_exist = 0
    for image_url, date in get_blog_posts():
        date = date.strftime("%Y-%m-%d")
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
            print(image_url, date)
            download_file(image_url, output_file_path)

        if files_exist > 10:
            break


if __name__ == '__main__':
    main()
