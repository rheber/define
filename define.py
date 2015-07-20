from argparse import Action, ArgumentParser
from contextlib import closing
from html.parser import HTMLParser
import shelve
import sys
from urllib.request import urlopen, URLError

URL = "http://dictionary.reference.com/browse/{word}?s=t"
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
            else:
                self.glosses[-1] += data.strip("\n")

def glosses(word):
    """Fetch the definitions of a word."""

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

def print_glosses(glosses):
    """Print a list of definitions in a nice format."""

    if not glosses:
        print("Not defined.", file=sys.stderr)
        return
    for (n, gloss) in enumerate(glosses):
        print("{num}. {gloss}\n".format(num=n,
                gloss=gloss.encode(errors='replace')))

def define(word, override=False):
    """Print the definitions of a word, fetching them if necessary."""

    with closing(shelve.open("glossary")) as glossary:
        if word not in glossary or override:
            glossary[word] = glosses(word)
        print_glosses(glossary[word])

class DefineAction(Action):
    def __call__(self, parser, namespace, values, option_string):
        define(values)

class OverrideAction(Action):
    def __call__(self, parser, namespace, values, option_string):
        define(values, override=True)

class KeysAction(Action):
    def __call__(self, parser, namespace, values, option_string):
        with closing(shelve.open("glossary")) as glossary:
            for key in sorted(glossary):
                print(key)

class LexemesAction(Action):
    def __call__(self, parser, namespace, values, option_string):
        with closing(shelve.open("glossary")) as glossary:
            for key in sorted(glossary):
                if(glossary[key]):
                    print(key)

class DeleteAction(Action):
    def __call__(self, parser, namespace, values, option_string):
        with closing(shelve.open("glossary")) as glossary:
            glossary.pop(values, None)

if __name__ == "__main__":
    parser = ArgumentParser(description="Look up the meanings of a word")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-d", "--define", help="try to define the given word",
                        action=DefineAction)
    group.add_argument("-c", "--clear", help="clear the given key if present",
                        action=DeleteAction)
    group.add_argument("-k", "--keys", help="list all stored keys",
                        action=KeysAction, nargs=0)
    group.add_argument("-l", "--lexemes",
                        help="list all stored keys which have definitions",
                        action=LexemesAction, nargs=0)
    group.add_argument("-o", "--override", help="override stored definitions",
                        action=OverrideAction)
    group.add_argument("-v", "--version", action="version",
                        version="define v0.1")
    args = parser.parse_args()

