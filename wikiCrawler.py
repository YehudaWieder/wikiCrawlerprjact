import random
import urllib.parse
import re

import requests
from bs4 import BeautifulSoup
import os

EN_VALID_WIKI_URL = "https://en.wikipedia.org/wiki/"
HE_VALID_WIKI_URL = "https://he.wikipedia.org/wiki/"
MIN_PHOTO_SIZE = 3000


def get_soup_object(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
    except:
        pass
    return


def get_page_title(soup_object):
    title = soup_object.find('title')
    return title.text.strip() if title else "untitle_folder"


def get_images(url, soup_object):
    valid_images = []
    images = soup_object.findAll('img', class_="mw-file-element")
    for image in images:
        width = int(image['width'])
        height = int(image['height'])
        src = image.get("src")
        src = urllib.parse.urljoin(url, src)

        if (width * height) >= MIN_PHOTO_SIZE:
            valid_images.append(src)

    return valid_images


def save_image(image_url, folder_dir):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            img_data = response.content
            img_name = image_url.rsplit('/', 1)[1]
            img_path = os.path.join(folder_dir, img_name)
            with open(img_path, "wb") as img_file:
                img_file.write(img_data)
    except:
        print(f'saving the image {img_name} is failed')


def extract_links(url, soup_object, width, visited_url):
    links = []
    for link in soup_object.find_all('a', href=True):
        link_url = link['href']
        if ':' not in link_url:
            full_url = urllib.parse.urljoin(url, link_url)
            if full_url not in visited_url and full_url.startswith(EN_VALID_WIKI_URL) or full_url.startswith(HE_VALID_WIKI_URL):
                links.append(full_url)
    return random.sample(links, min(width, len(links)))


def crawl_wiki(url, main_dir_folder, depth, width, visited_url):
    visited_url.add(url)
    soup_object = get_soup_object(url)
    page_name = get_page_title(soup_object)
    folder_dir = os.path.join(main_dir_folder, page_name)
    images = get_images(url, soup_object)
    if images:
        os.makedirs(folder_dir, exist_ok=True)
        for image_url in images:
            save_image(image_url, folder_dir)
    if depth > 0:
        links = extract_links(url, soup_object, width, visited_url)
        for link in links:
            crawl_wiki(link, main_dir_folder, depth - 1, width, visited_url)


def main():
    visited_url = set()

    # while True:
    #     try:
    #         depth_str = input(str("input a integer number for depth of pages to search: "))
    #         assert depth_str.isdigit() and int(depth_str) > 0
    #         depth = int(depth_str)
    #         break
    #     except AssertionError:
    #         print("invalid input, please enter a positive integer.")
    #         print()
    #
    # while True:
    #     try:
    #         width_str = input(str("input a integer number for width of links to search in any page: "))
    #         assert width_str.isdigit() and int(width_str) > 0
    #         width = int(width_str)
    #         break
    #     except AssertionError:
    #         print("invalid input, please enter a positive integer.")
    #         print()

    # url = input("input a wikipedia url to start the search from it: ")
    # main_dir_folder = input("input a direction in your computer for the main folder to save the photos in it: ")

    url = r"https://en.wikipedia.org/wiki/Donald_Trump"
    main_dir = r"/home/mefathim/Downloads/pic"
    depth = 2
    width = 2

    crawl_wiki(url, main_dir, depth, width, visited_url)


main()
