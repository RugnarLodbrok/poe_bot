import re

from item import *
from item_bases import ITEM_BASES

SEP = ': '
SIMPLE_RARITY = {RARITY_UNIQUE, RARITY_RARE, RARITY_MAGIC, RARITY_COMMON}


class IntRange:
    __slots__ = ['a', 'b']

    @staticmethod
    def from_str(s):
        m = re.match(r'(\d+)-(\d+)', s)
        return IntRange(m.group(1), m.group(2))

    def __init__(self, *args):
        if len(args) == 2:
            self.a, self.b = args
        elif len(args) == 1 and isinstance(args[0], str):
            m = re.match(r'(\d+)-(\d+)', args[0])

            self.a = int(m.group(1))
            self.b = int(m.group(2))
        else:
            raise ValueError(*args)

    def __int__(self):
        return int((self.a + self.b + 1) / 2)

    def __float__(self):
        return (self.a + self.b) / 2

    def __str__(self):
        return "{}-{}".format(self.a, self.b)


class Field:
    def __init__(self, attr_name, name, type=None, p=None, required=False):
        self.attr_name = attr_name
        self.name = name
        self.type = type or int
        self.required = required
        if p:
            self.pattern = p
        else:
            if self.type == int:
                self.pattern = r'(\d+) ?.*'
            elif self.type == float:
                self.pattern = r'([\d\.]+) ?.*'
            elif self.type == str:
                self.pattern = r'([\w\- ]+) ?.*'
            elif self.type == IntRange:
                self.pattern = r'([\d\-]+) ?.*'
            else:
                raise ValueError("explicit pattern required")

    def match(self, l):
        m = re.match(r'{}: {}'.format(self.name, self.pattern), l)
        if m:
            return self.type(m.group(1))
        return None


class Block:
    DEFAULT_PATTERN = r'(.+)'
    KEYWORDS = []
    FIELDS = []

    def __init__(self, data):
        self.data = data
        self.fileds = {f.name: f for f in self.FIELDS}
        self._cache = {}

    def __getitem__(self, item):
        if item not in self._cache:
            field = self.fileds[item]
            for l in self.data:
                v = field.match(l)
                if v:
                    self._cache[item] = v
                    return v
            else:
                if field.required:
                    raise KeyError(item)
                else:
                    self._cache[item] = None
                    return None
        else:
            return self._cache[item]

    def set_values(self, item):
        for f in self.FIELDS:
            v = self[f.name]
            if v:
                if not hasattr(item, f.attr_name):
                    raise TypeError("{} is not supposed to have {}".format(item.__class__.__name__, f.attr_name))
                setattr(item, f.attr_name, self[f.name])

    @classmethod
    def matches(cls, data):
        for k in cls.KEYWORDS:
            for l in data:
                if k in l:
                    return True
        for f in cls.FIELDS:
            for l in data:
                if (f.name + ':') in l:
                    return True
        return False


class TitleBlock(Block):
    FIELDS = [Field('rarity', 'Rarity', str, required=True)]

    def __init__(self, data):
        super().__init__(data)
        name_data = [x for x in data[1:] if x]
        print(name_data)
        self.name = " ".join(name_data)
        self.short_name = name_data[-1]
        self.end_name = self.short_name.split(' ')[-1]


class BasicBlock(Block):
    FIELDS = [
        Field('quality', 'Quality', int, r'\+(\d+)% ?.*'),
        Field('pd', 'Physical Damage', IntRange),
        Field('crit_chance', 'Critical Strike Chance', float, r'([\d\.]+)% ?.*'),
        Field('aps', 'Attacks per Second', float),
        Field('range', 'Weapon Range'),
        Field('armor', 'Armour'),
        Field('block', 'Chance to Block', int, r'\+(\d+)% ?.*'),
        Field('evasion', 'Evasion Rating'),
    ]

    def __init__(self, data, uniq=False):
        super().__init__(data)
        if uniq:
            self.name = data[0].strip()


class ReqsBlock(Block):
    KEYWORDS = ['Requirements']
    FIELDS = [
        Field('req_lvl', 'Level'),
        Field('req_str', 'Str'),
        Field('req_dex', 'Dex'),
        Field('req_int', 'Int')]


class SocketsBlock(Block):
    FIELDS = [Field('sockets', 'Sockets', str)]


class ILevelBlock(Block):
    FIELDS = [Field('ilvl', 'Item Level')]


class QuanityBlock(Block):
    FIELDS = [Field('quantity', 'Stack Size', int, r'(\d+)/\d+')]


def is_flask(name):
    return 'Flask' in name.split(' ')


def parse_item(data):
    blocks = [x.strip().split('\n') for x in re.split('-{4,10}', data)]

    title = TitleBlock(blocks[0])
    if title['Rarity'] == RARITY_CURRENCY:
        for b in blocks:
            item = Currency(title.name)
            if QuanityBlock.matches(b):
                block = QuanityBlock(b)
                block.set_values(item)
            return item
        else:
            raise ValueError("Currency missing quanity")
    elif title['Rarity'] == RARITY_GEM:
        for b in blocks:
            item = Gem(title.name)
            if BasicBlock.matches(b):
                block = BasicBlock(b)
                block.set_values(item)
            return item
        else:
            raise ValueError("Currency missing quanity")
    elif title['Rarity'] == RARITY_CARD:
        return Card(title.name)

    if title['Rarity'] not in SIMPLE_RARITY:
        raise ValueError(title['Rarity'])

    blocks = blocks[1:]

    if BasicBlock.matches(blocks[0]):
        if title['Rarity'] == RARITY_UNIQUE:
            block = BasicBlock(blocks[0], uniq=True)
            name = block.name
            item = ITEM_CLASSES[name]()
        else:
            block = BasicBlock(blocks[0])
            name = title.name
            if title.end_name not in ITEM_CLASSES:
                item = ITEM_BASES[title.short_name]()
            elif is_flask(title.short_name):
                item = Flask(title.short_name)
            else:
                item = ITEM_CLASSES[title.end_name]()
        item.rarity = title['Rarity']
        item.name = name
        block.set_values(item)
        blocks = blocks[1:]
    else:
        if is_flask(title.short_name):
            item = Flask(title.short_name)
        else:
            item = ITEM_CLASSES[title.end_name]()
        item.rarity = title['Rarity']
        item.name = title.name

    for p in [ReqsBlock, SocketsBlock, ILevelBlock]:
        for b in blocks:
            if p.matches(b):
                block = p(b)
                block.set_values(item)
                blocks.remove(b)
                break
    item.unparsed = blocks
    if item.rarity != RARITY_COMMON and "Unidentified" in blocks[-1]:
        print('undefind')
        item.identified = False
    return item


ITEM_CLASSES = {
    'One Handed Mace': WeaponStandard,
    'Hat': Armor,
    'Greaves': Armor,
    'Mitts': Armor,
    'Gloves': Armor,
    'Gauntlets': Armor,
    'Bascinet': Armor,
    'Boots': Armor,
    'Shield': Shield,
    'Buckler': Shield,
    'Sceptre': Weapon,
    'Quiver': Quiver,
    'Ring': Jewellery,
    'Amulet': Jewellery,
    'Jewel': Jewellery,
    'Belt': Belt,
    'Vise': Belt,
    'Flask': Flask,
    'Vessel': Vessel,
    'Goddess': Offering,
    'Map': Map,
}
