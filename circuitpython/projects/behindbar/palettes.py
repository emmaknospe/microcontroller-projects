

def rainbow(index):
    index = index % 60
    if index < 10:
        return (int(255 * (10 - index) / 10), int(255 * index / 10), 0, 0)
    if index < 20:
        return (0, int(255 * (20 - index) / 10), int(255 * (index - 10) / 10), 0)
    if index < 30:
        return (0, 0, int(255 * (30 - index) / 10), int(255 * (index - 20) / 10))
    if index < 40:
        return (int(255 * (index - 30) / 10), 0, int(255 * (40 - index) / 10), 0)
    if index < 50:
        return (int(255 * (50 - index) / 10), int(255 * (index - 40) / 10), 0, 0)
    return (int(255 * (60 - index) / 10), int(255 * (index - 50) / 10), int(255 * (index - 50) / 10), 0)


BIPINK = (214, 2, 112)
BIPURPLE = (155, 79, 150)
BIBLUE = (0, 56, 168)


def bisexual_flag(index):
    index = index % 60
    if index < 20:
        return BIPINK
    elif index < 40:
        return BIPURPLE
    else:
        return BIBLUE


TRANSBLUE = (91, 206, 250)
TRANSPINK = (245, 84, 84)
TRANSWHITE = (120, 120, 120)


def trans_flag(index):
    index = index % 30 // 10
    if index == 0:
        return TRANSBLUE
    elif index == 1:
        return TRANSPINK
    else:
        return TRANSWHITE


LESBIANDARKORANGE = (213, 45, 0)
LESBIANORANGE = (239, 118, 39)
LESBIANLIGHTORANGE = (255, 154, 86)
LESBIANWHITE = (120, 120, 120)
LESBIANPINK = (209, 98, 164)
LESBIANDUSTYPINK = (181, 86, 144)
LESBIANDARKROSE = (163, 2, 98)


def lesbian_flag(index):
    index = index % 30
    if index < 5:
        return LESBIANDARKORANGE
    elif index < 9:
        return LESBIANORANGE
    elif index < 13:
        return LESBIANLIGHTORANGE
    elif index < 17:
        return LESBIANWHITE
    elif index < 21:
        return LESBIANPINK
    elif index < 25:
        return LESBIANDUSTYPINK
    else:
        return LESBIANDARKROSE


GAYDARKGREEN = (7, 141, 112)
GAYGREEN = (38, 206, 170)
GAYLIGHTGREEN = (152, 232, 193)
GAYWHITE = (120, 120, 120)
GAYLIGHTBLUE = (123, 173, 226)
GAYINDIGO = (80, 73, 204)
GAYBLUE = (61, 26, 120)


def gay_flag(index):
    index = index % 30
    if index < 5:
        return GAYDARKGREEN
    elif index < 9:
        return GAYGREEN
    elif index < 13:
        return GAYLIGHTGREEN
    elif index < 17:
        return GAYWHITE
    elif index < 21:
        return GAYLIGHTBLUE
    elif index < 25:
        return GAYINDIGO
    else:
        return GAYBLUE


def club(index):
    # return dark blue or violet based on index
    index = index % 60
    if index < 30:
        # return dark blue-violet
        return (148, 0, 211)
    else:
        # return violet-blue
        return (138, 43, 226)


def fast_club(index):
    # return dark blue or violet based on index, alternating more quickly
    index = index % 10
    if index < 5:
        # return dark blue-violet
        return (148, 0, 211)
    else:
        # return violet-blue
        return (138, 43, 226)


def fast_seafoam(index):
    # return seafoam green or seafoam blue based on index, alternating more quickly
    index = index % 10
    if index < 5:
        # return seafoam green
        return (0, 255, 127)
    else:
        # return seafoam blue
        return (0, 195, 255)


def seafoam(index):
    # return seafoam green or seafoam blue based on index
    index = index % 60
    if index < 30:
        # return seafoam green
        return (0, 255, 127)
    else:
        # return seafoam blue
        return (0, 195, 255)


def strobe(index):
    # return white or black based on index
    index = index % 2
    if index == 0:
        return (120, 120, 120)
    else:
        return (0, 0, 0)