import requests

from urllib import parse
from xmlrpc.client import ServerProxy


BASE_URL  = "https://slovnik.seznam.cz/{from_lang}-{to_lang}/?q={query}"
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


def _should_anlayze(graph_response) -> bool:



def _translate(graph_response: dict) -> dict:
    # graph_response['data']['meanings'][0]['queries'][0]['tokens'][0]['text']

    if _should_analyze(graph_response):
        translation = client.toolbar.search(query, f"{from_lang}_{to_lang}")

    else:
        translation = {'status': 400, 'statusMessage': 'Bad Request', 'translations': []}

    return translation


def _construct_link(query: str, from_lang='cz', to_lang='en') -> str:
    link = BASE_URL.format(
        from_lang=from_lang,
        to_lang=to_lang,
        query=parse.quote(query)
    )

    return link


def translate(text: str) -> dict:
    response = raw_graphql_query(text)

    return _analyze(response)


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
