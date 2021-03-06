import argparse
import os
from dotenv import load_dotenv

import requests
from urllib.parse import urlparse


def add_http(link):
    url = urlparse(link, 'https')
    return url.scheme + '://' + url.netloc + url.path


def delete_http(link):
    url = urlparse(link)
    return url.netloc + url.path


def check_user_link(link):
    fixed_link = add_http(link)
    response = requests.get(fixed_link)
    return response.raise_for_status()


def shorten_link(link, headers):
    url = 'https://api-ssl.bitly.com/v4/shorten'
    payload = {
      'long_url': link
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    decoded_response = response.json()
    if 'errors' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['errors'])
    bitlink = decoded_response['link']
    return bitlink


def count_clicks(link, headers):
    fixed_link = delete_http(link)
    params = (
      ('unit', 'month'),
    )
    url = f'https://api-ssl.bitly.com/v4/bitlinks/{fixed_link}/clicks/summary'
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    decoded_response = response.json()
    if 'errors' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['errors'])
    total_clicks = decoded_response['total_clicks']
    return total_clicks


def is_bitlink(link, headers):
    fixed_link = delete_http(link)
    url = f'https://api-ssl.bitly.com/v4/bitlinks/{fixed_link}'
    response = requests.get(url, headers=headers)
    return response.ok


def main():
    load_dotenv()
    token = os.getenv('BITLY_SECRET_TOKEN')
    headers = {
        'Authorization': token,
    }

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
        check_user_link(args.link)
        if is_bitlink(args.link, headers):
            number_of_clicks = count_clicks(args.link, headers)
            print(
              f'Your link has been followed: {number_of_clicks} time(s)'
            )
        else:
            bitlink = shorten_link(args.link, headers)
            print('Bitlink:', bitlink)
    except requests.exceptions.HTTPError:
        print('Error. Check that the link is correct.')


if __name__ == '__main__':
    main()
