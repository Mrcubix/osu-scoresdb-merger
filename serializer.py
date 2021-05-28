import struct

#parse = osudb.parse_score(r"./osu!MapSync/scores.db")
#with open('./osu!MapSync/output.txt', 'w') as f:
#    f.write(str(parse)) #[1:-1].split(',')

def serialize_type_exp(fobj, data_type,data=None):
    if data_type == "Boolean": ## False if 0x00 else True
        return struct.pack("<?", fobj)
    elif data_type == "Byte": ## 1 byte int
        return struct.pack("<s", fobj)
    elif data_type == "Double": ## 8 bytes floating point
        return struct.pack("<d", fobj)
    elif data_type == "Int": ## 4 bytes unsigned int
        return struct.pack("<I", fobj)
    elif data_type == "Long": ## 8 bytes unsigned int
        return struct.pack("<Q", fobj)
    elif data_type == "Short": ## 2 bytes unsigned int
        return struct.pack("<H", fobj)
    elif data_type == "Single": ## 4 bytes floating point
        return struct.pack("<f", fobj)
    elif data_type == "String": ## 0x00 or 0x0b - ULE128(n) - UTF-8(length=n)
        bb = fobj
        if bb == None:
            return None
        data = fobj
        data = data.encode("utf-8")
        return bytes([0x0b]) + serialize_type_exp(fobj, "ULEB128", len(data)) + \
            data
    elif data_type == "ULEB128": ## https://en.wikipedia.org/wiki/LEB128#Encode_unsigned_integer
        res = []
        while True:
            bb = data & 0b1111111
            data >>= 7
            if data:
                bb |= 0b10000000
            res.append(bb)
            if not data:
                break
        return bytes(res)
    else:
        raise NotImplementedError('parse_type(fobj, data_type): Unknown data type: "%s".' % data_type)

def serialize_types_exp(fobj, types):
    return [serialize_type_exp(fobj, i) for i in types]

score_data_types = ['Byte', 'Int', 'String', 'String', 'String', 'Short', 'Short', 'Short', 'Short', 'Short', 'Short', 'Int', 'Short', 'Boolean', 'Int', 'String', 'Long', 'Int', 'Long']

def serialize_scoredb_data(list):
    fobj = list
    with open("./output/scores.db", "wb") as otp:
        otp.truncate(0)
        for i in range(2):
            otp.write((serialize_type_exp(fobj[i],'Int')))
        for maps in fobj[2]:
            for i in range(2):
                if type(maps[i]) == str:
                    otp.write(serialize_type_exp(maps[i],'String'))
                if type(maps[i]) == int:
                    otp.write(serialize_type_exp(maps[i],'Int'))
            for scores in maps[2]:
                for idx, stats in enumerate(scores): 
                    if score_data_types[idx] == 'Byte':
                        otp.write(serialize_type_exp(bytes(stats), score_data_types[idx]))
                    elif stats == None:
                           otp.write(b'\x00')
                    else:    
                        otp.write(serialize_type_exp(stats, score_data_types[idx]))