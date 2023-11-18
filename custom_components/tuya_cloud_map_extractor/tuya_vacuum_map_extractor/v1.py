import numpy as np

from .const import colors
from .pylz4 import uncompress

def _hexStringToNumber(bits):
    number = []
    for i in [bits[i:i+2] for i in range(0, len(bits), 2)]:
        number.append(int(i, 16))
    return number

def _chunk(In, n):
    out = []
    for i in [In[i:i+n] for i in range(0, len(In), n)]:
        out.append(i)
    return out

def _highLowToInt(high, low):
    return low + (high << 8)

def _numberToBase(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]

def decode_header_v1(header: str):
    maxmin = list(map(lambda x: _highLowToInt(x[0], x[1]), _chunk(_hexStringToNumber(header), 2)))
    return {
        'id': list(map(lambda x: _highLowToInt(x[0], x[1]), _chunk(_hexStringToNumber(header[2:6]), 2))),   
        'version': _hexStringToNumber(header[0:2]),
        'roomeditable': True,   
        'type': _hexStringToNumber(header[6:8]),
        'width': maxmin[2],
        'height': maxmin[3],
        'originx': maxmin[4],
        'originy': maxmin[5],
        'mapResolution': maxmin[6],
        'pileX': maxmin[7],
        'pileY': maxmin[8],
        'totalcount': int(header[36:44], 16),
        'compressbeforelength': int(header[36:44], 16),
        'compressafterlenght': maxmin[11]
    }

def decode_roomArr(mapRoomArr):
    rooms = []
    roomCount = _hexStringToNumber(mapRoomArr.hex()[2:4])[0]
    infoByteLen = 26
    nameByteLen = 20
    bytePos = 2 * 2
    for i in range(roomCount):
        roomInfoStr = mapRoomArr.hex()[bytePos:(bytePos + (infoByteLen + nameByteLen + 1) * 2)]
        data = list(map(lambda x: _highLowToInt(x[0], x[1]), _chunk(_hexStringToNumber(roomInfoStr[0:16]), 2)))
        data2 = _hexStringToNumber(roomInfoStr[16:28])
        nameLen = _hexStringToNumber(roomInfoStr[52:54])[0]
        vertexNum = _hexStringToNumber(roomInfoStr[-2:])[0]
        vertexStr = mapRoomArr.hex()[(bytePos + (infoByteLen + nameByteLen + 1) * 2):(bytePos + (infoByteLen + nameByteLen + 1) * 2 + vertexNum * 2 * 2 * 2)]
        bytePos = bytePos + (infoByteLen + nameByteLen + 1) * 2 + vertexNum * 2 * 2 * 2
    
        rooms.append({
            'ID': data[0],
            'name': bytes.fromhex(roomInfoStr[(infoByteLen * 2 + 1 * 2):(infoByteLen * 2 + 1 * 2 + nameLen * 2)]).decode(),
            'order': data[1],
            'sweep_count': data[2],
            'mop_count': data[3],
            'color_order': data2[0],
            'sweep_forbidden': data2[1],
            'mop_forbidden': data2[2],
            'fan': data2[3],
            'water_level': data2[4],
            'y_mode': data2[5],
            'vertexNum': vertexNum,
            'vertexStr': vertexStr
        })

    return rooms

def to_array_v1(pixellist: list, width: int, height: int) -> np.array:
    pixels = []
    height_counter = 0
    while height_counter < height:
        width_counter = 0
        line = []
        while width_counter < width:
            pixel = colors.v1.get(pixellist[width_counter + height_counter * width])
            if not pixel: 
                pixel = (20, 20, 20)
            line.append(pixel)
            width_counter = width_counter + 1
        pixels.append(line)
        height_counter = height_counter + 1
    return np.array(pixels, dtype=np.uint8)

#customdata = b"\x01\x00\x00\x01\x01F\x014\x00\x00\x00\x00\x00\x05\x05\xb4\x06\x18\x00\x01\x88\xf4\x15(\x1f\xf3\x01\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff,\x1e\xf1\x01\x00\x0f.$\xff <\xf1\xf1\x04\x01\x00\x06F\x01\x0ea\x01\x0fc\x01\xff\x05\x0eE\x01\x08F\x01\x0ca\x01\x08c\x01\x0f\x02\x00\xf9\x0fF\x01\xff\xffT\x00\xc4\x04\x0f\x02\x00\x03\t\x8b\x03\x0f\x8c\x02\xff\x0c?\xf1\xf1\x10\x01\x00\x04\x07H\x01\x00f\x01\x00\xed\x04\n\x02\x00\x0f\x18\x05\xf7\x0fE\x01\x076\x10\x10\x10\x8d\x02\n?\x01\x03\x02\x00\x00\\\x01\x03\x02\x00\x03\x12\x00\x07\x02\x00\x06c\x01\x0f\x02\x00\xd0\x0f\x8a\x02\x06\x00\x02\x00\x05\x00\x01?\xf1\xf1\x04+\x01\x02\x0f\x02\x00\x08\x0fF\x01\xff\x01\x1f\xf3C\x01\x14\x07\'\x00\x0fF\x01\xf5\x06\x17\x05\x00G\x01\x0fw\x02\x08\x01;\n\x0c~\x06\x0fF\x01*\x07\x93\x05\x0f\x02\x00\x92!\xf1\xf3\x00\x05\x00\xc0\x03\x1b\x10\xde\x03!\xf1\xf3\xf5\x04\x02\xc7\x00\x0c%\x01\x0b\x02\x00\x0e\x1f\x00\x0fF\x01)2\xf1\xf3\x04v\x00\x0f\x02\x00\x9c\x00\x04\x05\x0ci\x06\x11\xf1\x11\x00\x01J\x01\x0ek\x02\x0f\x02\x00\x0e\x0fF\x01*\x1f\x04F\x01\xa8\x01\x91\x02\x0c\x02\x00_\xf1\xf1\x10\xf1\x10[\x06\x1a\x11\xf3b\x01\x0fF\x01\xde\x00\xd6\x03\x00s\x02\x0cA\x01\x02\x02\x00\x01\xe8\x03\x077\x06\x0f\x02\x00\x14\x0fF\x01,\x0f?\x00)\x0f\x02\x00b\x01?\x01\x01,\x01\x0f\x02\x00\x07\x00e\x03\x0f\x02\x00\x15\x03\x8c\x02\x00\x98\x01\x03[\x05\x00\x02\x00\x0f\xdb\x00\x19\x10\xf1\xee\x07\x0fH\x01\x9d\x07\x15\x05\x0fM\x01\x05\x0f\x8c\x02\x1f\x01\x02\x00\x06\n\x04\x01\x16\x01\x04\x05\x00\x01\x08\x00\x0f\x02\x00\x08\x01\xac\x06\x0f \x00\x08\x0f\x02\x00\x811\xf1\xf1\x10\x05\x00\x00\x8a\x02\x02\x06\x00\x0e\x02\x00\x0fF\x01$\x06\xc3\x02\x03A\x00\x13\xf1#\x01\x0fi\x02\x0b\x0fF\x01\xa2\x00\xb1\x03\x03?\x01\x01\xf8\x08\x04E\x01\x03\x14\x00\x00\x02\x00\x03\x05\x01\x0f\x02\x00\x01\x1f\x05\x15\x00\x01\x0f\x02\x00\x05\x0fF\x01\xca\x11\x10\x1c\x05\x03\x02\x00\x08\x0c\x00\x04\x02\x00\x0fF\x01\x08\x0f\x02\x00\x1a\x034\t\x1f\xf3\x8c\x02\x10\x0f#\x00\x0b\x0f\x02\x00~\x07s\x02\x00\x02\x00\x02\'\n\x0b\x02\x00\x0fF\x01\x19\x02^\x06\x0f\x02\x00\x04\x03*\x05\x0f#\x01\x0b\x01\xd2\x03\x0f#\x00\x0b\x0f\x02\x00}\t{\x02\x01\xfa\x05\x0bB\x01\x00\x02\x00\x0fF\x01\x19\x0f\x02\x00\x0b\x01J\x00\x0f\xb3\x07\x0c\x02F\x01\x0fG\x01\x9a\x07\x8b\x02\x0fD\x01\x05\x00\x1a\x00\x0f\x1c\x01\x0b\x07\x02\x00\x0f\x8b\x02\x08\x00\x1b\x00\x01J\x00\x0fJ\x02\x0c\x01F\x01\x00,\t\x0f(\x00\x0c\x0f\x02\x00x\x00\x9c\x0c\x00)\x01\x00\x02\x00\x06\n\x00\x0b\x02\x00\x01\xfc\x00\x0f\x02\x00\x13\x00+\x01\x0f\x02\x00\x08\x01J\x00\x0f\xff\x00\x0c\x02F\x01\x0f\'\x00\x0e\x0f\x02\x00w7\xf1\xf1\xf3\x86\x10\x0fF\x01Q\x00f\x01\x0f\xad\x03\x0c\x0fF\x01\x9f\x08u\x02\x0f\x13\x05\x02\x01\x02\x00\x01B\x02\x0f\x02\x00\x13\x00&\x01\x0f\x02\x00\t\x00 \x00\x0fF\x02\x0c\x04F\x01\x0fm\x01\x0c\x0f\x02\x00w\x04~\x02\x01\x08\x00\x01\x05\x00\x0f\x02\x00\x02\x0fF\x01$\x15\x05M\n\x05\n\x00\x01\x22\x01\x0f\x1f\x01\x0c\x01$\x00\x00\x1a\x05\x0f(\x01w\x0f\x02\x00\x0b\x05\x16\x05\x00\xbc\x11\x0fF\x01\x0b\x01\x7f\x19\x02\x05\x00\x00\x87\x06\x01\xe8\x00\x04\x02\x00%\xf1\xf33\x0f\x00l\x02\x04\x02\x00%\x05\x07\n\x00\x04P\x01\x01\x1f\x00\x0fF\x01\x14\x0f\xbb\x00\x0b\x0f\x02\x00y\x06{\x02\n\xde\x03\n\x02\x00\x04\x1e\x02\x03\x02\x00\x00F\x01\x057\x01S\xf1\xf1\xf1\xf0\xf0\x19\x00\x0f\x02\x00\x0f\x0fF\x01\x1f\x01b\x00\x0fx\x01\x0c\x0f\x02\x00m\n.\x01\x0f\x02\x00\x05\x0cF\x01\x01\x0c\x01\x03\x02\x00O\xf1\x04\xf3\x04F\x01\x12\x03\x8f\x02\x00\xc9\x16\x0f\x15\x01\x0b\x04n\x00\x00&\x00\x03\xa7\x0b\x0f\'\x01m\x0f\x02\x00\x0b\x00\xc5\x03\t\xa7\x07\x0f\x02\x00\x03\x04\xd8\x00\x03\x02\x00\tF\x01\x00\x02\x00\x0fF\x01\x12\x07\x02\x00\x1f\xf3\x0c\n\n\x04n\x00\x01\xb3\x18\x006\x00\x0f.\x00\n\x0f\x02\x00p\x02/\x03\x0f\xf6\r\x02\x08\x02\x00\x04\xd8\x00\x03\x02\x00\x0b\x0f\x00\x0fF\x01\x1f\x00\x89\x01\x0f\xfe\x00\x07\x0c_\x00\x0fE\x01\x8d\x04\x02\x00\x00\x93\x02\x0f\x02\x00\t\x0b\xd8\x00\x0f\x8c\x02.\x0f\xe0\r\x0b\x0cn\x00\x0fr\x01\t\x0f\x02\x00y\x0fF\x01\x1d\x00N\x02\x08\x02\x00\x0f\xd2\x03\x1e\x0f\xfd\x00\n\x0cF\x01\x0f-\x00\n\x0f\x02\x00x\x0fF\x01]\x0f^\x02\x0b\x0bF\x01\x0fH\x13\x0c\x0f\x02\x00w\x0fF\x01,\x0f\xea\x08\x15\x03\xa6\x07\x0fF\x01\x1c\x0f\x8d\x02\x96\x0fF\x01S\x05\xc1\x0c\x0f\x18\x01\x0b\x02\x98\x07\x07\x02\x00\x04/\n\x04\x08\x00\x0f\x02\x00\x85\x0fF\x01^\x0f\xd3\x03\t\x0b\xd1\x03\x00\x02\x00\x01G\x08\x00t%\x01\xfd\x08\x0fF\x01\xeb\x07\x02\x00\x0f\t\x01\t\x0fF\x01\x00\x01\x02\x00\x00F\x01\x00\x1c\x00\x0f<\x00\t\x0f\x02\x00j\x0f\x8c\x02,\x00\xdc\x00\x0f\x02\x00\x10\x05\x17\x05\x0f\x19\x05\x0b\x0fN\x00\x08\x00\xed\x03\x0f\x8c\x02\xc6\x0f\xf8\x00\x08\x08\x02\x00\x05\x9c\x10\x0fw\x07\x0b\x0fN\x00\x0b\x0f;\x00\n\x0f\x02\x00k\x0f\x8c\x02S\x06\x02\x00\x0f\x17\x05\t\x06\xc5\x1e\x0f\x02\x00\x02\x0f;\x00\n\x0f\x02\x00k\x0fF\x01\r\x0b\xd0\x00\x0c.\x02\x0c\x10\x00\x0f\x02\x00\x0e\x0f\x0b\x01\n\x0fN\x00\x0b\x0f;\x00\n\x0f\x02\x00k\x0fF\x01\r\x0b~\x10\x0c\xe8\x00\x0c\x10\x00\x0f\x02\x00\x0e\x0f\x0b\x01\n\x0fN\x00\n\x0f\x16\x05\x87\x0fF\x01\x9a\x00\xaf\x00\x0f\x02\x00\x84\x0f\x8c\x02\x0c\x0b\x8b\x02\rH\x0f\x0f>\x02\n\x0f\x02\x00\x01\x07\x8c\x02\x0e]\x02\x0fN\x00\n\x07:\x00\x0f\x02\x00~\x0fF\x01\r\x0bG\x01\x0c\xe8\x00\x0c\x10\x00\x0f\x02\x00\x0e\x07\x0c\x01\x00g\'\n\x10\x01\x0fN\x00\n\x07:\x00\x0f\x02\x00~\x0fF\x01\x0c\x0b\xd8\x00\x00\xb6\t\t\x02\x00\x0b \x00\x0f\x02\x00\x0f\x07\x0c\x01\x0fF\x01\x1d\x07;\x00\x0f\x02\x00}\x0fF\x01[\t\x10\x0f\x0fF\x01\x1c\x0fG\x01\x89\x0fF\x01\r\n\xd2\x03\x0f\x8c\x02\x19\x06\x82\x10\x07\x02\x00\x08P\x02\x0fF\x01\x1d\x0fG\x01\x88\x0fF\x01\r\x07\x02\x01\x01\xc8\x00\x01\x07\x00\x06\x02\x00\x0f\xd2\x03\x1d\x0fF\x01%\x00r\x01\x00\xc5\x01\x0f\xcb\x03}\x03\x02\x00\x0fF\x01\x1b\n\x9a\x02\x00W\x01\x01\x06\x00\x0f\x02\x00\x17\x0fF\x01&\x11\xf1k\x00\x0fG\x01}\x00o\x12\x01\x02\x00\x0fu\x19\t\x00\xf3\x1f\x05;\x010\xf3\xf1\xf3\xce%\x01z\x19\x01:\x00\x01\x02\x00\x0fA\x01\x17\x01\x02\x00\x0fF\x01%\x12\xf3F\x01\x0c\xd5\x07\x0f\x02\x00m\x0f\x84\x02\x0c\x04\x02\x00\x03\'\x01\x00\x04\x02\x02\x13\x00\x03\x11\x00\x01\x02\x00\x00\x17!\x01\t\x00\x0f\x02\x00\x17\nF\x01\x0c`\x10\x0f \x04\x0f\x00\x89\x00\x00q\x0f\x00\x93!\x01\n\x00\x0f\x02\x00k\x00F\x01\x01M\x02\x01\x1d\x01\x03\x07\x00\x0e\x02\x00\x00\'\x00\t\x02\x00\x0f_9\x15\x0f\x02\x00\x04\x03\x06\x01\x01\x02\x00\x1d\xf1Z\x02\x0fF\x01\x0f\x00\x0e\x03\x02[\x00\x0fF\x01v\x00\x07=\x01\'\x01\x00O\x01\t,\x01\x05\x02\x00\x01\x1f\x00\t\x02\x00\x04\xc6\x00\x0f\x02\x00$\x07\xfd\x00\x1d\xf1\x11\x1c\x0fF\x01\x10\x05\x02\x00\x07I\x00\x0f\x02\x00g\x01\x1f\x01\x00\x1c\x03\x00#\x01\x00\x010\x01\x11\x00\r\x02\x00\x0e\x16\x00\x0f\xea\x00\x19\x0f\x02\x00\x00\x00\xb1\x01\x04\x02\x00\x0fF\x01\x1e\x003\x00\x03T\x00\x0c\r\x04\x0f\x02\x00c\x01\x1f\x01\x07F\x01\x02O\x01\r\x02\x00\x01\'\x00\t\x02\x00\x0fF\x01,\t\x02\x00\x0cP\x02\x0f\\\x00\r\x00F\x01\x02\'\x08\x0fE\x01s\x015\x01\x00\xa5\x04\x01\'\x01\x00G1\x00\xf12\x0f\x02\x00\x11\x0f\xea\x00\r\x06\x02\x00\x07\'\x18\x0f\x02\x00\x04\x0fF\x01\x1d\x02I\x05\x0e8\x00\x0f\x02\x00f\x00>\x01\x00\xa5#\x00\x08\x00\x00\x22\x05\x01\x06\x00\x0f\x02\x00\x10\x0f\x96\x07\x18\x0f\xbd\x0c\x02\t\x02\x00\x00F\x01\x04\xdf\x03\x01\x02\x00\t\x1e\x00\x0f\x02\x00\x00\x001\x00\x17\xf3\xc6\x1a\x01\x10\x00\x0f\x02\x00h\x03>\x01\x0f\x02\x00 \x0f\xdd\x00\x00\x0f\x02\x00%\x00:\x01\x02\xa2\x03\x01\x02\x00\x0fF\x01\x16\x01Q\x05\x003\x00\x0fF\x01\xa7\x10\x10\xbf\x00\x0f\x02\x00d\x016\x01\x05b\x06\x03\x10\x00\x0f\x02\x00h\x0f\x8c\x02\'\x0f\x8e\x02:\x0f\x02\x00\x1c\x00\xca\x05\x01\xd4\x03\x03\x02\x00\x01V\x01\x0f\x02\x00h\x0fF\x01)\x0f\x8e\x02h\x007\x01\x03B\x01\x00\xd9\x03\x00\x0f\x00\x0f\x02\x00i\x0fF\x01*\x0fG\x01g\x007\x01\x01A\x01\x02\x02\x00\x00\x0f\x00\x0f\x02\x00i\x0fF\x01+\x0fG\x01f\x00h\t\x01\x85\x06\x00\t\x00\x0fF\x01\xff\'\x01\xd2\x07\x00B\x01\x01K\x01\x02@\n\x0f\x02\x00h\x0f\x8c\x02\xa4\x01F\x01\x00\x02\x00\x0fF\x01\xff*\x00\x03\x0e\x00\x8a\x02\x01\n\x00\x0f\x08\x0ep\x0f\x8c\x02\xa0\x00\xa4\x0b\x02\xcf\x03\x01\xcc\x03\x00\x07\x00\x0f^\x06\xff\x06\x00c\x02\x0f\x02\x00\x04\x02G4\x03!\x00\x0fF\x01\x88\x10\x11T\x0b\x22\x10\x11\x07\x00\x0f\x02\x00\n\x0f\xe9\x00\x04\x0f\x02\x00,\x00n\x02\x03&\x01\x0f\x02\x00\x13\x0f\x8c\x02\xac\x0f\xeb\x08@\x01s,\x03D\x01\x0f\x0f\x12\x04\x05 \x00\x04\x02\x00\x0fF\x01\xad\x0fG\x01=\x01\x87\x02\x03D\x01\x0f\x0f\x12\x0c\x05&\x00\x0fF\x01\xb0\x0fG\x019\nC\x01\x00\x02\x00\x06}+\r\x02\x00\x01L\x0f\x02\xfa\x1a\x01\x0b\x00\x0f\x02\x00h\x0fh\x19\x05\x0f\x02\x00\x19\r\xe0\x00\x0f\x02\x00#\x01C\x01\x05\x08\n\x03\x02\x00\x0f\xd3\x03\x04\x00\x02\x00\x03;\x01\x0f\xcd\x03m\x00\x02\x00\x0f\xe9\x08,\x02\x02\x00\x00\xd4\x00\x0f\x02\x00\x08\x00\x98\x08\x0f\x02\x00\x0b\x01A\x01\x0eC\x01\x0f\x02\x00\x0c\x0f@\x01q\x02\x02\x00\x0fF\x012\x0c\x80\x22\n\x02\x00\x07\xe7\x04\x0f\x02\x00\x05\x016\x1b\x0f\x1d\x00\x05\x0f\x02\x00\x06\x0fF\x01\xbe\x07\xe9\x05\x00\n\x0b\x08\x0f\x00\x0fc\x02\x11\x00F\x01\x01:\x00\x0f\x02\x00\x1a\x0fF\x01\xd8\x0f\x8a\x02\x10\x01\x10\x01\x08y\x01\x0f\x02\x00\x14\x0fF\x01\x8c\x04o\x0b\x04\x08\x00\x0f\x02\x00\x0e\x0b\x8f\x03\x07\x0f\x00\x0fE\x01\x12\x00\x93\x11\x00\x18\x05\x06\x02\x00\x0fH\x01\x0e\x01+\x00\x02\x95\x04\x0f\x02\x00p\x0f\x18\x05\n\x15\x11G\x01\x05\t\x00\x0f\x02\x00\x03\x0b\xf7\x00\x06\x0f\x00O\xf3\xf1\xf1\x0c\x12\x01\x0e\x0e\x90(\x01$\x01\x0f8\x00\x0e\x0f\x8c\x02\x80\x05O\x01\x08\xf7\r\x0f=\x01\x0c\x05\x02\x00\x0b\xf3\x00\x05\x0f\x00\x00E\x01\x1f\x0cG\x01\x03\x01)\x01\x04\x02\x00\x0fO\x02\x01\x0f\xe3\x03\x0e\x0f\xd1\x1ft\x00\x02\x00\x05=\x01\x05\x02\x00%\x11\x13\x0b\x00\x0f\x02\x00\x16\x057\x01\x02\x02\x00\x05\x01\x01\x01E\x01\x0fG\x01\x01\x1f\xf3J\x02\x0f\x05E\x00\x0f\x02\x00\x05\x0f\x8b\x02w\x01\x1b!\x0f\x02\x00/\x0fF\x01\x04\x03E\x01\x06\x02\x00\x02\x11\x01\x01\x88G\x0fJ\x02\x0e\x0fF\x01\xdf\tJ\x1a\x04@\x15\x00\xef\x04\x06A\x01\x02\x02\x00\x01G\x01\x0fE\x02\x13\x03\xee\x03\x012\x00\x0f\x02\x00\x02\x0fG\x00\x13\x0f\x02\x00R\x0e\xd2\x03\x0f\x02\x00!\x03\xe6\x00\n\xf4\x00\x0fE\x01\x00\x02G\x01\x0f\xff\x00\x19\x02?\x14\x0f\x02\x00\x02\x0fG\x00\x19\x0f\x02\x00L\x0fF\x01\x04\x16\x11\x9f\x07\x02\x02\x00\x0fh\x06\x0b\x03\xe6\x00\t\xf3\x00\x1d\xf1\xd0\x03\x01\x02\x00\x00\xa4\x02\x0f\xd4\x00\x19\x03\x93\x02\x05\x02\x00\x01<\x00\x00A\x01\x03\x0b\x00\x0f\x02\x00r\x04F\x01\x04\x08\x00\x03\x02\x00\x19\x11\xab\x07\x0f\x02\x00\x07\x05\xdd\x00\x03\xe8-\x06\x02\x00\x0fE\x01\x04\x00G\x01\x1f\x0c\xfa\x00r\x0f\x02\x009\x04>\x01\x04\x08\x00\x03\x02\x00\x13\x11\xe9\x16\x0f\x83\x02\x0b\x017*\x05\x02\x00\x01K\x01\x07\x02\x00\x003\x01\x08\x02\x00\x06\x12\x00\x053\x00\x0f\x02\x00\xb5\x05>\x01\x05\t\x00\x01\x02\x00\x0fF\x01!\n\x02\x00\x02\xe4\x08\x07\x02\x00\x01\x9a\x07\x03\x02\x00\n+\x00\x0f\x02\x00\xaf\n=\x01\x00m\x19\x03\x06\x00\x0f\x86\x02\r\x02\x02\x00\x00\xa1\x04\x0f\x02\x00\x03\x0fF\x01\x00\x0f)\x00\x03\x0f\x02\x00\xb1\rF\x01\x02\x02\x00\x00^\x06\x0ca\x06\x0f\x02\x00\x01\x0f\x1b\x01\x07\x0fF\x01\xf4?\x13\x13\x13b\x06\x0f\x0fF\x01\x07\'\xf3\xf3\xce\x03\x00\x02\x00\x0f+\x00\t\x0f\x02\x00\xad\x0f\x8c\x02\x05\x11\x10F\x01\x05G\x01\x05\t\x00\x0b\x02\x00\x0f\x1b\x01\t\x00;\x01\x07\x02\x00\x0f+\x00\t\x0f\x02\x00\xad\x0fF\x01\x0c\x04>\x01\x04\x08\x00\x0c\x02\x00\x0f\x1b\x01\t\x07B\x01\x00\x02\x00\x0f+\x00\t\x0f\x02\x00\xad\x0fF\x01\x07\x00\x19\x05\x0c5\x01\r\x02\x00\x0e\x1b\x01\x03\x86\x07\x0e/\n\x0e+\x00\x0f\x02\x00\xb7\tF\x01\x06r\x02\x0f\xa4\x07\x16\x010\x01\x00s\x0b\x02\x8c\x1f\x0e=\x01\x05\x02\x00\x0f\xe0\x08\xbf\x06\x02\x00\tF\x01\x06\x02\x00\x0f\xbc\x0c\x15\x04\x02\x00\x00F\x01\x050\x01\x0f\x02\x00\x04\x0f\x8d\x02\xc8\x0fF\x01\x04\x0f\x02\x00\x1d\x0fF\x01\xff\xff\\\x063\x05\x0e\x02\x00\x00\x0f\x05\x0fg\x0b\x00\x0c\x02\x00\x0f\xd2\x03\xda\t1\x18\x0f=\x01\t\x02\x02\x00\x00V\x06\x00\x04\x00\x06l\x10\x0f\x02\x00\x05\x0fF\x01\xda\t\xe0\x08\x0fF\x01\x0f\x10\x10\x88\x02\x1f\xf0:\x01\x05\x08\x02\x00\x0fF\x01\xda\x04\x02\x00\tN\x01\x0f\x02\x00\t?\xf3\xf3\xf0F\x01\xff\x08\x0f\x02\x00\x15?\xf1\xf3\xf0F\x01\xff0\x00Oc\x0f\x8b\x02\x12\x0f\xd2\x03\xe3\x0f\x02\x00\x13\x1f\xf3\x8b\x02\x16\x0fF\x01\xff\x08\x00_\x02\x0f\x8b\x02\x15\x0fF\x01\xff\x07\x00\x16 \x1f\xf1F\x01\xff.\x00\x8e\x0f/\xf1\x10F\x01\xff.\x00\xe9w/\x10\x10\xa1\x07\x13\x0f\xd2\x03\xdd\x0fi\x0b\x10\x05\x02\x00/\xf1\xf3\x8b\x02\x17\x0f\x18\x05\xe1\x0ft\x0b\x12\x0f\x8b\x02\x1a\x0fF\x01\xc8\x0f\xa91*\x00E\x01\x0f\xd1\x03\x17\x0fF\x01\xc9\x05\x9d\x03\x0f\x02\x00 \x00\xc0H\x0f\x16\x05\x16\x0fH\x0f\xc9\x0f\x8c\x02*\x00\x02\x00\x0f\xb7\x0c\x13\x01\x02\x00\x00]\n\x0f\x02\x00\xc5\x00\x0b\x01\x0f\x02\x00(\x01 \x01\x0f\x02\x00\x13\x0fF\x01\xff\x0f\x00\x1e\x13\x0fK\x01\x0e\x0fF\x01\xc8\x00_\x15\x03\x02\x00\x00\xe7\x04\x0f\x02\x00\x1e\x02<\x01\x00w\x19\rS\x22\x0c\x02\x00\x0fF\x01\xc8\x07\x02\x00\x00\xb4M\x0fF\x01\xff0\x00\xcf\r\x0fF\x01(\x0c{\x02\r\x02\x00\x0f\x8c\x02\xd3\x0fF\x01\xff\xff\xff\xf7\x11\x10\xff\x04\x00\xa4\x07\x01\t\x00\x0f\x02\x00\t\x0f\x18\x05\xff\t\x02\xec\x08\x0fF\x01\xff\x11\x02\xb4\x1f\x0f\x02\x00\x0b\x0f\x1b!\x10\x0f\x8e\x10\xc8\n\x02\x00\x0f\xea\x08\x04\x0f\x8b\x03\x12\x0fu\x0b\x0e\x0fF\x01\xd5\x0f\x9b\x10\x01\x00\x9b(\x0fF\x01\xff\x1d\x00\xe7\x04\n\x02\x00\x00\xac\x03\x0f\x02\x00\x13\x0f\x8c\x02\xf5\x0f\x8b\x02\x02\x0fC\x01\x13\x00\r\x1c\x0f\x9f\x07\t\x01\x02\x00\x0f\xd3\x02\x12\x0f\x02\x00\xae\x0f\x16\x05\x01\x0f\xfa\x00\x17\x0f\x8c\x02\xf4\x0f\x8b\x02\x01\x0f\x8c\x02\xff \x0f\x8b\x02\x01\x02\xfe.\x0ff\x03\x12\x0f\x8c\x02\xf5\nX\x06\x06\x02\x00\x0f\xd6\x03\x13\x0fF\x01\xff\xffV\x07\xb7\x0c\x0f\xdd\x03\x07\x0f\x8c\x02\xf4\x0f1\x18\x11\x00\xd2\x08\x06T\x01\tS\x01\x0fF\x01\xf3\x001\x9f\x0f\x02\x00\x1b\n0\x05\x0fF\x01\x0b\x01{\x01\tv\x01\x0f\x02\x00\xc3\x0f\xa3\x07\x02\x0f\x02\x00\n\x0fF\x01\x18\x0fB\x01\xd2\x00\x02\x00\x0fF\x01I\x0fE\x01\xd6\x0f\xe9\x08\x07\x0f\x02\x00\x06\x0f\x8c\x02\x17\n*\x00\x0f\x02\x00\xc9\x0f\x8c\x02J\x0f9\x01\xc9\t\x02\x00\x0fF\x01\xff\xff\xff\xf5\t5\x06\x0f0\n\t\t)\x00\x0f\x02\x00\xca\x0f\x18\x05 \x18\xf11L\x0fF\x01\xf4\x0f\x02\x0e\x11\t\x02\x00\x0fF\x01\xff\x02\x0f1\n\x1f\x00\x12=\x06\x9f\x03\x0f\x8c\x02\xf3\x0fF\x01#\x06\xd4\x03\x0fF\x01\xff\'\x00\x94\x1a\x05\x8d\x02\x0fF\x01\xf3\x0f\xd4\x11 \x00F\x01\x05H\x01\x0fF\x01\xf4\t:\x06\x0f\x02\x00\x11\x048\x01\x02\x8f\x02\x03k\x06\x00X\x01\r\x02\x00\x0f\xea\x08\xd8\x0f\xa4\x07\x1f\x03.\x01\x04F\x01\x00\x0f\x00\x0fG\x01\x03\x0fF\x01\xd7\x0f\x8d\x02\x1f\x028\x01\x00:\x01\x00\x02\x00\x00\x0e\x00\x00\t\x17\x00\x12\x00\x0c\x02\x00\x0fF\x01\xff\x0b\x009\x01\x00\x02\x00\x00E\x01\x00\x1c!\x01\xc9\\\x00\x11\x00\x0c\x02\x00\x0fF\x01\xff\x0c\x12\x08/\x01\x04F\x01\x00-\x01\x04Z\x01\t\x02\x00\x00\x19\x00\x0f\x02\x00\xd4\x0f\x1c!\x02\x0f\x02\x00\x08R\xf1\xf1\xf1\x08\x08-\x01\x00\x22\x01\x12\xf1\x8b\x02\x0c\x02T\x01\x02\x00\x0fF\x01\xd8\x0fj\x84\x05\x0f\x02\x00\x04\x01E\x01\x03G\x01\x03F\x01\x00\x07\x00\x0fF\x01\xee\x0f`\x06\x1a\x00\xd5\x1b\x00F\x01\x10\x08m\x02\x00?\x01\x0f\xea\x08\xf3\x00F\x01\x0f\xd8\x11\x17\x03\x8a\x02\x00\x02\x00\x01G\x01\x1f\xf1F\x01\xf7\x0fG\x01\x17\x05\x8a\x02\x00\x02\x00\x00G\x01\x00\x04T\x00\xfe\x04\x00\x0c\x00\x0e\x02\x00\x00\x1a\x00\x0f\x02\x00\xd8\x0fb\x06\x14\x00\xe6N\x00@\x01\x03\x02\x00\x007\x01\x00X\x01\x00K\x01\x00\x0c\x00\x05\x02\x00\x01\x13\x00\x00\x02\x00\x0fC\x01\xd8\x00\x02\x00\x00\xf3\x00\x03\x02\x00\x0fV\x06\x04\x01\x8f\'\x00)\x00\x03C\x01\x00\x02\x00\x00\xfb.\x00\xd4\x03\x1c\x0cF\x01\x00S\x00\x0f\x02\x00\xea\x03L\x01\x0f\x02\x00\x02\x00\x19\x01\x10\xf1?\x01\x04\x02\x00\x05~\x02\n\x02\x00\x0f\xca\x03\xdc\x0f\x02\x00 \tF\x01\x1a\x08>\x01\x04\x02\x00\x0fF\x01\xff\x1e\x0fG\x01\x03\x0fF\x01\xff\x1f\x0fG\x01\x02\x0fF\x01\xff \x0fG\x01\x01\x0fF\x01\xff!\x0f\x02\x00\x00\x0fF\x01\xff4\x0f\xb5\x06 \x0f\x02\x00\xda\x07\x02\x0e\x0f\x02\x00\x08\x0f\x13\x01\xda\x0f\x02\x00\x19\x014\x01\x03\x07\x00\x0f\x02\x00\x0f\x02[\n\x0f\x02\x00\xff\x00\x0f:\x01\x0f\t\x02\x00\x0f\x1a\x05\xff\x04\x04Im\t+\x01\x03\x02\x00\n\x88\x0b\x02\x02\x00\x0fF\x01\xff\x04\x02\x02\x00\x0fF\x01\x01\x0f*\x05\x03\x0fF\x01\xff\x0b\x02i\x02\t\x02\x00\x00\xa6\x02\x19\xf3\x12\x00\x00\x02\x00\x00\xa5>\x02z\x01\x0f\x02\x00\xff\x01\x00!\x01\n\x02\x00\x01H\x06\x0f\xd4\x03\xff\x1c\x0f.\x01\x00\x01k\x02\x0f\x18\x00\x00\x1f\x08\x8c\x02\xff\x07\x0f\xba\x03\x00\x02\x00\x1c\x0fF\x01\xff\x1c\n\xcd\x03\x00\x02\x00\x01\x8b\x02\x0f\x19\x00\x01\x0f\x8c\x02\xff\t\x008\x01\t\x02\x00\x02E\x01\x0f\x19\x00\x00\x00v\x06\x03\x1d\x00\x0f\x02\x00\xfd\x0e\xb9\x03\x03\x22\x01\x0e\x19\x00\x0fF\x01\xff\x1a\x03E\x01\x0f\x8c\x02\xff\x1d\x00\xa6\x03C\xf1\xf3\x08\xf3\xb0\x0c\x01\xe6\x08\x00\x02\x00\x0f\x8c\x02\xff\x1b\x00a\'\x0f\x02\x00\x02\x0e\xbc\x07\x00c\x01\x0f\x02\x00\x04\x00w\x01\x0f\x02\x00\xea\x0ft\x02\x01\x0f\x02\x00\x1d\x00\xd0\x02\x0f\x02\x00\xeb\x0fF\x010\x0f\x8c\x02\xed\x00\xa1\x03\x0fy\x02\x1d\x0e\x02\x00\x0f\x8b\x02\xed\x0f\x89\x020\x0f\x8d\x0b\xf0\x0fF\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfft\x00\x04\x12\x02\x02\x00\x00\x1d\x17\x04\x02\x00\x0f\xd4\x11\xff\x1e\x050\x01\x02K\x01\x04\x02\x00\x0f\xa2\x15\xeb\x0f\xa3\x1a\x02\x0f\x02\x00\t\x05F\x01\x0f\x02\x00\xfa\x0f\x1a\x13\x1d\x0fF\x01\xff\xffu\x03\x03\x05\x0f\xca\x03\xfa\x04\x02\x00\x0f\xd2\x03\x17\x0f\xcc\x03\xff\x04\x02\x02\x00\x00b\x02\x0fN\x06\t\x05\x02\x00\x02/\x00\x0f\x02\x00\xff\x08\x10\xf1\x15!\x0f\x94\x02\x0e\x0f@\x01\xff\x08\x02\x02\x00\x10\xf1\xb1(\x0fF\x01\xff2\x1f\xf18\n\x0f\x02\x1a*\x0f\x02\x00\xff\x08\x00\xd2\x03\x0fF\x01\x0f\x1f\x08A\x01\xff\x08\x01\x02\x00\x00\xcd\x03\x00\x04\x00\x0f\x02\x00\x0c\x01,\x00\x0f\x02\x00\xff\x08/\xf1\x08\xa7\x07\x12\x0fA\x01\xff\x08\x01\x02\x00\x05\x88\x02\x0f\xaa\x07\x0b\x00\x14\t\x0f4\n\xff\t\x00F\x01\x01\x8e\x02\x0f\x95\x02\x0f\x0fF\x01\xff\x0f\x10\xf1c\x06\x01M\x01\x0f\x02\x00\x08\x0fF\x01\xff\x0c\x10\xf3\xeb\x08\x00E\x01\x00\x98\x02\x0f\x02\x00\x08\x0fF\x01\xff\n\x01\xf0\x04\x0f\x87\x02\r\x00\xf6\x03\x0f\x8c\x10\xff\x05\x07\x02\x00\x0fF\x01\x0e\x0fw\x0b\xff\x0e\x02\x02\x00\x01m\x02\x00t\x02\x0f\x02\x00\x04\x0f\xce\x03\xff\t\x06\x02\x00\x03\xc2\x0c\x0f\x19\x05\x06\x0f\xce\x03\xff\x10\x00\x02\x00\x00\xe7\x08\x02F\x01\x0f_9\x00\x0fE\x01\xff\x16\x00I\x0f\x00?\x06\x00M\x01\x0f\x90\x02\x01\x0f\xd0\x03\xff\x13\x00\x17\x05\x01\x02\x00\x0fF\x01\x05\x00#\x00\x0f\x02\x00\xff\x11\x06\x81\x02\r\xd2\x03\x00\x855\x0fB\x01\xff\x11\x00\x02\x00\x06F\x01\x00\xdd\x03\x07\x02\x00\x02\xb9\x07\x00#\x00\x0f\x02\x00\xff\x11\x00\xa4\x07\x01\x19\x05\x05\x02\x00\x00\xc82\x01\r\x00\x00S\x01\x0fB\x01\xff\x11\x00\x02\x00\x00-\x01\x01\xbaD\x04\xd3\x08\x01A\x01\x04\x1a\x00\x0f\xa4\x15\xff\x0e\x04\x02\x00\x06\xd2\x03\x00?\x01\x00E\x01\x04\x1a\x00\x01\xe2\x03\x05\r\x00\x0f\x02\x00\xff\x0c\x06F\x01\x03\x02\x00\x06\xdc\x08\x00\x1b\x00\x0f=\x01\xff\x0c\x05\x02\x00\x00+\x01\t\x02\x00\x05F\x01\x01\x1a\x00\x05(\x00\x0f\x02\x00\xff\x0c\x01,\x01\x08\x02\x00\x05F\x01\x00\xe9\x08\x0f\x18\x05\xff\x19\x01/\x01\x04\x02\x00\x07\xc3\x11\x01\xad\x07\x0f\x84\x02\xff\x0c\x04\x02\x00\x00T\x06\t\x02\x00\x04\x19\x00\x02\x1b\x00\x00\x08\x00\x0f\x02\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf7a\x01\x04\x00\x01\x00\x00\x04\x00P\x00\x00\x01\x01\xff\x07\x00\x04\x02\x00d\x05room1\x0e\x00\x04\x02\x00\x1f\x02/\x00\n\x142\'\x00\x04\x02\x00\x1f\x03/\x00\n\x143\'\x00\x04\x02\x00\x1f\x04/\x00\n\x144\'\x00P\x00\x00\x00\x00\x00"
#
#header = decode_header_v1(customdata.hex()[0:48])
#mapArea = header['width'] * header['height']
#infoLength = 48 + header['totalcount'] * 2
#encodeDataArray = bytes(_hexStringToNumber(customdata.hex()[48:infoLength]))
#raw = uncompress(encodeDataArray)
#mapDataArr = raw[0:mapArea]
#mapRoomArr = raw[mapArea:]
#print(decode_roomArr(mapRoomArr))