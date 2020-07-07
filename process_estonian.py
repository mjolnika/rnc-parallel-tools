import os
import re
import json
from lxml import etree
from xml.sax.saxutils import escape, unescape

reWords = re.compile('((?:<[^<>\r\n]+>)*)(?:^|\\b)([^<>]+?)(?:\\b|$)((?:</[^<>\r\n]+>)*)', flags= re.DOTALL)
reWordsSimple = re.compile('(?:^|\\b)[^<>]+?(?:\\b|$)', flags= re.DOTALL)


def xml2json(fnameIn, fnameOut):
    xmlTree = etree.parse(fnameIn)
    jsonText = {'paragraphs': [{'sentences': []}]}
    sentences = xmlTree.xpath('/html/body/para/se[@lang="et"] | /html/body/para/se[@lang="ee"]')
    for sentence in sentences:
        jsonText['paragraphs'][0]['sentences'].append({'words': []})
        text = sentence.xpath('string()')
        words = reWordsSimple.findall(text)
        for word in words:
            word = word.strip()
            if len(word) <= 0:
                continue
            jsonText['paragraphs'][0]['sentences'][-1]['words'].append({'text': word})
    fOut = open(fnameOut, 'w', encoding='utf-8')
    fOut.write(json.dumps(jsonText, ensure_ascii=False, indent=4))
    fOut.close()


def json2xml(fnameInXml, fnameInJson, fnameOut):
    fXml = open(fnameInXml, 'r', encoding='utf-8-sig')
    fJson = open(fnameInJson, 'r', encoding='utf-8')
    jsonSentences = json.loads(fJson.read())['paragraphs'][0]['sentences']
    fJson.close()
    fOut = open(fnameOut, 'w', encoding='utf-8')
    paraId = -1
    iSe = -1
    iWord = 0
    lang = 'ru'
    for line in fXml:
        if 'lang="ru' in line:
            lang = 'ru'
        if 'lang="e' in line:
            lang = 'ee'
        m = re.search('([ \t]*<se +lang="e[^<>]*>|^)([^\r\n]*?)'
                      '(</se>[ \t]*\r?\n|\r?\n)', line)
        if m is None or lang == 'ru' or '<para' in m.group(2) or '</para' in m.group(2):
            mPara = re.search('^([ \t]*<para id=")([^"]+)(.*)', line)
            if mPara is not None:
                paraId += 1
                fOut.write(mPara.group(1) + str(paraId) + mPara.group(3))
            else:
                fOut.write(line)
            continue
        lineOut = m.group(1)
        if '<se' in line:
            iSe += 1
            if re.search('\\w', m.group(2)) is not None:
                while iSe < len(jsonSentences) and\
                      len(jsonSentences[iSe]['words']) <= 0:
                    iSe += 1
            iWord = 0
        words = reWords.findall(m.group(2).replace('&quot;', '"').replace('&apos', "'"))
        for word in words:
            wordStripped = word[1].strip()
            if len(wordStripped) <= 0 or iWord >= len(jsonSentences[iSe]['words']) or\
               (iWord == 0 and jsonSentences[iSe]['words'][iWord]['text'] != wordStripped):
                lineOut += word[0] + word[1] + word[2]
                continue
            # print(word, jsonSentences[iSe][u'words'][iWord])
            anas = jsonSentences[iSe]['words'][iWord]['analysis']
            iWord += 1
            if len(anas) <= 0:
                if re.search('\\w', word[1], flags=re.U) is not None:
                    lineOut += word[0] + '<w>' + escape(word[1]) + '</w>' + word[2]
                else:
                    lineOut += word[0] + escape(word[1]) + word[2]
                continue
            lineOut += word[0] + '<w>'
            for ana in anas:
                lineOut += '<ana lex="' + ana['root'] + '" gr="' +\
                           ana['partofspeech'] + ',' + ana['form'].replace(' ', ',') +\
                           '" />'
            lineOut += escape(word[1]).strip() + '</w>' + word[2]
        lineOut = lineOut.replace('," />', '" />')
        lineOut += m.group(3)
        fOut.write(lineOut)
    fOut.close()


if __name__ == u'__main__':
    #xml2json(u'texts/keisrihull.xml', u'texts/keisrihull.json')
    json2xml(u'texts/keisrihull.xml', u'texts/keisrihull-analyzed.json', u'texts/keisrihull-analyzed.xml')
    #json2xml(u'texts/kompromiss.xml', u'texts/kompromiss-analyzed.json', u'texts/kompromiss-analyzed.xml')
    for fname in os.listdir('texts'):
        if not fname.endswith('.xml') or fname.endswith('analyzed.xml'):
            continue
        fname = 'texts/' + fname
        print(fname)
        json2xml(fname, fname[:-4] + '-analyzed.json', fname[:-4] + '-analyzed.xml')
