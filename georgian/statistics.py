from collections import defaultdict, Counter
import re

def transliteration(lex):
    newlex = ''
    nopunct = ''
    for i in list(lex):
        try:
            newlex += alpdict[i]
            nopunct += alpdict[i]
        except:
            newlex += i
    return newlex, nopunct

def get_dict():
    alp ='''aა
    bბ
    gგ
    dდ
    eე
    vვ
    zზ
    **Eჱ
    Tთ
    iი
    kკ
    lლ
    mმ
    nნ
    **yჲ
    oო
    pპ
    Zჟ
    rრ
    sს
    tტ
    uუ
    **wჳ
    Pფ
    Kქ
    Gღ
    qყ
    Sშ
    Xჩ
    Cც
    jძ
    cწ
    xჭ
    Hხ
    **Qჴ
    Jჯ
    hჰ
    **Oჵ'''
    
    alpdict = {}
    for string in alp.splitlines():
        trans, georg = list(string.strip('*'))
        alpdict[georg] = trans
    return alp_dict


if __name__ == '__main__':
    
    alp_dict = get_dict()
    with open('texts_2020/texts_2020_processed/gnv-1.para-analyzed.xml', encoding='utf-8') as f:
        text = f.read()
        
    anas = text.split('<ana')
    
    unparsed = defaultdict(int)
    for ana in anas:
        if re.search('transl=\"\"', ana):
            lemma = re.search('lex="([^"]+)?" ', ana).group(1)
            wordform = re.search('/>(.+)?</w>', ana)
            unparsed[lemma] += 1
            
    unique = []
    for ana in anas:
        try:
            t = re.search('lex="([^"]+)?"', ana).group(1)
            if t not in unique:
                unique.append(t)
        except:
            pass
        
    print('Количество нераспарсенных словоформ', sum(unparsed.values())/len(anas))
    print('Количество нераспарсенных лексем', len(unparsed)/len(unique))
    
    with open('georgian_freq_list_1.tsv', 'w', encoding='utf-8') as f:
        for w in Counter(unparsed).most_common():
            f.write(f"{w[0]}\t{w[1]}\t{transliteration(w[0])[0]}\t{transliteration(w[0])[1]}\n")
