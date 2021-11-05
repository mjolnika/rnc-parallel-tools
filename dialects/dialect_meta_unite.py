import xlrd, os, codecs, re


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

def read_data(fname):
    data = []
    try:
        book = xlrd.open_workbook(fname)
        for shN in range(book.nsheets):
            sh = book.sheet_by_index(shN)
            for c in range(sh.ncols):
                data.append(sh.cell_value(rowx=0, colx=c))
    except:
        print('Could not read ' + fname)
    return data


def read_all(startDir):
    fileData = {}       # filename -> {dataType -> [data]}
    for root, dirs, files in os.walk(startDir):
        for fname in files:
            if not fname.lower().endswith('.xls'):
                continue
            fname = os.path.join(root, fname)
            data = read_data(fname)
            m = re.search('^(.*?)-?(meta-general|phonetics|geography|)\\.xls$',
                          fname.lower(), flags=re.U)
            if m is None:
                print('Wrong XLS filename: ' + fname)
                continue
            xmlFilename = m.group(1)
            dataType = m.group(2)
            if len(dataType) <= 0:
                dataType = 'basic'
            try:
                fileData[xmlFilename][dataType] = data
            except KeyError:
                fileData[xmlFilename] = {dataType: data}
    return fileData


def printAll(fileData, fnameOut):
    fOut = codecs.open(fnameOut, 'w', 'utf-8-sig')
    for xmlFilename in fileData:
        if 'basic' not in fileData[xmlFilename] or\
           'meta-general' not in fileData[xmlFilename] or\
           'phonetics' not in fileData[xmlFilename]:
            print('Wrong XLS: ' + xmlFilename)
            continue
        fOut.write(transliterate(xmlFilename[2:]) + '.xml\t')
        for dataType in ('basic', 'meta-general', 'phonetics'):
            for dataCell in fileData[xmlFilename][dataType]:
                fOut.write(str(dataCell).replace('\n', ' ').replace('\r', '').replace('\t', '') + '\t')
        if 'geography' in fileData[xmlFilename]:
             for dataCell in fileData[xmlFilename]['geography']:
                fOut.write(str(dataCell).replace('\n', ' ').replace('\r', '').replace('\t', '') + '\t')
                
        fOut.write('\r\n')
    fOut.close()

if __name__ == '__main__':
    d = '.'
    dirs = [filename for filename in os.listdir(d) if os.path.isdir(os.path.join(d, filename))]
    for directory in dirs:
        print(directory)
        path = os.path.join(d, directory, 'xls')
        #read = read_all(path)
        #for key in read.keys():
         #   print(read[key])
        printAll(read_all(path), f'{directory}_meta-dialect.csv')

#    for file in os.listdir('.'):
#        if file.endswith('.csv'):
#            with open(file, encoding='utf-8') as f:
#                text = f.read()
#
#            with open(file, 'w', encoding='utf-8') as f:
#                f.write(text.replace('_xls_', '_'))
    
