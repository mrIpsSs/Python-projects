import pygame
import socket
import threading
import time

username = input("Enter ur username: ")

HostIP = "87.2.53.188"
port = 5000

PLAYER_COLOR = (83, 79, 89)
PLAYER_SIZE = 50

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

positions = []
running = True

chatHistory = [
]

client.sendto(b"hello", (HostIP, port))

client.sendto(("set_username;" + username).encode(), (HostIP, port))

def sendMoveRequest(direction):
    if direction == 0:
        client.sendto(b"up", (HostIP, port))

    elif direction == 1:
        client.sendto(b"down", (HostIP, port))

    elif direction == 2:
        client.sendto(b"right", (HostIP, port))

    elif direction == 3:
        client.sendto(b"left", (HostIP, port))
        
    elif direction == 4:
        client.sendto(b"color", (HostIP, port))

def receivePositions():
    global positions, running
    while running:
        try:
            data, _ = client.recvfrom(1024)
            decoded = data.decode().strip()
            if decoded.startswith("chatmsg;"):
                _, usrname, text = decoded.split(";")
                s = usrname + ": " + text
                while len(s) > 40:
                    chatHistory.append(s[:40])
                    s = s[40:]
                chatHistory.append(s)
            else:
                parts = decoded.split(";")

                new_positions = []
                for p in parts:
                    if p:
                        x, y, r, g, b, name = p.split(" ")
                        new_positions.append([int(x), int(y), int(r), int(g), int(b), name])

                positions = new_positions
        except Exception as e:
            print("Receive error:", e)

threading.Thread(target=receivePositions, daemon=True).start()

WIDTH, HEIGHT = 800, 800

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

font = pygame.font.Font(None, 24)

typing = False

chatBG = pygame.surface.Surface((WIDTH / 2, HEIGHT / 4))
chatBG.fill((0, 0, 0))
chatBG.set_alpha(50)

typingBG = pygame.surface.Surface((WIDTH / 2, 50))
typingBG.fill((100, 100, 100))
typingBG.set_alpha(50)
typedText = ""

def RenderChat():
    global chatHistory
    screen.blit(chatBG, (10, HEIGHT - chatBG.get_height() - 10 - 70))
    while len(chatHistory) * 24 - chatBG.get_height() > -20:
        chatHistory = chatHistory[1:]

    for x, line in enumerate(chatHistory):
        lineText = font.render(line, True, (255, 255, 255))
        y = x * 24 + HEIGHT - chatBG.get_height()
        screen.blit(lineText, (20, y - 50)) 

    screen.blit(typingBG, (10, HEIGHT - typingBG.get_height() - 20))
    typedTextSrf = font.render("> " + typedText + ("_" if int(time.time() * 2) % 2 == 0 and typing else ""), True, (255, 255, 255))
    screen.blit(typedTextSrf, (15, HEIGHT - typingBG.get_height() - 15))


showChat = True

ctrlcp = False
ctrlcp2 = False
ctrlcplf = False

lastMsgSent = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.unicode == "/":
                typing = not typing
                break

            if typing:
                if event.key == pygame.K_RETURN:
                    if not len(typedText.strip()) < 1 and time.time() - lastMsgSent > 1:
                        client.sendto(("chatmsg;" + username + ";" + typedText).encode(), (HostIP, port))
                        typedText = ""
                        typing = False
                        lastMsgSent = time.time()

                elif event.key == pygame.K_BACKSPACE:
                    typedText = typedText[:-1]

                else:
                    typedText += event.unicode

            else:
                if event.key == pygame.K_z:
                    sendMoveRequest(4)

    keys = pygame.key.get_pressed()

    ctrlcp2 = ctrlcp
    ctrlcp = keys[pygame.K_t] and keys[pygame.K_LCTRL]
    ctrlcplf = ctrlcp and not ctrlcp2

    if ctrlcplf:
        showChat = not showChat
        typedText = ""

    if not typing:
        if keys[pygame.K_w]:
            sendMoveRequest(0)
        if keys[pygame.K_s]:
            sendMoveRequest(1)
        if keys[pygame.K_d]:
            sendMoveRequest(2)
        if keys[pygame.K_a]:
            sendMoveRequest(3)

    screen.fill((25, 25, 25))
    for pos in positions:
        pygame.draw.rect(
            screen,
            (pos[2], pos[3], pos[4]),
            (pos[0], pos[1], PLAYER_SIZE, PLAYER_SIZE)
        )
        usernameSurface = font.render(pos[5], True, (255, 255, 255))
        screen.blit(usernameSurface, ( 
            pos[0] + PLAYER_SIZE / 2 - usernameSurface.get_width() / 2,
            pos[1] - usernameSurface.get_height() - 15
        ))
    
    if showChat:
        RenderChat()
    else:
        typing = False

    pygame.display.update()
    clock.tick(60)

client.sendto(b"disconnect", (HostIP, port))
pygame.quit()