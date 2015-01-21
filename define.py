from contextlib import closing
from html.parser import HTMLParser
import shelve
from sys import stderr
from urllib.request import urlopen, URLError

URL = "http://dictionary.reference.com/browse/{word}?s=t"
DEFINITION_CLASS = "def-content"

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
    """Return the definitions of a word."""

    try:
        response = urlopen(URL.format(word=word))
        page = response.read().decode('utf-8')
        parser = GlossParser()
        parser.feed(page)
        return parser.glosses
    except URLError:
        print("Error: Couldn't access site", file=stderr)
    except UnicodeEncodeError:
        print("Error: Can't look that up", file=stderr)

def print_glosses(glosses):
    """Print a list of definitions in a nice format."""

    if not glosses:
        print("Not defined.")
        return
    for (n, gloss) in enumerate(glosses):
        print("{num}. {gloss}\n".format(num=n, gloss=gloss))

def define(word, override=False):
    """Print the definitions of a word, fetching them if necessary."""
    
    with closing(shelve.open("glossary")) as glossary:
        if word not in glossary or override:
            glossary[word] = glosses(word)
        print_glosses(glossary[word])
