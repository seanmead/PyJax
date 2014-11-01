"""
Created on Jan 30, 2014

@author: Sean Mead
"""


import re


meaning = ['a ', 'is ']

entity = {'&#8221': '"', '&#8220': '"', '&#8217;': "'", '&quot;': '"', '&#39;': "'", "&ldquo;": '"',
          "&rdquo;": '"'}


def strip_meaning(extra):
    """
    Strip extra meaning.
    :rtype : String
    """
    for item in meaning:
        extra = re.sub(item, '', extra, 1)
    return extra


def white_fix(text):
    """
    Parse and return a given text with extra spaces stripped out.
    :param text:
    :return:
    """
    prnt = ''
    text = text.split(' ')
    for item in text:
        if len(item) > 0:
            prnt += item.strip() + ' '
    return prnt.strip()


def decode(text):
    """
    Parse and decode a unicode String.
    """
    text = text.encode('ascii', 'ignore')
    for key, value in entity.items():
        text = text.replace(key, value)
    return text


def destroy(text):
    """
    Destroy extra tags and whitespace.  Will remove extra html.
    """
    tag = re.compile(r'<[^>]+>')
    return white_fix(tag.sub('', text).strip('\n<>'))


def href(text):
    """
    Find the href within a tag.
    """
    left = bounded(text, 'href=\"', '\"')
    text = text[text.index(left):].replace(left, '')
    text = bounded(text, '/', '"')[:-1]
    return text


def allbound(html, start):
    """
    Return text bounded by a significant starting String.
    """
    opens = 1
    html = html.replace('<br>', '')
    html = html.replace('<ol>', '')
    if start in html:
        html = html[html.index(start):]
        index = 0
        while opens > 0:
            index = 0
            opened = False
            for i in range(0, len(html)-1, 1):
                item = html[i:i+2]
                if item == '</':
                    opens -= 1
                    opened = False
                elif item == '/>':
                    opened = False
                    opens -= 1
                elif opened:
                    if item[0] == '>':
                        opened = False
                elif item[0] == '<':
                    opened = True
                    opens += 1
                index += 1
                if opens <= 1:
                    for c in html[index:]:
                        if c == '>':
                            return html[:index+1]
                        index += 1
            opens = 0
        return html[:index+1]


def bounded(html, left, right, offset=0):
    """
    Return a text between a left and right String.
    """
    text = html.lower()
    left = left.lower()
    right = right.lower()
    if left in text and right in text:
        html = html[text.index(left)-offset:]
        text = html.lower()
        html = html[:text.index(right) + len(right) + offset]
    return html.strip()


def multi_bound(html, left, right):
    """
    Return a list of items bounded by left and right.
    """
    bounds = []
    while left in html and right in html:
        bound = bounded(html, left, right, 1)
        html = html.replace(bound, '')
        bounds.append(bound[1:-1])
    return bounds


def unsect(html, left, right):
    """
    Remove sections containing the bounded left and right.
    """
    while left in html and right in html:
        html = html.replace(bounded(html, left, right, 1), '')
    return html


def rows(html, row, on='<tr>'):
    """
    Find rows within html.

    :param html: Full html
    :param row: String that row must contain
    :param on: Search for rows by splitting.  Default is <tr>
    """
    links = []
    html = html.split(on)
    for item in html:
        item = str(item)
        if row in item:
            links.append(item)
    return links