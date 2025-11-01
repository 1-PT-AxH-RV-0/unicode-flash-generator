import os
import re
import msgpack
import zlib

CUR_FOLDER = os.path.dirname(__file__)
NAMES_LIST_PATH = os.path.join(os.path.dirname(CUR_FOLDER), 'data', 'NamesList.txt')
OUT_PATH = os.path.join(os.path.dirname(CUR_FOLDER), 'ToolFiles', 'DefinedCharacterList.mp.zlib')
UNICODE_RE = re.compile(r"^([0-9a-fA-F]|10)?[0-9a-fA-F]{0,4}$")

res = set()

with open(NAMES_LIST_PATH) as f:
    for line in f.readlines():
        line = line[:-1]
        if line.startswith('@@\t'):
            block_start, block_name, block_end = line.split('\t')[1:]
            if (
                block_name.startswith('CJK Unified Ideographs') or
                block_name == 'Hangul Syllables' or
                block_name == 'Tangut' or
                block_name == 'Tangut Supplement'
            ):
                res.update(range(int(block_start, 16), int(block_end, 16) + 1))
        if (
            line and
            not line.startswith('\t') and
            len(line.split('\t')) == 2 and
            UNICODE_RE.search(line.split('\t')[0])
        ):
            code, name, *_ = line.split('\t')
            if name.startswith('<'): continue
            res.add(int(code, 16))

with open(OUT_PATH, 'wb') as f:
    f.write(zlib.compress(msgpack.packb(sorted(list(res)))))
