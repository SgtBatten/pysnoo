"""Snoo CLI Tool"""
import asyncio
import logging
import argparse
import getpass
import json

from pysnoo import SnooAuthSession

logging.basicConfig(level=logging.DEBUG)


def get_token_updater(token_file):
    """Return an token_updater function writing tokens to token_file"""
    def token_updater(token):
        with open(token_file, 'w') as outfile:
            json.dump(token, outfile)
    return token_updater


def get_token(token_file):
    """Read a token from a token_file (fails silently)"""
    try:
        with open(token_file) as infile:
            token = json.load(infile)
            return token
    except FileNotFoundError:
        pass
    except ValueError:
        pass


async def async_main(username, password, token_file):
    """Async Main"""
    token_updater = get_token_updater(token_file)
    async with SnooAuthSession(token=get_token(token_file), token_updater=token_updater) as auth:

        if not auth.authorized:
            # Init Auth
            new_token = await auth.fetch_token(username, password)
            token_updater(new_token)

        me_response = await auth.get('https://snoo-api.happiestbaby.com/us/me/')
        print('Me: {}'.format(await me_response.json()))

        # pubnub = SnooPubNub(auth.access_token, SERIAL)
        # pubnub.subscribe()


def _header():
    _bar()
    print("Snoo CLI")
    _bar()


def _bar():
    print('---------------------------------')


def get_username():
    """read username from STDIN"""
    username = input("Username: ")
    return username


parser = argparse.ArgumentParser(
    description='Snoo Smart Bassinett',
    epilog='https://github.com/rado0x54/pysnoo',
    formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('-u',
                    '--username',
                    dest='username',
                    type=str,
                    help='username for Snoo account')

parser.add_argument('-p',
                    '--password',
                    type=str,
                    dest='password',
                    help='username for Snoo account')

parser.add_argument('-t',
                    '--tokenFile',
                    metavar='file',
                    default='.snoo_token.txt',
                    dest='token_file',
                    help='Cached token file to read and write an existing OAuth Token to.')

args = parser.parse_args()
_header()

if not args.username:
    args.username = get_username()

if not args.password:
    args.password = getpass.getpass("Password: ")

# Python 3.7+
asyncio.run(async_main(args.username, args.password, args.token_file))
