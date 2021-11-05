import os
path = r'texts\texts_2020'
for root, dirs, files in os.walk(path):
    for file in files:
        p1 = os.path.join(path, file)
        p2 = os.path.join(path, file.replace(' ', '_'))
        try:
            os.rename(p1, p2)
        except:
            print(p1)