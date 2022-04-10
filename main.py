import argparse
import os
from dotenv import load_dotenv

import requests
from urllib.parse import urlparse

load_dotenv()

TOKEN = os.getenv('BITLY_SECRET_TOKEN')
HEADERS = {
    'Authorization': TOKEN,
    'Content-Type': 'application/json'
}


def delete_http(link):
    url = urlparse(link)
    return url.netloc + url.path


def shorten_link(link):
    url = 'https://api-ssl.bitly.com/v4/shorten'
    payload = {
      'long_url': link
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    decoded_response = response.json()
    if 'errors' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['errors'])
    bitlink = decoded_response['link']
    return bitlink


def count_clicks(link):
    fixed_link = delete_http(link)
    params = (
      ('unit', 'month'),
    )
    url = f'https://api-ssl.bitly.com/v4/bitlinks/{fixed_link}/clicks/summary'
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    decoded_response = response.json()
    if 'errors' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['errors'])
    total_clicks = decoded_response['total_clicks']
    return total_clicks


def is_bitlink(link):
    fixed_link = delete_http(link)
    url = f'https://api-ssl.bitly.com/v4/bitlinks/{fixed_link}'
    response = requests.get(url, headers=HEADERS)
    return response.ok


def main():
    parser = argparse.ArgumentParser(
        description='''The script shortens the user's link and returns a bitlink. 
        Counts the number of clicks on bitlinks.'''
    )
    parser.add_argument(
        'link',
        help='''The user's link. Link formats that the script works with:
        bitlink - https://bit.ly/xxxxxxx ; regular link - https://example.com'''
    )
    args = parser.parse_args()

    try:
        if is_bitlink(args.link):
            number_of_clicks = count_clicks(args.link)
            print(
              f'Your link has been followed: {number_of_clicks} time(s)'
            )
        else:
            bitlink = shorten_link(args.link)
            print('Bitlink:', bitlink)
    except requests.exceptions.HTTPError:
        print('Error. Check that the link is correct.')


if __name__ == '__main__':
    main()
