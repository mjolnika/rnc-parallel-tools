import re

dictNgrams = {'ა':'a','ბ':'b', 'გ':'g', 'დ':'d', 'ე':'e', 'ვ':'v', 'ზ':'z', 'თ':'t', 'ი':'i',
            'კ':'k’', 'ლ':'l', 'მ':'m', 'ნ':'n', 'ო':'o', 'პ':'p’', 'ჟ':'ž', 'რ':'r', 'ს':'s',
            'ტ':'t’', 'უ':'u', 'ფ':'p', 'ქ':'k', 'ღ':'ɣ', 'ყ':'q’', 'შ':'š', 'ჩ':'č', 'ც':'с',
            'ძ':'ʒ', 'წ':'с’', 'ჭ':'č’', 'ხ':'x', 'ჯ':'ǯ', 'ჰ':'h'}

rxGeorgian2Latin = re.compile('(?:' + '|'.join(k for k in sorted(dictNgrams,
                                                                key=lambda x: -len(x))) + ')')


def georgian_translit_latin(text):
    """
    Transliterate Georgian text to Latin orphography.
    """
    return rxGeorgian2Latin.sub(lambda m: dictNgrams[m.group(0)], text)
