import sys
from urllib.request import urlopen

URL = "http://dictionary.reference.com/browse/{word}?s=t"
DEFINITION_CLASS = "def-content"

def glosses(word):
    """Return the definitions of a word."""

    try:
        response = urlopen(URL.format(word=word))
    except URLError:
        print("Error: Couldn't access site", file=sys.stderr)
    
