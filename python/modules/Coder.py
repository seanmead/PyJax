"""
Created on Jan 30, 2014

@author: Sean Mead
"""


entity = {'&#8221': '"', '&#8220': '"', '&#8217;': "'", '&quot;': '"', '&#39;': "'", "&ldquo;": '"',
          "&rdquo;": '"'}


def decode(text):
    """
    Parse and decode a unicode String.
    """
    text = text.encode('ascii', 'ignore')
    for key, value in entity.items():
        text = text.replace(key, value)
    return text