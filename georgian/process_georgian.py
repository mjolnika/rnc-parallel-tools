import json
from lxml import etree
import os
import re
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from georgian_translit_latin import georgian_translit_latin

with open('parsed12.json', encoding='utf-8') as f:
    dictionary = json.load(f)
with open('parsed12_nopunct.json', encoding='utf-8') as f:
    dictionary_nopunct = json.load(f)


def xml2sents(fnameIn):
    xmlTree = etree.parse(fnameIn)
    sentences = xmlTree.xpath('/html/body/para/se[@lang="ka"] | /html/body/p/para/se[@lang="ka"]')
    return [sent.xpath('string()') for sent in sentences]


def parsesents(session, sentences):
    parsed = []
    for num, sentence in enumerate(sentences):
        if not sentence:
            analysis = ''
        else:
            sentence = preprocess_punctuation_before_wordform(sentence)
            url = 'https://clarino.uib.no/gnc/parse-api'
            data = {"command": "parse",
                    "session-id": session_id,
                    "text": sentence}
            parsed_s = session.post(url, data)
            analysis = build_ana(parsed_s.json())
        parsed.append(analysis.replace('❉', ''))
    return parsed


def preprocess_punctuation_before_wordform(sentence):
    """Если встречаются словоформы, в начале которых находятся знаки препинания,
    программа не отделяет знаки препинания (кроме скобок). Поэтому при подаче на разметку их отделяет
    эта функция. Оформление прямой речи -- отделяется пробелом, скобки не отделяются,
    любые другие символы (eg кавычки) отделяются вот такой комбинацией (❉ ), которая будет удалена после обработки.
    Это такой маркер, что какой-то символ нужно приклеить к словоформе, которая идет после него (eg “ჩვენი)"""

    tokens = sentence.split(' ')
    changes = 0
    for token_id, token in enumerate(tokens):
        if token:
            if not token.isalpha() and not token[0].isalpha() and any(char.isalpha() for char in token):
                changes = 1
                match = re.search(r'(\W+)(\D.+)', token)
                punct = match.group(1)
                phrase = match.group(2)
                if punct != '(':
                    if punct == '--':
                        tokens[token_id] = ' '.join([punct, phrase])
                    else:
                        tokens[token_id] = ' '.join([punct + '❉ ', phrase])
    if changes == 0:
        return sentence
    else:
        return ' '.join(tokens)

def find_in_dictionary(lexeme):

    if lexeme in dictionary.keys():
        return dictionary[lexeme]['lex_feat'], dictionary[lexeme]['transl']
    else:
        no_punct = ''
        for l in lexeme:
            if l.isalpha():
                no_punct += l
        if no_punct in dictionary_nopunct.keys():
            return dictionary_nopunct[no_punct]['lex_feat'], dictionary_nopunct[no_punct]['transl']
        else:
            return '', ''


def build_ana(parsed_json):
    sentence = ''
    tokens = parsed_json['tokens']
    for word in tokens:
        token = word['word']
        if not word['msa'][0]['features'].startswith('Punct') and not word['msa'][0]['features'].startswith(
                'Foreign') and not word['msa'][0]['features'].startswith('Interj'):
            xmlcode = '<w>'
            variants = word['msa']
            for variant in variants:
                lemma = variant['lemma'].replace('·', '').split('/')[0]
                gr = variant['features'].replace(' >', ',').replace(' ', ',').replace('<', '{').replace('>', '}')
                # comment lines below if translation is not needed
                lex_f, transl = find_in_dictionary(lemma)
                lex_f = ', '.join(lex_f.strip(' ').split(' '))
                transl = transl.replace(' ', ' ').replace(' #def ', ' ')
                analysis = f'<ana lex="{lemma}" gr="{gr}" transliteration="{georgian_translit_latin(token)}" lex_feat="{lex_f}" transl="{transl}"/>'
                # uncomment line below
                #analysis = f"<ana lex="{lemma}" gr="{gr}" transliteration="{georgian_translit_latin(token)}"/>"
                xmlcode = xmlcode + analysis
            xmlcode = xmlcode + token + '</w> '
            sentence = sentence + xmlcode
        else:
            sentence = sentence.strip(' ') + token

    return sentence.strip(' ')  # in case a sentence didn't end with a punctuation mark


def parsed2xml(fnameInXml, sentences, fnameOut):
    """
    Read the aligned Georgian/Russian XML.
    Generate an XML where the Georgian part is analyzed.
    """
    # print(fnameInXml)

    sentences = [s.strip() for s in sentences]
    if len(sentences[-1]) <= 0:
        sentences = sentences[:-1]
    # print(sentences)

    fOut = open(fnameOut, 'w', encoding='utf-8')
    paraId = -1
    iSe = 0
    lang = 'ru'
    fXml = open(fnameInXml, 'r', encoding='utf-8-sig')
    xmlText = fXml.read()
    xmlText = re.sub('(\n+)(?=</se>)',
                     lambda m: len(m.group(1)) * 2 * ' ',
                     xmlText, flags=re.DOTALL).split('\n')
    fXml.close()
    for line in xmlText:
        line += '\n'
        if re.search('^ *</?(body|head|html)> *\n|^[ \n]*$', line) is not None:
            fOut.write(line)
            continue
        if line.strip().startswith('<weight'):
            continue
        if 'lang="' in line:
            m = re.search('lang="([^\r\n"]*)"', line)
            lang = m.group(1)
        m = re.search('^([ \t]*<se +lang="ka[^<>]*>|^)([^\r\n]*?)'
                      '(</se>[ \t]*\n|\n)', line)
        if m is None or lang != 'ka' or '<para' in m.group(2) or '</para' in m.group(2):
            mPara = re.search('^([ \t]*<para id=")([^"]+)(.*)', line, flags=re.DOTALL)
            if mPara is not None:
                paraId += 1
                fOut.write(mPara.group(1) + str(paraId) + mPara.group(3))
            else:
                fOut.write(line)
            continue
        # lineSrc = m.group(2)
        if iSe >= len(sentences):
            print('Error: sentence mismatch. Paragraph ID: ' + str(paraId))
        else:
            lineOut = m.group(1) + sentences[iSe] + m.group(3)
            fOut.write(lineOut)
        iSe += 1
        # print(paraId, lineSrc)
        # print(lineOut)
    fOut.close()


if __name__ == '__main__':
    texts_folder = './texts_2020'
    processed_texts_folder = f'{texts_folder}/{texts_folder[2:]}_processed'
    for root, dirs, files in os.walk(texts_folder):
        for fname in files:
            if not fname.endswith('.xml') or fname.endswith('analyzed.xml'):
                continue
            fnameFull = os.path.join(root, fname)
            print(fnameFull)
            sentences = xml2sents(fnameFull)
            session = requests.Session()
            # по какой-то причине иногда апи не выдает номер сессии, поэтому достать его можно
            # кликнув на кнопку "parse" https://clarino.uib.no/gnc/parse?, номер сессии появится в строке
            session_id = session.get('https://clarino.uib.no/gnc/parse-api?command=get-session',
                                     verify=False).json().get('session-id')
            #session_id = 251706363915057
            setparams = session.get(
                f'https://clarino.uib.no/gnc/parse-api?command=parameter&session-id={session_id}&attribute=disambiguate&value=false',
                verify=False)
            parsed = parsesents(session, sentences)
            if not os.path.isdir(processed_texts_folder):
                os.mkdir(processed_texts_folder)
            parsed2xml(fnameFull, parsed, os.path.join(processed_texts_folder, fname[:-4] + '-analyzed.xml'))
            print(f'{fnameFull} processed')
