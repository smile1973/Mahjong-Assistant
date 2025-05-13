from enum import Enum
from google.protobuf.json_format import MessageToDict
from proto import liqi_pb2 as liqi
import base64

class Msg_type(Enum):
    Notify = 1
    Req = 2
    Res = 3
    
class Analyze_proto:
    def __init__(self):
        pass 
    def analyze(self, msg):
        buffer = msg.content
        msg_type = Msg_type(buffer[0])
        
        # print(msg_type)
        if msg_type == Msg_type.Notify: #Notify
            msg_list = proto_separate(buffer[1:])
            # print("msg_block ----> ", msg_list)
            #原本型態為bytes, 轉換回來
            tmp = msg_list[0]['data'].decode("UTF-8")
            #拆分 .lq.ActionPrototype 等訊息, 並使用liqi.py的proto語法文件尋找對應message type
            method = tmp.split(".")[2]
            method_class = getattr(liqi, method)
            #從對應類別的定義將protobuf資料轉換
            result = method_class.FromString(msg_list[1]['data'])
            result_dict = MessageToDict(result, preserving_proto_field_name=True, including_default_value_fields=True)
            if 'data' in result_dict:
                B = base64.b64decode(result_dict['data'])
                action_class = getattr(liqi, result_dict['name'])
                action = action_class.FromString(decode(B))
                action_dict = MessageToDict(action, preserving_proto_field_name=True, including_default_value_fields=True)
                result_dict['data'] = action_dict
            return result_dict
        else:
            return None
            
def proto_separate(buffer):
    #雀魂資料格式 : 型式(message type) + 資料(bytes) ---> 拆分成兩部分, 從第一部分獲取message type, 來對第二部分資料進行轉換
    pos = 0
    result = []
    while(pos < len(buffer)):
        #第一組資料 -> Tag, 和 7 做 & 運算可得資料型態
        #Tag = field_num << 3 | wire_type
        proto_type = (buffer[pos] & 7)
        #回推三位 獲取資料field_num
        proto_num = buffer[pos] >> 3
        pos += 1
        if proto_type == 0: #varint
            data, pos = type_varint(buffer, pos)
        elif proto_type == 2: #string
            str_len, pos = type_string(buffer, pos)
            data = buffer[pos : pos + str_len]
            pos += str_len
        else:
            #unknow proto_type
            continue
        result.append({'id': proto_num, 'data': data})
    return result
    
def type_varint(buffer, pos):
    #取每組數據的後 7 位 -> &127可以拿到
    data = 0
    shift = 0
    while(pos < len(buffer)):
        #得到資料要反轉 -> 從底部開始放 -> 將指針右移 7 位
        data += (buffer[pos] & 127) << shift
        shift += 7
        pos += 1
        #每組資料首位決定後續是否仍有資料
        if buffer[pos-1] >> 7 == 0:
            break
    return data, pos

def type_string(buffer, pos):
    #獲取字串長度
    str_len = (buffer[pos] & 127)
    pos += 1
    #多做一次避免資料超出7bit大小
    if buffer[pos-1] >> 7 != 0:
        str_len += (buffer[pos] & 127) << 7
        pos += 1
    return str_len, pos

def decode(data: bytes):
    keys = [0x84, 0x5e, 0x4e, 0x42, 0x39, 0xa2, 0x1f, 0x60, 0x1c]
    data = bytearray(data)
    k = len(keys)
    d = len(data)
    for i, j in enumerate(data):
        u = (23 ^ d) + 5 * i + keys[i % k] & 255
        data[i] ^= u
    return bytes(data)