import os
import msgpack
import zlib
import re

CUR_FOLDER = os.path.dirname(__file__)
NAMES_LIST_PATH = os.path.join(os.path.dirname(CUR_FOLDER), 'data', 'NamesList.txt')
OUT_PATH = os.path.join(os.path.dirname(CUR_FOLDER), 'ToolFiles', 'NamesList.mp.zlib')
CTRL_NAME = {
    k: v for k, v in zip(
        tuple(range(0x20)) + tuple(range(0x7F, 0x100)),
        ("NUL SOH STX ETX EOT ENQ ACK BEL BS HT LF VT FF CR SO SI DLE " +
         "DC1 DC2 DC3 DC4 NAK SYN ETB CAN EM SUB ESC FS GS RS US DEL " +
         "XXX(PAD) XXX(HOP) BPH NBH IND NEL SSA ESA HTS HTJ VTS PLD PLU " +
         "R1 SS2 SS3 DCS PU1 PU2 STS CCH MW SPA EPA SOS XXX(SGCI) SCI CSI " +
         "ST OSC PM APC").split()
    )
}


def edit_reserved(o):
    return (f"<reserved-{o.id:04X}, " +
            f"cross references: {o.xref[0]}>")


UNICODE_RE = re.compile(r"^([0-9a-fA-F]|10)?[0-9a-fA-F]{0,4}$")

characters: dict[int, "OneCharacter"] = {}

class OneCharacter:
    id = None
    name = None
    comment: list[str] = []
    xref: list[str] = []
    compat: list[str] = []

    def __init__(self, code, name):
        self.id = int(code, 16)
        self.name = name
        self.comment = []
        self.xref = []
        self.compat = []

    def update(self):
        global characters
        characters[self.id] = self
    
    def serialise(self):
        return {"code": "U+" + hex(self.id)[2:].upper().zfill(4),
                "name": (edit_reserved(self)
                         if (n := self.name) == "<reserved>"
                         else n),
                "comment": self.comment,
                "alias": [],
                "formal alias": [],
                "cross references": self.xref,
                "variation": [],
                "decomposition": [],
                "compat mapping": self.compat}


with open(NAMES_LIST_PATH) as f:
    current = None
    for line in f.readlines():
        def oneline(line):
            global current
            if len(line) == 0:
                return
            elif line[0] in ['@', ';']:
                return
            elif line[0] == '\t':
                if line[1] == '%':
                    return
                if line[1] == '=':
                    return
                if line[1] == ':':
                    return
                if line[1] == '~':
                    return
                if current is None:
                    return
                if len(line) < 3:
                    print(f'Malformed line: {line}')
                    return
                if line[1] == '\t':
                    return
                if line[1] == '*':
                    current.comment.append(line[3:].replace('\'', '"'))
                if line[1] == 'x':
                    current.xref.append("U+" + (
                        line.split(' ')[-1][:-1]
                        if line[3] == '('
                        else line[3:]).replace('\'', '"')
                    )
                if line[1] == '#':
                    current.compat.append(
                        ' '.join((
                            "U+" + s
                            if UNICODE_RE.search(s)
                            else s
                        ) for s in line[3:].split(' ')
                          if re.match('^([0-9A-F]+|<.*>)$', s))
                        .replace('\'', '"')
                    )
            else:
                if current is not None:
                    current.update()
                tokens = line.split('\t')
                if len(tokens) != 2:
                    print(f'Malformed line: {line}')
                    return
                if tokens[1] == '<not a character>':
                    current = None
                    return
                if tokens[1] == '<control>':
                    tokens[1] = ('<control-' +
                                 f'{CTRL_NAME[int(tokens[0], 16)]}>')
                current = OneCharacter(tokens[0], tokens[1])
        oneline(line.replace("\n", ""))
        if current is not None:
            current.update()

with open(OUT_PATH, "wb") as f:
    f.write(zlib.compress(msgpack.packb({k: v.serialise() for k, v in characters.items()})))
