from enum import Enum
from enum import IntEnum


class Day(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Dungeon(Enum):
    NONE = 0
    GIANT = 1
    DRAGON = 2
    NECRO = 3
    SPIRITUAL_REALM = 4
    STEEL_FORTRESS = 5
    CRYPT = 6
    MAGIC_ESSENCE = 7
    FIRE_ESSENCE = 8
    WATER_ESSENCE = 9
    WIND_ESSENCE = 10
    LIGHT_ESSENCE = 11
    DARK_ESSENCE = 12

    FIRE_RIFT = 13
    WATER_RIFT = 14
    WIND_RIFT = 15
    LIGHT_RIFT = 16
    DARK_RIFT = 17

    RAID = 18
    FIRE_RAID = 19
    WATER_RAID = 20
    WIND_RAID = 21


class Rta(Enum):
    NONE = 0
    REGULAR = 1

    SL_FOUR_STARS_ONLY = 2
    SL_BAN = 3
    SL_ONLY_RGB = 4
