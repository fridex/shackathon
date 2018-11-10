from xmlrpc.client import ServerProxy
from urllib import parse

import requests

from google_translate import translate


BASE_URL  = "https://slovnik.seznam.cz/{source_lang}-{target_lang}/?q={query}"
QUERY_URL = "https://api.slovnik.seznam.cz/rpc2"

_QUERY = \
"""
{
  cqp(query: "%s") {
    meanings {
      queries {
        text
        tokens {
          text
          bestLemma {
            lemma
            morphology {
              tagStr
            }
          }
          languages {
            language
            probability
          }
        }
      }
    }
  }
}
"""


client = ServerProxy(QUERY_URL)


def _should_analyze(graph_response) -> bool:

    return True


def _translate(graph_response: dict,
               source_lang='cz',
               target_lang='en',
               api='s') -> dict:
    # graph_response['data']['meanings'][0]['queries'][0]['tokens'][0]['text']

    if _should_analyze(graph_response):
        query = ...

        if api == 's':
            translation = client.toolbar.search(query, f"{source_lang}_{target_lang}")
        elif api == 'g':
            translation = translate(query, source_lang, target_lang)
        else:
            translation = {'status': 404, 'statusMessage': 'API Not Found', 'translations': []}

    else:
        translation = {'status': 400, 'statusMessage': 'Bad Request', 'translations': []}

    return translation


def _construct_link(query: str, source_lang='cz', target_lang='en') -> str:
    link = BASE_URL.format(
        source_lang=source_lang,
        target_lang=target_lang,
        query=parse.quote(query)
    )

    return link


def translate(text: str,
              source_lang='cz',
              target_lang='en',
              api='s') -> dict:
    response = raw_graphql_query(text)

    return _translate(response)


def raw_graphql_query(text: str) -> dict:
    query = _QUERY % text
    response = requests.post(
      'https://cqc.seznam.net/hackathon/graphql',
      headers={
        "Authorization": "Basic aGFja2F0aG9uOkFoSjR4aWU2bGllME9wYXU=",
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      json={"query": query}
    )

    return response.json()
