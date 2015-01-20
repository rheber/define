from html.parser import HTMLParser
from sys import stderr
from urllib.request import urlopen

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
                self.glosses.append(data)
                self.gloss_start = False
            else:
                self.glosses[-1] += data


def glosses(word):
    """Return the definitions of a word."""

    try:
        response = urlopen(URL.format(word=word))
        parser = GlossParser()
        parser.feed(response.read())
        # parser.glosses
    except URLError:
        print("Error: Couldn't access site", file=stderr)
