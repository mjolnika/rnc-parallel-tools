import re
import os
from lxml import etree


def transliterate(s):
    s = s.replace('́', '').replace("'", "_").replace(')', '.')
    alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    translit = 'abvgdeezzijklmnoprstufxccww_y_euq'
    alphabet += alphabet.upper()
    translit += translit.upper()
    ru2translit = {alphabet[i]: translit[i] for i in range(len(alphabet))}
    newS = ''
    for c in s:
        if c in ru2translit:
            newS += ru2translit[c]
        else:
            newS += c
    return cleanfilename(newS)

def cleanfilename(s):
    s = s.replace('.xhtml', '')
    s = re.sub('[^\w\d]-[^\w\d]', '_', s)
    s = re.sub('[^\w\d](-)', '_', s)
    s = re.sub('(-)[^\w\d]', '_', s)
    s = s.replace('+', '_').replace(' ', '_').replace('(', '').replace(')','')
    s = re.sub('[^\w\d_-]', '_', s)
    s = re.sub('_+', '_', s)
    return s.strip('_')

def process_sentence(se):
    seText = se.text
    words = []
    # if seText is not None:
    #     words = seText.split()
    # else:
    #     words = [etree.tostring(w, encoding='unicode')
    #              for w in se]
    if len(se) > 0 or seText is None:
        words = [etree.tostring(w, encoding='unicode')
                 for w in se]
        if seText is not None:
            words[0] = seText + words[0]
    else:
        words = re.findall('[^<>\r\n\\w]*[\\w()\\[\\]][-\\w()\\[\\]́\'̯̂]*[^<>\r\n\\w]*', seText)
    return words


def process_file(fnameIn, fnameOut):
    print('Starting ' + fnameIn + '...')
    try:
        fIn = open(fnameIn, 'r', encoding='utf-8-sig')
        source = fIn.read()
    except UnicodeDecodeError:
        fIn = open(fnameIn, 'r', encoding='utf-16le')
        source = fIn.read()
    source = re.sub('^<\\?.*?>', '', source.replace('w_raw', 'w'))
    source = source.replace('"gr=', '" gr=')
    source = re.sub('format=([123])', 'format="\\1"', source)
    source = source.replace('<xml version="1.0" encoding="utf-8".>',
                            '<?xml version="1.0" encoding="utf-8"?><html><head>\n</head>\n<body>')
    if '</body>' not in source:
        source = source.replace('<p>', '</p>\n<p>')
        source = source.replace('<body>\n</p>', '<body>')
        source += '\n</p>\n</body>\n</html>'
    source = source.replace('ў', 'ў')
    source = source.replace('Ў', 'Ў')
    source = re.sub('ч"(?=\\w)', 'ӵ', source)
    fIn.close()
    tree = etree.XML(source)
    # except:
    #     print('XML in ' + fnameIn + ' is not valid.')
    #     return

    bInterviewer = False
    bSpeaker = False
    fOut = open(fnameOut, 'w', encoding='utf-8')
    fOut.write('<?xml version="1.0" encoding="utf-8"?>\n<html><head/><body><text>\n')
    paras = tree.findall('.//para')
    for para in paras:
        wordsPhon = []
        wordsNorm = []
        sentences = para.findall('se')
        for se in sentences:
            if se.attrib['format'] == '1':
                continue
            elif se.attrib['format'] == '2':
                wordsPhon = process_sentence(se)
            elif se.attrib['format'] == '3':
                wordsNorm = process_sentence(se)
        if len(wordsNorm) != len(wordsPhon):
            print(len(wordsNorm), len(wordsPhon))
            #print('Unequal number of words in the lines: ', '_'.join(wordsPhon))
            #print('_'.join(wordsNorm), len(wordsNorm))
            c = 0
            for x, y in zip(wordsPhon, wordsNorm):
                c += 1
                print(c)
                print(x)
                print(y)

        if all('<w>' not in w for w in wordsNorm):
            if bSpeaker:
                fOut.write('</speaker>\n')
                bSpeaker = False
            if not bInterviewer:
                fOut.write('<interviewer>\n')
                bInterviewer = True
        else:
            if bInterviewer:
                fOut.write('</interviewer>\n')
                bInterviewer = False
            if not bSpeaker:
                fOut.write('<speaker>\n')
                bSpeaker = True
        fOut.write('<se>\n')
        for i in range(len(wordsPhon)):
            m = re.search('>([^<>]*)</w>', wordsPhon[i])
            if m is not None:
                wordsPhon[i] = m.group(1)
            else:
                if wordsPhon[i].count('(') == wordsPhon[i].count(')') and not\
                       (wordsPhon[i].startswith(')') and wordsPhon[i].endswith(')')):
                    wordsPhon[i] = wordsPhon[i].strip(' .,<>!?\'":;[]*_-«»/')
                else:
                    wordsPhon[i] = wordsPhon[i].strip(' .,<>!?\'":;()[]*_-«»/')
        for i in range(len(wordsNorm)):
            wordNorm = ''
            if '<w>' not in wordsNorm[i]:
                m = re.search('^([^\\w]*?)(\\w|\\w[\\w-]*\\w)\\b(.*)$',
                               wordsNorm[i])
                if m is None:
                    print('Not a word: ' + wordsNorm[i])
                    wordNorm = wordsNorm[i].strip(' .,<>!?\'":;()[]*_-«»/')
                else:
                    wordsNorm[i] = m.group(1) + '<w>' + m.group(2) +\
                                   '</w>' + m.group(3)
                    wordNorm = m.group(2)
            else:
                wordNorm = re.sub('^.*>([^<>]*?)</w>.*$', '\\1', wordsNorm[i])
            wordsNorm[i] = wordsNorm[i].replace('<w>', '<w norm="' + wordNorm + '">')
            wordsNorm[i] = re.sub('[^<>]*</w>', wordsPhon[i].replace('\\', '/') +
                                  '</w>', wordsNorm[i])

        fOut.write('\n'.join(wordsNorm).replace("'", "ʼ") + '\n')
        fOut.write('</se>\n')
    if bInterviewer:
        fOut.write('</interviewer>\n')
    elif bSpeaker:
        fOut.write('</speaker>\n')
    fOut.write('</text></body></html>\n')
    fOut.close()

    #fIn = open(fnameOut, 'r', encoding='utf-8-sig')
    #text = fIn.read()
    t = etree.parse(fnameOut)
    #fIn.close()


def process_dir(dirname):
    for root, dirs, files in os.walk(dirname):
        for fname in files:
            if not fname.endswith('.xhtml'):
                continue
            newRoot = root.replace(dirname, f'./{dirname[2:]}/dialect_xml_corpus')
            if not os.path.exists(newRoot):
                os.makedirs(newRoot)
            fnameOut = os.path.join(newRoot, transliterate(fname) + '.xml')
            fname = os.path.join(root, fname)
            process_file(fname, fnameOut)

if __name__ == '__main__':
    #dirname = input()
    d = '.'
    dirs = [filename for filename in os.listdir(d) if os.path.isdir(os.path.join(d, filename))]
    for directory in dirs[5:]:
        print(directory)
        path = os.path.join(d, directory, 'xhtml')
    #process_dir(f'./{dirname}')
        process_dir(path)
