#-*-coding:utf-8;-*-

"""
osudb - A database parser for osu! databases (osu!.db, scores.db, collection.db).
Version 0.1
Written by: KirkSuD
Written @ 2019/08/22
Last modified @ 2019/08/22
Current found bugs: None

Wiki: https://osu.ppy.sh/help/wiki/osu!_File_Formats/Db_(file_format)
Currently, 4 databases: osu!.db, scores.db, collection.db, and presence.db.
presence.db is not described on the wiki page and is not supported.

Roughly tested @ 2019/08/22
with osu!.db ver.20190816, collection.db ver.20190808, scores.db ver.20190524.

Roughly tested @ 2020/04/29
with osu!.db ver.20200320, collection.db ver.20200320, scores.db ver.20190828.

2020/04/12 update:
make a quick but bad fix for a change of beatmap information: bm[0] disappears now, all index -1.
TODO: make a better, easier to maintain DS to hold the beatmap info.

osu! directory path:
Windows: %localappdata%/osu!
Mac OSX: /Applications/osu!.app/Contents/Resources/drive_c/Program Files/osu!/
"""

import struct

### Helper Functions ###
def parse_type(fobj, data_type):
    """
    Read needed bytes from fobj and parse it according to data_type.
    """
    if data_type == "Boolean": ## False if 0x00 else True
        return struct.unpack("<?", fobj.read(1))[0]
    elif data_type == "Byte": ## 1 byte int
        return fobj.read(1)[0]
    elif data_type == "DateTime": ## 8 bytes signed int
        return struct.unpack("<q", fobj.read(8))[0]
    elif data_type == "Double": ## 8 bytes floating point
        return struct.unpack("<d", fobj.read(8))[0]
    elif data_type == "Int": ## 4 bytes unsigned int
        return struct.unpack("<I", fobj.read(4))[0]
    elif data_type == "Int-Double pair": ## 0x08-Int-0x0d-Double with AssertionError
        bb = fobj.read(1)[0]
        if bb != 0x08:
            raise AssertionError('parse_type(fobj, data_type): '
                '1st byte(%s) of "Int-Double pair" != 0x08' % bb)
        first_int = parse_type(fobj, "Int")
        bb = fobj.read(1)[0]
        if bb != 0x0d:
            raise AssertionError('parse_type(fobj, data_type): '
                '6th byte(%s) of "Int-Double pair" != 0x0d' % bb)
        return [first_int, parse_type(fobj, "Double")]
    elif data_type == "Int-Double pair*": ## int(n) - "Int-Double pair"*n
        return [parse_type(fobj, "Int-Double pair") for i in range(parse_type(fobj, "Int"))]
    elif data_type == "Long": ## 8 bytes unsigned int
        return struct.unpack("<Q", fobj.read(8))[0]
    elif data_type == "Short": ## 2 bytes unsigned int
        return struct.unpack("<H", fobj.read(2))[0]
    elif data_type == "Single": ## 4 bytes floating point
        return struct.unpack("<f", fobj.read(4))[0]
    elif data_type == "String": ## 0x00 or 0x0b - ULE128(n) - UTF-8(length=n)
        bb = fobj.read(1)[0]
        if bb == 0x00:
            return None
        elif bb != 0x0b:
            ## TODO: show integers in assertion error in hexadecimal and decimal
            ##       to make debug more convenient (cause I may inspect the file in a byte reader.
            raise AssertionError('parse_type(fobj, data_type): '
                '1st byte(%s) of "String" not in {0x00, 0x0b}' % bb)
        strlen = parse_type(fobj, "ULEB128")
        return fobj.read(strlen).decode("utf-8")
    elif data_type == "ULEB128": ## https://en.wikipedia.org/wiki/LEB128#Decode_unsigned_integer
        i = 0 ## derived from the wiki psuedo code
        res = 0
        shift = 0
        while True:
            bb = fobj.read(1)[0]
            i += 1
            res |= ((bb & 0b1111111) << shift)
            if (bb & 0b10000000) == 0:
                break
            shift += 7
        return res
    elif data_type == "Timing point": ## Double - Double - Boolean
        return parse_types(fobj, ["Double", "Double", "Boolean"])
    elif data_type == "Timing point+": ## int(n) - "Timing point"*n
        return [parse_type(fobj, "Timing point") for i in range(parse_type(fobj, "Int"))]
    else:
        raise NotImplementedError('parse_type(fobj, data_type): Unknown data type: "%s".' % data_type)

def parse_types(fobj, types):
    return [parse_type(fobj, i) for i in types]

### Main Functions ###
def parse_osu(file_path):
    fobj = open(file_path, "rb")
    res = parse_types(fobj, ['Int', 'Int', 'Boolean', 'DateTime', 'String', 'Int'])
    beatmaps_count = res[-1]
    res.append([])
    ## change @ 2020/04/12 due a change in Beatmap Information: Int: Size in bytes of the beatmap entry. Only present if version is less than 20191106.
    ## so beatmap_info[0] disappears, all index has to -1.
    ## TODO: Enhance parsed data structure, make it accessible by a key. Make it easier to maintain.
    #beatmap_data_types = ['Int', 'String', 'String', 'String', 'String', 'String', 'String', 'String', 'String', 'String', 'Byte', 'Short', 'Short', 'Short', 'Long', 'Single', 'Single', 'Single', 'Single', 'Double', 'Int-Double pair*', 'Int-Double pair*', 'Int-Double pair*', 'Int-Double pair*', 'Int', 'Int', 'Int', 'Timing point+', 'Int', 'Int', 'Int', 'Byte', 'Byte', 'Byte', 'Byte', 'Short', 'Single', 'Byte', 'String', 'String', 'Short', 'String', 'Boolean', 'Long', 'Boolean', 'String', 'Long', 'Boolean', 'Boolean', 'Boolean', 'Boolean', 'Boolean', 'Int', 'Byte']
    beatmap_data_types = ['String', 'String', 'String', 'String', 'String', 'String', 'String', 'String', 'String', 'Byte', 'Short', 'Short', 'Short', 'Long', 'Single', 'Single', 'Single', 'Single', 'Double', 'Int-Double pair*', 'Int-Double pair*', 'Int-Double pair*', 'Int-Double pair*', 'Int', 'Int', 'Int', 'Timing point+', 'Int', 'Int', 'Int', 'Byte', 'Byte', 'Byte', 'Byte', 'Short', 'Single', 'Byte', 'String', 'String', 'Short', 'String', 'Boolean', 'Long', 'Boolean', 'String', 'Long', 'Boolean', 'Boolean', 'Boolean', 'Boolean', 'Boolean', 'Int', 'Byte']
    for _ in range(beatmaps_count):
        res[-1].append(parse_types(fobj, beatmap_data_types))
    res.append(parse_type(fobj, "Int"))
    left_data = fobj.read(1)
    fobj.close()
    if left_data:
        raise AssertionError("parse_osu(file_path): file not empty after parsing!")
    return res

def parse_collection(file_path):
    fobj = open(file_path, "rb")
    res = parse_types(fobj, ['Int', 'Int'])
    collections_count = res[-1]
    collections = []
    for _ in range(collections_count):
        collections.append(parse_types(fobj, ["String", "Int"]))
        collections[-1].append([parse_type(fobj, "String") for _ in range(collections[-1][1])])
    res.append(collections)
    left_data = fobj.read(1)
    fobj.close()
    if left_data:
        raise AssertionError("parse_osu(file_path): file not empty after parsing!")
    return res

def parse_score(file_path):
    fobj = open(file_path, "rb")
    res = parse_types(fobj, ['Int', 'Int'])
    beatmaps_count = res[-1]
    beatmaps = []
    score_data_types = ['Byte', 'Int', 'String', 'String', 'String', 'Short', 'Short', 'Short', 'Short', 'Short', 'Short', 'Int', 'Short', 'Boolean', 'Int', 'String', 'Long', 'Int', 'Long']
    for _ in range(beatmaps_count):
        beatmaps.append(parse_types(fobj, ["String", "Int"]))
        beatmaps[-1].append([parse_types(fobj, score_data_types) for _ in range(beatmaps[-1][1])])
    res.append(beatmaps)
    left_data = fobj.read(1)
    fobj.close()
    if left_data:
        raise AssertionError("parse_osu(file_path): file not empty after parsing!")
    return res

