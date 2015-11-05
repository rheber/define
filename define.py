from argparse import Action, ArgumentParser
from contextlib import closing
from html.parser import HTMLParser
import shelve
import sys
from urllib.request import urlopen, URLError

URL = "http://dictionary.reference.com/browse/{word}"
AUDIO_CLASS = "audio-wrapper" # When you know you've gone too far.
DEFINITION_CLASS = "def-content"

def fatal_error(msg):
    """"Print error message and exit."""

    print(msg, file=sys.stderr)
    exit(1)

class GlossParser(HTMLParser):
    def __init__(self):
        self.strict = False
        self.reset()
        self.depth = 0
        self.gloss_start = False
        self.glosses = []

    def handle_starttag(self, tag, attrs):
        if ("class", DEFINITION_CLASS) in attrs:
            self.depth += 1
            self.gloss_start = True
        elif ("class", AUDIO_CLASS) in attrs:
            self.depth = 0
        elif self.depth:
            self.depth += 1

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            if self.gloss_start:
                self.glosses.append(data.strip("\n"))
                self.gloss_start = False
            elif self.glosses:
                self.glosses[-1] += data.strip("\n")

def glosses(word):
    """Fetch the definitions of a word. Returns a list."""

    try:
        print("Fetching definitions...", file=sys.stderr)
        response = urlopen(URL.format(word=word))
        page = response.read().decode('utf-8')
        parser = GlossParser()
        parser.feed(page)
        return parser.glosses
    except URLError:
        fatal_error("Error: Couldn't access site")
    except UnicodeEncodeError:
        fatal_error("Error: Can't look that up")

def print_glosses(tup):
  """Print a formatted list of definitions."""

  if tup == "Not defined.":
    print("Not defined.")
    return
  for (n, gloss) in enumerate(tup): # tup is a gloss list
    print("{num}. {gloss}\n".format(num=n,
        gloss=gloss.encode(errors='replace')))

def define(word, override=False):
    """Print the definitions of a word, fetching them if necessary."""

    with closing(shelve.open("glossary")) as glossary:
        if word not in glossary or override:
            g = glosses(word)
            glossary[word] = g if g else "Not defined."
        print_glosses(glossary[word])

class DefineAction(Action):
    def __call__(self, parser, namespace, values, option_string):
        define(values)

class OverrideAction(Action):
    def __call__(self, parser, namespace, values, option_string):
        define(values, override=True)

class NonlexemesAction(Action):
    def __call__(self, parser, namespace, values, option_string):
        with closing(shelve.open("glossary")) as glossary:
            for key in sorted(glossary):
                if(glossary[key] == "Not defined."):
                    print(key)

class LexemesAction(Action):
    def __call__(self, parser, namespace, values, option_string):
        with closing(shelve.open("glossary")) as glossary:
            for key in sorted(glossary):
                if(glossary[key] != "Not defined."):
                    print(key)

class DeleteAction(Action):
    def __call__(self, parser, namespace, values, option_string):
        with closing(shelve.open("glossary")) as glossary:
            glossary.pop(values, None)

class DeleteAllAction(Action):
    def __call__(self, parser, namespace, values, option_string):
        with closing(shelve.open("glossary")) as glossary:
            glossary.clear()

if __name__ == "__main__":
    parser = ArgumentParser(description="Look up the meanings of a word",
                            add_help=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--clear", help="clear the given key if present",
            metavar="KEY", action=DeleteAction)
    group.add_argument("--clearall", help="clear all stored keys",
            action=DeleteAllAction, nargs=0)
    group.add_argument("-d", "--define", help="try to define the given key",
            metavar="KEY", action=DefineAction)
    group.add_argument("-h", "--help", action='help')
    group.add_argument("-l", "--lexemes",
            help="list all stored keys which have definitions",
            action=LexemesAction, nargs=0)
    group.add_argument("-n", "--nonlexemes",
            help="list all stored keys which are not defined",
            action=NonlexemesAction, nargs=0)
    group.add_argument("-o", "--override",
            help="try to define the given key, overriding any stored definitions",
            metavar="KEY", action=OverrideAction)
    group.add_argument("-v", "--version",
            action="version", version="define v0.1")
    args = parser.parse_args()

