from functools import partial
import os
import csv
import json

CUR_FOLDER = os.path.dirname(__file__)

CONTINUOUS_RANGES = [
    (0x00, 0x20, 0x2400),
    (0x80, 0xA0, 0xE000),

    (0x180B, 0x180F, 0xF0000),
    (0x2000, 0x2011, 0xF0000),
    (0x2028, 0x202F, 0xF0000),
    (0x205F, 0x2064, 0xF0000),
    (0x2066, 0x206F, 0xF0000),
    # (0x2596, 0x259F, 0xF0000),
    # (0x2FF0, 0x2FFF, 0xF0000),
    (0xFE00, 0xFE0F, 0xF0000),
    (0xFFF9, 0xFFFC, 0xF0000),

    (0x13430, 0x13455, 0xF0000),
    (0x1BCA0, 0x1BCA3, 0xF0000),
    (0x1D173, 0x1D17A, 0xF0000),
    (0x1DA9B, 0x1DA9F, 0xF0000),
    (0x1DAA1, 0x1DAAF, 0xF0000),

    (0xE0020, 0xE007F, -0xD2000),
    (0xE0100, 0xE01EF, -0xD2000),
]

DISCRETE = {
    0x7F: 0x23A2,

    0xAD: 0xE000,
    0x34F: 0xE000,
    0x61C: 0xE000,
    0x890: 0xE000,
    0x891: 0xE000,
    0x2022: 0xF0000,
    # 0x2191: 0xF0000, 0x2193: 0xF0000, 0x2236: 0xF0000, 0x23F4: 0xF0000, 0x23F5: 0xF0000, 0x25C0: 0xF0000, 0x25B6: 0xF0000,
    0x2424: 0xF0000,
    # 0x2580: 0xF0000, 0x2584: 0xF0000, 0x258C: 0xF0000, 0x2590: 0xF0000, 0x25B2: 0xF0000, 0x25BC: 0xF0000, 0x25E6: 0xF0000, 0x2660: 0xF0000, 0x2663: 0xF0000, 0x2665: 0xF0000, 0x2666: 0xF0000,
    # 0x2B1A: 0xF0000,
    0x3000: 0xF0000,
    0x303E: 0xF0000,
    0xFEFF: 0xF0000,

    0x1107F: 0xF0000,
    0x11A47: 0xF0000,
    0x11D45: 0xF0000,
    0x11D97: 0xF0000,
    0x11F42: 0xF0000,
    0x16FE4: 0xF0000,
    0x1BC9D: 0xF0000,
    0x1D159: 0xF0000,

    0xE0001: -0xD2000,
}

CHAR_MAP = {
    # 连续区间
    **{
        code: chr(code + offset)
        for start, end, offset in CONTINUOUS_RANGES
        for code in range(start, end + 1)
    },

    # 离散点
    **{
        code: chr(code + offset)
        for code, offset in DISCRETE.items()
    }
}

NOT_CHAR = [
    *[(0x10000 * i + 0xFFFE, 0x10000 * i + 0xFFFF) for i in range(0, 17)],
    (0xFDD0, 0xFDEF)
]
CTRLS = {
  *sum([list(range(s, e + 1)) for s, e, _ in CONTINUOUS_RANGES], []), # sum(..., []) 用于扁平化列表。
  *DISCRETE
}
with open(
    os.path.join(CUR_FOLDER, 'ToolFiles', 'Blocks.csv'),
    encoding='utf-8'
) as blocks_csv:
    reader = list(csv.reader(blocks_csv, delimiter='|'))
    BLOCK_RANGES = [tuple(map(partial(int, base=16), line[0].split('..'))) for line in reader]
UNDEFINED_CHARACTER_LIST = set(range(0, 0x110000)) - set(json.load(open(
    os.path.join(CUR_FOLDER, 'ToolFiles', 'DefinedCharacterList.json'),
    encoding='utf8'
))) - CTRLS

def get_char(code: int) -> str:
    return CHAR_MAP.get(code, chr(code))

def get_char_in_last_resort(code: int) -> str:
    for i, (start, end) in enumerate(NOT_CHAR):
        if start <= code <= end:
            return 0x10B000 + i
    
    plane_index = code // 0x10000
    if plane_index < 0xF and not 0xD800 <= code <= 0xDFFF and code in UNDEFINED_CHARACTER_LIST:
        return 0x10A000 + plane_index

    for i, (start, end) in enumerate(BLOCK_RANGES):
        if start <= code <= end:
            return 0x100000 + i
    
    raise ValueError(f"No last resort mapping found for code point: U+{code:04X}.")
