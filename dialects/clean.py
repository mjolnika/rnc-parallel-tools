# NOTE: every dialect is specific
# this code is only provided for users to know
# what some of the special symbols are
# without searching for them themselves

import re

filename = 'Текст-5.xhtml'
with open(filename, encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
newlines = []
for line in lines:
    if re.search('<se format="2">[^\[]', line):
        new_line = re.sub(' ([А-яёЁ́ɣlўё́-]+)([ ,/\.])', r' <w>\1</w>\2', line)
        newlines.append(new_line)
    else:
        newlines.append(line)

with open(filename, 'w', encoding='utf-8') as f:
    f.write('\n'.join(newlines))


with open(f'old{filename}'[:-5], 'w', encoding='utf-8') as f:
    f.write(text)
