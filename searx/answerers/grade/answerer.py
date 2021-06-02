import hashlib
import hmac
import json
import urllib.parse

from urllib.request import Request, urlopen

from flask_babel import gettext


from searx import settings

keywords = ('grade', 'privacy')


author = {
    'name': 'The ToS;DR Team',
    'url': "https://tosdr.org"
}

def proxify(url):
    if url.startswith('//'):
        url = 'https:' + url

    if not settings.get('result_proxy'):
        return url

    url_params = dict(mortyurl=url.encode())

    if settings['result_proxy'].get('key'):
        url_params['mortyhash'] = hmac.new(settings['result_proxy']['key'],
                                           url.encode(),
                                           hashlib.sha256).hexdigest()

    return '{0}?{1}'.format(settings['result_proxy']['url'],
                            urllib.parse.urlencode(url_params))

# required answerer function
# can return a list of results (any result type) for a given query
def answer(query):
    service = ''
    parts = query.query.split()
    if len(parts) < 2:
        return []

    if len(parts) > 2:
        _parts = parts
        _parts.pop(0)
        service = ' '.join(_parts)
    else:
        service = parts[1]

    search_result = search_service(service)


    if len(search_result) > 0:
        return [{
            'answer': gettext('{service} has a {grade} on ToS;DR'.format(service=search_result['name'], grade=search_result['rating']['human'])),
            'url': search_result['links']['crisp']['service'],
            'image': {
                'src': proxify(search_result['links']['crisp']['badge']['png']),
                'width': '202',
                'height': '20',
                'align': 'right'
            }
        }]


    return [{
        'answer': gettext('No Service on ToS;DR Found with the Query "{service}"'.format(service=service)),
    }]


# required answerer function
# returns information about the answerer
def self_info():
    return {'name': gettext('ToS;DR Grade'),
            'description': gettext('Get a grade from ToS;DR'),
            'examples': ['grade Facebook']}


def search_service(query):
    httprequest = Request('https://api.tosdr.org/search/v4/?query='+ urllib.parse.quote(query), headers={"Accept": "application/json"})

    with urlopen(httprequest) as response:
        if response.status != 200:
            return []

        api = json.loads(response.read().decode())

        # Request Success
        if api['error'] & 0x100:
            if len(api["parameters"]["services"]) > 0:
                return api["parameters"]["services"][0]
            return []
        return []

# if __name__ == "__main__":
#    search_query = SearchQuery('grade Facebook lol', [EngineRef('Test', 'general')],
#                                   'en-US', 0, 1, None, None)
#    print(answer(search_query))
