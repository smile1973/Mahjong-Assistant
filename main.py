from selenium import webdriver
import copy
import time
from selenium.webdriver.chrome.options import Options
Path="./chromedriver.exe"
# 使用Chrome作為WebDriver
options = webdriver.ChromeOptions()
# options.add_argument('--proxy-server=http://127.0.0.1:8888')
options.add_argument('--ignore-certificate-errors')
options.add_argument('headless')
driver = webdriver.Chrome(Path, chrome_options=options)
total = {'m':[4,4,4,4,4,4,4,4,4], 'p':[4,4,4,4,4,4,4,4,4], 's':[4,4,4,4,4,4,4,4,4], 'z':[4,4,4,4,4,4,4]}
hand = {'m':[], 'p':[], 's':[], 'z':[]}
set = []
stable=1

def analyzee(cards,set,s): 

    target = dicTransformStr(cards)
    content,lis = webCrawler(target,s)
    content = strTransformDic(content)
    result = compare(content,set)
    display(lis,content, result) 

def webCrawler(cards,s):
    if s:
        url = "https://tenhou.net/2/?q=%s"%cards
    else:
        url = "https://tenhou.net/2/?p=%s"%cards
        
    driver.get(url)
    content = driver.find_element_by_tag_name("textarea").text
    lis = driver.find_element_by_id("tehai").text
    lis = lis.split('(')[0]
    lis = lis.split(' ')[0]
    return content,lis

def strTransformDic(content):
    Content = {}
    l = content.split()[1:]
    for i in range(0,len(l),3):
        waits = {'m':[], 'p':[], 's':[], 'z':[]}
        while(len(l[i+1]) != 0):
            if(l[i+1][0].isdigit()):
                waits[l[i+1][1]].append(l[i+1][0])
                l[i+1] = l[i+1][2:]
            else:    
                l[i+1] = l[i+1][1:]    
        Content[l[i][1:3]] = waits            
    return Content  

def compare(content,set):
    dic = {'z':4, 'm': 3, 'p':2, 's':1}
    compare = []
    for i in content:
        num = int(i[0])
        type = i[1]
        if hand[type].count(num) > set.count(i):
            probability = calculate(content[i])
            compare.append([i,probability])
    # print(compare[0][0][1])                
    compare.sort(key= lambda x: (x[1],dic[x[0][1]]), reverse=True)
    return compare

def calculate(waits):
    probability = 0
    remain = sum(total['m']+total['p']+total['s']+total['z'])
    for i in waits:
        l = waits[i]
        for j in l:
            if(total[i][int(j)-1] == 0):
                waits[i].remove(j)
            else:    
                probability += total[i][int(j)-1]/remain             
    return probability

def dicTransformStr(cards):
    str = ""
    for i in cards:
        for j in cards[i]:
            str += chr(int(j)+48)
        if(len(cards[i])!=0):
            str += i
    return str                  

def display(lis,content, result):
    if(lis[:3] == "標準形"):
        lis = lis[3:]
    # print(lis)    
    if(lis == "和了"):
        print("和牌")   
    else:
        if(lis == "標準形聴牌"):
            lis = "聽牌"
        print(lis)    
        for l in result:
            probability = round(l[1]*100,3)
            waits = dicTransformStr(content[l[0]])
            print("打",l[0],"摸",waits,f"進牌機率: {probability}%")
        print("==========")    


def reset():
    
    for i in hand:
        hand[i] = []  
    total['m'] = [4,4,4,4,4,4,4,4,4]
    total['p'] = [4,4,4,4,4,4,4,4,4]
    total['s'] = [4,4,4,4,4,4,4,4,4]
    total['z'] = [4,4,4,4,4,4,4]
    set.clear()     

def getHand(n):   
    reset() 
    str = ''.join(n)
    cards = []
    for i in str:
        if(i.isdigit()):
            cards.append(int(i))
        else:
            hand[i] += cards
            for j in cards: 
                total[i][j-1] -= 1
            cards = []                   

def run(order, card,s):
    if(order == 0):    #摸牌
        drawCard(card)
        analyzee(hand,set,s)
    elif(order == 1):  #打牌
        playCard(0,card)    
    elif(order == 2):  #對手打牌
        playCard(1,card)
    elif(order == 3):  #可碰牌
        pongAnalyze(card,s)
    elif(order == 4):  #碰牌
        num = int(card[0])
        type = card[1]
        for _ in range(3): 
            set.append(card)
        hand[type].append(num)
    elif(order == 5):  #別家碰牌
        num = int(card[0])
        type = card[1]
        total[type][num-1] -= 2
    elif(order == 6):  #可吃牌
        eatAnalyze(card,s)
    elif(order == 7): #吃牌(list:進牌，吃的第一張)
        num = int(card[1][0])
        type = card[1][1]  
        for i in range(3):
            set.append(chr(num+i+48)+type)
        num = int(card[0][0])
        type = card[0][1]
        hand[type].append(num)     
    elif(order == 8):  #別家吃牌
        num = int(card[1][0])
        type = card[1][1]
        for i in range(3):
            total[type][num+i-1] -= 1
    elif(order == 9): #暗槓
        num = int(card[0])
        type = card[1]
        total[type][num-1] = 0
        for _ in range(4): 
            set.append(card)
        playCard(0,card)
    elif(order == 10): #槓
        num = int(card[0])
        type = card[1]
        total[type][num-1] = 0
        for _ in range(4): 
            set.append(card)
    elif(order == 11): #別人槓:
        num = int(card[0])
        type = card[1]
        total[type][num-1] = 0       
    elif(order == 12): #開寶牌
        num = int(card[0])
        type = card[1]
        total[type][num-1] -= 1

def drawCard(card):
    num = int(card[0])
    type = card[1]
    hand[type].append(num)
    if(num == 0): 
        total[type][4] -= 1
    else:
        total[type][num-1] -= 1

def playCard(player,card):
    num = int(card[0])
    type = card[1]
    if(player == 0):
        hand[type].remove(num)   
    else:
        total[type][num-1] -= 1    

def pongAnalyze(card,s):
    num = int(card[0])
    type = card[1]
    hand_tmp = copy.deepcopy(hand)
    hand_tmp[type].append(num)
    set_tmp = copy.deepcopy(set)
    set_tmp.append(card)
    set_tmp.append(card)
    set_tmp.append(card)
    analyzee(hand_tmp,set_tmp,s)

def eatAnalyze(card,s):
    num = int(card[0])
    type = card[1]
    tmp = copy.deepcopy(hand)
    for i in set:
        # print(tmp[i[1]])
        # print(int(i[0]))
        try:
            tmp[i[1]].remove(int(i[0]))
        except:
            continue    
    tmp[type].append(num)    
    if(all(element in tmp[type] for element in [num-2, num-1, num])):
        print("吃",num-2,num-1,num)    
        hand_tmp = copy.deepcopy(hand)
        hand_tmp[type].append(num)
        set_tmp = copy.deepcopy(set)
        set_tmp.append(chr(num-2+48)+type)
        set_tmp.append(chr(num-1+48)+type)
        set_tmp.append(chr(num+48)+type)
        analyzee(hand_tmp,set_tmp,s)
    if(all(element in tmp[type] for element in [num-1, num, num+1])):
        print("吃",num-1,num,num+1)    
        hand_tmp = copy.deepcopy(hand)
        hand_tmp[type].append(num)
        set_tmp = copy.deepcopy(set)
        set_tmp.append(chr(num-1+48)+type)
        set_tmp.append(chr(num+48)+type)
        set_tmp.append(chr(num+1+48)+type)
        analyzee(hand_tmp,set_tmp,s)
    if(all(element in tmp[type] for element in [num, num+1, num+2])):
        print("吃",num,num+1,num+2)    
        hand_tmp = copy.deepcopy(hand)
        hand_tmp[type].append(num)
        set_tmp = copy.deepcopy(set)
        set_tmp.append(chr(num+48)+type)
        set_tmp.append(chr(num+1+48)+type)
        set_tmp.append(chr(num+2)+type)
        analyzee(hand_tmp,set_tmp,s)        



import mitmproxy.http
import analyze
from proto import liqi_pb2 as liqi
analyze_protobuf = analyze.Analyze_proto()

class WebSocketAddon:
    def __init__(self):
        self.seat = -1
        self.check = False
        self.precard = None
        self.stable=1
    def websocket_message(self, flow: mitmproxy.http.HTTPFlow):
        # client_ip = flow.client_conn.address[0]
        # print(f"Client IP: {client_ip}")

        # # 檢查 server 的 IP 地址
        # server_ip = flow.server_conn.address[0]
        # print(f"Server IP: {server_ip}")
        # WebSocket 觸發
        assert flow.websocket is not None
        message = flow.websocket.messages[-1]
        # 解析proto消息
        pr = analyze_protobuf.analyze(message) #pr = proto_result 
        if pr != None and 'name' in pr.keys():
            # print(pr)
            result = {}
            action_type = pr['name']
            # pai:起始手牌 | doras:起始寶牌
            if action_type == "ActionNewRound": # 開始新一輪
                result = {"action" : "new_round", "pai" : pr['data']['tiles'], 
                          "doras" : pr['data']["doras"]}
            
            # 有東西代表是發給玩家的
            # seat:場風 0~3=東南西北 這裡的seat就是玩家所在位子
            # doras:寶牌 可能為空 / 槓(ActionAnGangAddGang)後會有內容更新
            # left_pai:海底還有幾張牌 | can_do:可以做什麼動作 pon碰 / gang槓 / liqi立直 / babei拔北
            elif action_type == "ActionDealTile": # 發牌
                if 'operation' in pr['data']:   
                    result = {"action" : "fa_pai", "seat" : pr['data']['seat'],
                              "pai" : pr['data']['tile'], "doras" : pr['data']['doras'],
                              "left_pai" : pr['data']['left_tile_count']}
                    can_do = operation_type(pr['data']['operation']['operation_list'])
                    result['player_can_do'] = can_do           
                else:
                    result = {"action" : "fa_pai", "seat" : pr['data']['seat'],
                              "doras" : pr['data']['doras'], "left_pai" : pr['data']['left_tile_count']}
            
            elif action_type == "ActionDiscardTile": # 丟牌
                result = {"action" : "discard_pai", "seat" : pr['data']['seat'],
                          "pai" : pr['data']['tile']}
                if 'operation' in pr['data']: # 代表玩家有可以做的動作
                    can_do = operation_type(pr['data']['operation']['operation_list'])
                    result["player_can_do"] = can_do
                
            elif action_type == "ActionAnGangAddGang": # 槓 | 槓後會有進牌
                result = {"action" : "gang", "seat" : pr['data']['seat'], "pai" : pr["data"]['tiles']}
            
            elif action_type == "ActionChiPengGang": # 吃 碰 | 吃碰後要丟牌 EX pai = ['4z', '4z', '4z']
                result = {"action" : "chi_pon", "seat" : pr['data']['seat'], "pai" : pr['data']['tiles']}
            
            if result:
                huma=0
                action=result['action']
                # print("result", result)
                if 'pai' in result:
                    if isinstance(result['pai'], list):
                        for i ,x in enumerate(result['pai']):
                            if int(x[0])==0:
                                result['pai'][i]='5'+x[1]
                    else:
                        if int(result['pai'][0])==0:
                            result['pai']='5'+result['pai'][1]

                if 'player_can_do' in result :
                    if 'hula' in result['player_can_do']:
                        huma=1
            #*************************************************************************
            #                      在這call function
            #*************************************************************************
                if action != 'chi_pon':
                    self.check = False
                if huma:
                    print("hula!")
                elif action=="new_round":
                    self.precard=None
                    self.seat=-1
                    if len(result['pai'])>13:
                        getHand(result['pai'][:13])
                        run(0, result['pai'][13],self.stable)
                        self.seat=0
                    else:
                        getHand(result['pai'])
                    run(12,result['doras'][0],self.stable)
                elif action=='discard_pai':
                    if result['seat']!=self.seat:
                        self.precard=result['pai']
                        run(2,result['pai'],self.stable)
                        if 'player_can_do' in result:
                            if result['player_can_do']:
                                if result['player_can_do'][0]=='chi':
                                    run(6,result['pai'],self.stable)
                                    self.check = True
                                elif result['player_can_do'][0]=='pong':
                                    run(3,result['pai'],self.stable)
                                    self.check = True
                    else:
                        run(1,result['pai'],self.stable)
                elif action=='fa_pai':
                    while result['doras']:
                        run(12,result['doras'].pop(),self.stable)
                    if 'pai' in result:
                        self.seat=result['seat']
                        run(0,result['pai'],self.stable)
                elif action=='chi_pon':
                    if result['seat' ]== self.seat or self.check:
                        self.stable=0
                        if result['pai'].count(result['pai'][0])==3:
                            run(4,result['pai'][0],self.stable)
                        elif result['pai'].count(result['pai'][0])==4:
                            run(10,result['pai'][0],self.stable)  
                        else:
                            l = sorted(result['pai'], key=lambda x:int(x[0]))
                            run(7,[self.precard, l[0]],self.stable)
                    else:        
                        if result['pai'].count(result['pai'][0])==3:
                            run(5,result['pai'][0],self.stable)
                        else:
                            l = sorted(result['pai'], key=lambda x:int(x[0]))
                            run(8,[self.precard,l[0]],self.stable)
                    self.check = False        
                elif action=='gang': 
                    if result['seat']!=self.seat and self.check == False:
                        run(10,result['pai'],self.stable)
                    else:
                        self.stable=0
                        run(9,result['pai'],self.stable)
                # print(hand)
                # print(total)
                # print(self.stable)
def operation_type(op_list):
    res = []
    for i in op_list:
        if i['type'] == 2: # 可以吃
            res.append("chi")
        elif i['type'] == 3: # 碰
            res.append("pong")
        elif i['type'] == 5: # 槓
            res.append("gang")
        elif i['type'] == 8 or i['type'] == 9: # 自摸 | 和
            res.append("hula")
    return res                  
            
addons = [
    WebSocketAddon()
]