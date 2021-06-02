import hashlib
import hmac
import json
import re
import html
import urllib.parse

from urllib.request import Request, urlopen

from flask_babel import gettext

from searx import settings

keywords = ('(.*)(bitcoin|btc|BTC) (.{3})(.*)', '(.*)(bitcoin|btc|BTC)(.*)')

author = {
    'name': 'Justin Back',
    'url': "https://github.com/JustinBack"
}


def answer(query):
    if re.match(keywords[0], query):

        currency = re.match(keywords[0], query).group(3)
        api = lookup_currency(currency)

        if not api:
            return False

        return {
            'answer': '<b>The current Bitcoin index is:</b><br><br><b>USD:</b> {usd}<br><b>{currency}:</b> {custom}<br><small>{disclaimer}</small>'.format(
                usd=html.escape(str((api['bpi']['USD']['rate_float'])) + ' USD'),
                custom=html.escape(str(api['bpi'][currency]['rate_float']) + ' ' + currency),
                currency=html.escape(currency),
                disclaimer=html.escape(str((api['disclaimer']))),
            ),
            'safe': True
        }

    else:
        api = lookup_top()

        if not api:
            return False


        return {
            'answer': '<b>The current Bitcoin index is:</b><br><br><b>USD:</b> {usd}<br><b>EUR:</b> {eur}<br><b>GBP:</b> {gbp}<br><small>{disclaimer}</small>'.format(
                usd=html.escape('$' + str((api['bpi']['USD']['rate_float']))),
                eur=html.escape(str(api['bpi']['EUR']['rate_float']) + '€'),
                gbp=html.escape(str(api['bpi']['USD']['rate_float']) + '£'),
                disclaimer=html.escape(str((api['disclaimer']))),
            ),
            'safe': True
        }


def lookup_top():
    httprequest = Request('https://api.coindesk.com/v1/bpi/currentprice.json',
                          headers={"Accept": "application/json"})

    with urlopen(httprequest) as response:
        if response.status != 200:
            return False

        api = json.loads(response.read().decode())

        return api


def lookup_currency(currency):
    try:
        httprequest = Request('https://api.coindesk.com/v1/bpi/currentprice/' + urllib.parse.quote(currency) + '.json',
                              headers={"Accept": "application/json"})

        with urlopen(httprequest) as response:
            if response.status != 200:
                return False

            api = json.loads(response.read().decode())

            return api
    except:
        return False