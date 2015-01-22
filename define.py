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
    """Return the definitions of a word."""

    try:
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
        print("Not defined.")
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        fatal_error("Error: Missing argument")
    else:
        define(sys.argv[-1])
