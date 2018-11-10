from xmlrpc.client import ServerProxy
from urllib import parse

import requests

from google_translate import translate as g_translate

BASE_URL  = "https://slovnik.seznam.cz/{source_lang}-{target_lang}/?q={query}"
QUERY_URL = "https://api.slovnik.seznam.cz/rpc2"

ALLOWED_LANGUAGE_SPEC  = ["anglicky", "anglický", "angličtina"]
ALLOWED_COMMANDS = ["přeložit", "překlad", "jak se říct", "jak přeložit"]
ALLOWED_EXACTS = ["anglicky", "v anglictine", "v angličtině", "do angličtiny"]

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

        if best_lemma:
            lemmas.append(best_lemma['lemma'])
            tag_key = best_lemma['morphology']['tagStr'][:2]
            tags.append(_AJKA_TAGSET.get(tag_key, 'N/A'))

            correction.append(text)

    return correction, lemmas, tags


def _analyze_query(graph_response: dict) -> bool:
    # TODO: use declension?
    if graph_response:

        skip_right, skip_left = 0, 0

        correction, lemmas, tags = _get_parsed_attrs(graph_response)

        # cmd check
        cmd_allowed = False
        for cmd in ALLOWED_COMMANDS:
            query_cmd_len = len(cmd.split(" "))
            query_cmd = " ".join(lemmas[:query_cmd_len])

            cmd_allowed = query_cmd  == cmd

            if cmd_allowed:
                skip_left = max(query_cmd_len, skip_left)
                break

        # exact check
        exact_allowed = False
        for exact in ALLOWED_EXACTS:
            exact_spec_len = len(exact.split(" "))
            query_exact = " ".join(correction[-exact_spec_len:])

            exact_allowed = query_exact == exact

            if exact_allowed:
                skip_right = max(exact_spec_len, skip_right)
                break

        # lang spec check
        valid_lang_spec = lemmas[-1] in ALLOWED_LANGUAGE_SPEC
        valid_lang_spec_len = len(exact.split(" "))

        if valid_lang_spec:
            skip_right = max(valid_lang_spec, skip_right)

        if exact_allowed or (cmd_allowed and valid_lang_spec):

            return lemmas[skip_left:len(lemmas) - skip_right], \
                   tags[skip_left:len(tags) - skip_right]

    return [], []


def _translate(graph_response: dict,
               source_lang='cz',
               target_lang='en',
               api='Seznam') -> dict:
    query, tags = _analyze_query(graph_response)

    resp = {'status': 400,
            'statusMessage': 'Bad Request',
            'translations': [],
            'tags': tags}

    if query:

        if api == 'Seznam':
            if source_lang == 'cs':
                source_lang = 'cz'

            # only one word per request is supported
            for q in query:
                r = client.toolbar.search(q, f"{source_lang}_{target_lang}")
                translations = [
                    pr['translatedPhrase'] for pr in r['translations']
                ]
                resp['translations'].append(translations)

            resp['status'] = 200
            resp['statusMessage'] = 'Status OK'

        elif api == 'Google':
            if source_lang == 'cz':
                source_lang = 'cs'

            translations = g_translate(query, source_lang, target_lang)
            resp['translations'] = [
                [t] for t in translations
            ]
            resp['status'] = 200
            resp['statusMessage'] = 'Status OK'


        elif api == 'TBD':  # TODO: custom model
            pass


    return resp


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
              api='Seznam') -> dict:
    g_counter += 1
    global g_counter
    response = raw_graphql_query(text['text'])
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
