from xmlrpc.client import ServerProxy
from urllib import parse

import requests

from google_translate import translate as g_translate

BASE_URL  = "https://slovnik.seznam.cz/{source_lang}-{target_lang}/?q={query}"
QUERY_URL = "https://api.slovnik.seznam.cz/rpc2"

ALLOWED_COMMANDS = ["přeložit", "překlad", "jak se říct"]
ALLOWED_LANGUAGE_SPEC  = ["anglicky", "anglický", "angličtina"]
ALLOWED_EXACTS = ["anglicky", "v anglictine", "v angličtině"]

_AJKA_TAGSET = {
  'k1': 'Substantivum',
  'k2': 'Adjektivum',
  'k3': 'Zajmeno',
  'k4': 'Cislovka',
  'k5': 'Sloveso',
  'k6': 'Prislovce',
  'k7': 'Predlozka',
  'k8': 'Spojka',
  'k9': 'Castice',
  'k0': 'Citoslovce',
  'kA': 'Zkratka',
  'kY': 'by,aby,kdyby',
}
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
g_counter = 0

def _get_parsed_attrs(graph_response: dict) -> list:
    meaning, = graph_response['data']['cqp']['meanings']
    meaning

    tokens =  meaning['queries'][0]['tokens']

    lemmas = []
    correction = []
    tags = []

    for token_attr in tokens:
        text = token_attr['text']
        best_lemma = token_attr.get('bestLemma', None)
        best_lemma = token_attr.get('bestLemma', None)

        if best_lemma:
            lemmas.append(best_lemma['lemma'])
            tag_key = best_lemma['morphology']['tagStr'][:2]
            tags.append(_AJKA_TAGSET.get(tag_key, 'N/A'))

            correction.append(text)

    #return correction, lemmas, tags
    return correction, lemmas


def _should_analyze(graph_response: dict) -> bool:
    # TODO: use declension?
    if graph_response:

        correction, lemmas = _get_parsed_attrs(graph_response)

        # matches checks
        cmd_allowed = False
        for cmd in ALLOWED_COMMANDS:
            query_cmd = " ".join(lemmas[:len(cmd.split(" "))])
            cmd_allowed = query_cmd  == cmd

            if cmd_allowed:
                break

        valid_lang_spec = lemmas[-1] in ALLOWED_LANGUAGE_SPEC

        exact_allowed = False
        for exact in ALLOWED_EXACTS:
            query_exact = " ".join(correction[-len(exact.split(" ")):])

            exact_allowed = query_exact == exact

            if exact_allowed:
                break


        if exact_allowed or (cmd_allowed and valid_lang_spec):
            return True

    return False


def _translate(graph_response: dict,
               source_lang='cz',
               target_lang='en',
               api='s') -> dict:
    # graph_response['data']['meanings'][0]['queries'][0]['tokens'][0]['text']

    if _should_analyze(graph_response):
        #query = ...
        pass

        if api == 'Seznam':
            translation = client.toolbar.search(query, f"{source_lang}_{target_lang}")
        elif api == 'Google':
            translation = g_translate(query, source_lang, target_lang)
        elif api == 'TBD':
            translation = {'success': 'You will see something here I guess...'}, 400
        else:
            translation = {'error': 'API Not Found'}, 400

    else:
        translation = {'error': 'Bad Request'}, 400

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
    global g_counter
    g_counter += 1
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

def get_access_count():
  global g_counter
  return g_counter
