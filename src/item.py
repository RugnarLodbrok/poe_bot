RARITY_CARD = 'Divination Card'
RARITY_CURRENCY = 'Currency'
RARITY_GEM = 'Gem'
RARITY_RARE = 'Rare'
RARITY_COMMON = 'Normal'
RARITY_MAGIC = 'Magic'
RARITY_UNIQUE = 'Unique'

SIZES = {
    'Gloves'
}


class Item:
    SIZE = None
    RARITY = None
    QUALITY = None

    def __init__(self, name=None):
        assert self.SIZE
        self.identified = True
        self.name = name
        self.rarity = self.RARITY
        self.quality = self.QUALITY
        # self.stats = None
        # self.implicits = []
        # self.explicits = []
        # self.base = None
        self.ilvl = 0
        self.req_lvl = 0
        self.req_str = 0
        self.req_int = 0
        self.req_dex = 0
        self.sockets = ""
        self.comment = ""
        self.unparsed = None

    def __repr__(self):
        return "{} {}".format(self.rarity, self.name)


class Currency(Item):
    SIZE = (1, 1)
    RARITY = RARITY_CURRENCY


class Gem(Item):
    SIZE = (1, 1)
    RARITY = RARITY_GEM

    def __init__(self, name):
        super().__init__(name)
        self.quality = 0


class Armor(Item):
    SIZE = (2, 2)

    def __init__(self):
        super().__init__()
        self.armor = 0
        self.es = 0
        self.evasion = 0


class ArmorBody(Armor):
    SIZE = (2, 3)


class Weapon(Item):
    SIZE = None

    def __init__(self):
        super().__init__()
        self.pd = None
        self.aps = None
        self.crit_chance = None
        self.range = None


class WeaponSmall(Weapon):
    SIZE = (1, 3)


class WeaponStandard(Weapon):
    SIZE = (2, 3)


class WeaponLarge(Weapon):
    SIZE = (2, 4)


class WeaponLong(Weapon):
    SIZE = (1, 4)


class Shield(Armor):
    SIZE = (2, 2)

    def __init__(self):
        super().__init__()
        self.block = None


class Bija(Item):
    pass


class Offering(Item):
    SIZE = (1, 1)


class Map(Item):
    SIZE = (1, 1)


class Card(Item):
    SIZE = (1, 1)
    RARITY = RARITY_CARD


class Flask(Bija):
    SIZE = (1, 2)


class Vessel(Flask):
    pass


class Belt(Bija):
    SIZE = (2, 1)


class Quiver(Bija):
    SIZE = (2, 3)


class Jewellery(Bija):
    SIZE = (1, 1)
