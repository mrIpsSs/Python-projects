import socket
import random

ip = "0.0.0.0"
port = 5433

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((ip, port))

players = {}

censure = [
    "fuck",
    "shit",
    "bitch",
    "asshole",
    "bastard",
    "dick",
    "pussy",
    "cunt",
    "slut",
    "whore",
    "faggot",
    "retard",
    "nigger",
    "kill yourself",
    "kys",
    "nigga",
    
]

print("UDP server running...")

def UpdatedGlobalPositions():
    positions_string = ""

    for p in players.values():
        positions_string += f"{p['PosX']} {p['PosY']} {p['R']} {p['G']} {p['B']} {p['Username']};"

    for client_addr in players.keys():
        server.sendto(positions_string.encode(), client_addr)

while True:
    data, addr = server.recvfrom(1024)
    msg = data.decode()

    if addr not in players:
        players[addr] = {
            "PosX": round(random.randint(50, 700) / 5) * 5, 
            "PosY": round(random.randint(50, 700) /5 ) * 5,
            "R": random.randint(1, 225), 
            "G": random.randint(1, 255), 
            "B": random.randint(1, 225),
            "Username": ""
            }
        
        print("Player joined:", addr)

    if msg == "hello":
        UpdatedGlobalPositions()

    if msg.startswith("set_username;"):
        players[addr]["Username"] = msg.split(";")[1] #

    elif msg == "disconnect":
        if addr in players:
            del players[addr]

            print("Player left:", addr)

            UpdatedGlobalPositions()
        continue

    elif msg == "up":
        players[addr]["PosY"] -= 5

    elif msg == "down":
        players[addr]["PosY"] += 5

    elif msg == "right":
        players[addr]["PosX"] += 5

    elif msg == "left":
        players[addr]["PosX"] -= 5
    elif msg == "color":
        players[addr]["R"] = random.randint(1, 225)
        players[addr]["G"] = random.randint(1, 225)
        players[addr]["B"] = random.randint(1, 225)

    elif msg.startswith("chatmsg;"):
        text = msg.split(";")[2].lower()
        text2 = msg.split(";")[2]
        for i in censure:
            text = text.replace(i, "#" * len(i))

        finalmessage = ""

        for i in range(len(text)):
            if text[i] == text2[i].lower():
                finalmessage += text2[i]
            else:
                finalmessage += "#"

        chatmsg = "chatmsg;" + msg.split(";")[1] + ";" + finalmessage
        print(chatmsg)

        for client_addr in players.keys():
            server.sendto(str(chatmsg).encode(), client_addr)

    UpdatedGlobalPositions()