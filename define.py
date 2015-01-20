from html.parser import HTMLParser
from sys import stderr
from urllib.request import urlopen

URL = "http://dictionary.reference.com/browse/{word}?s=t"
DEFINITION_CLASS = "def-content"



class GlossParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if ("class", DEFINITION_CLASS) in attrs:
            print(self.get_starttag_text())


def glosses(word):
    """Return the definitions of a word."""

    try:
        response = urlopen(URL.format(word=word))
        parser = GlossParser()
        parser.feed(response.read())
        # parser.glosses
    except URLError:
        print("Error: Couldn't access site", file=stderr)
