# StackOverflow Art Scraper

This script scrapes images and dates from blog posts on the StackOverflow Blog, up to a specified maximum page number. The images are then saved to the `images` directory, with file names in the format `{date}_{sha1_hash}.{file_extension}`. The script stops if more than 10 files already exist in the `images` directory.

## Requirements

- `beautifulsoup4`
- `dateutil`
- `requests`

## Usage

To run the script, use the following command:

```bash
python main.py

```
