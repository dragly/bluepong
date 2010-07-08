#TODO:
# Add scoreboard
# Make how you hit the ball affect the direction
# Put everything into neat classes and functions


import sys, pygame
import bluetooth
pygame.init()
from pygame.locals import *

size = width, height = 800, 400
speed = [0.3, 0.3]
black = 0, 0, 0

screen = pygame.display.set_mode(size)
pygame.display.set_caption('Bluepong')

NONE, CLIENT, SERVER, REJOIN = range(4)

# select host or join
font = pygame.font.SysFont("Arial", 36)
waittext = font.render("Please Wait", 1, (150, 150, 10))
clienttext = font.render("Join Game", 1, (150, 150, 10))
clienttextpos = clienttext.get_rect()
clienttextpos.left = 10
clienttextpos.top = 10
servertext = font.render("Host Game", 1, (150, 150, 10))
servertextpos = servertext.get_rect()
servertextpos.left = 10
servertextpos.top = clienttextpos.top + clienttextpos.height
rejointext = font.render("Rejoin Game", 1, (150, 150, 10))
rejointextpos = servertext.get_rect()
rejointextpos.left = 10
rejointextpos.top = servertextpos.top + servertextpos.height
filename = "bluepong.last"
selected = NONE
while selected == NONE:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            mpos = pygame.mouse.get_pos()
            if mpos[0] > clienttextpos.left and mpos[0] < clienttextpos.right and mpos[1] > clienttextpos.top and mpos[1] < clienttextpos.bottom:
                selected = CLIENT
            if mpos[0] > servertextpos.left and mpos[0] < servertextpos.right and mpos[1] > servertextpos.top and mpos[1] < servertextpos.bottom:
                selected = SERVER
            if mpos[0] > rejointextpos.left and mpos[0] < rejointextpos.right and mpos[1] > rejointextpos.top and mpos[1] < rejointextpos.bottom:
                selected = REJOIN
        if event.type == KEYUP:
            if event.key == K_q:
                sys.exit()
                
    screen.fill(black)
    if selected == NONE:
        screen.blit(clienttext, clienttextpos)
        screen.blit(servertext, servertextpos)
        screen.blit(rejointext, rejointextpos)
    else:
        screen.blit(waittext, clienttextpos)
    pygame.display.flip()

print selected

if selected == SERVER:
    server_sock=bluetooth.BluetoothSocket( bluetooth.L2CAP )

    port = 0x1645
    server_sock.bind(("",port))
    server_sock.listen(1)

    client_sock,address = server_sock.accept()
    print "Accepted connection from ",address

    #data = client_sock.recv(1024)
    #print "received [%s]" % data

elif selected == CLIENT:
    nearby_devices = bluetooth.discover_devices()

    devicelisttext = []
    devicelistpos = []
    devicelistaddr = []
    posx = 10
    posy = 10
    for bdaddr in nearby_devices:
        name = bluetooth.lookup_name( bdaddr )
        print name
        devicetext = font.render(name, 1, (150, 150, 10))
        devicetextpos = devicetext.get_rect()
        devicetextpos.left = posx
        devicetextpos.top = posy
        posy = posy + devicetextpos.height
        
        devicelisttext.append(devicetext)
        devicelistpos.append(devicetextpos)
        devicelistaddr.append(bdaddr)
    address = ""
    while address == "":
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mpos = pygame.mouse.get_pos()
                i = 0
                for devicetextpos in devicelistpos:
                    if mpos[0] > devicetextpos.left and mpos[0] < devicetextpos.right and mpos[1] > devicetextpos.top and mpos[1] < devicetextpos.bottom:
                        address = devicelistaddr[i]
                    i = i + 1
            if event.type == KEYUP:
                if event.key == K_q:
                    sys.exit()
                    
        screen.fill(black)
        for i in range(len(devicelistpos)):
            screen.blit(devicelisttext[i], devicelistpos[i])
        pygame.display.flip()
    f = open(filename, 'w')
    f.write(address)
    f.close()
    sock=bluetooth.BluetoothSocket(bluetooth.L2CAP)
    port = 0x1645
    sock.connect((address, port))
    
elif selected == REJOIN:
    f = open(filename, "r")
    address = f.read()
    f.close()

    sock=bluetooth.BluetoothSocket(bluetooth.L2CAP)
    port = 0x1645
    sock.connect((address, port))
    selected = CLIENT # change to client, since this is essentially what we are from now on
    


#pygame.mouse.set_visible(False)
ball = pygame.image.load("ball.png")
ballrect = ball.get_rect()
ballrect.centerx = screen.get_rect().centerx
ballrect.centery = screen.get_rect().centery
prevtime = pygame.time.get_ticks()

serverrect = Rect(50, 0, 30, 75)
clientrect = Rect(width - 50, 0, 30, 75)

fpos = [float(ballrect.width), float(ballrect.height)]

while 1:
    curtime = pygame.time.get_ticks()
    dt = curtime - prevtime
    speed[0] = speed[0] * (1 + 0.00001 * dt) # increase the speed with just a tad each time
    speed[1] = speed[1] * (1 + 0.00001 * dt)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()
        if event.type == pygame.MOUSEMOTION:
            mpos = pygame.mouse.get_pos()
            if selected == SERVER:
                serverrect.centery = mpos[1]
            elif selected == CLIENT:
                clientrect.centery = mpos[1]
        if event.type == KEYUP:
            if event.key == K_q:
                sys.exit()
                if selected == SERVER:
                    client_sock.close()
                    server_sock.close()
                elif selected == CLIENT:
                    sock.close()
    if selected == SERVER:
        # wait for data from the client
        data = client_sock.recv(1024)
        sdata = data.split(",")
        if sdata[0] == "cpos": # client position
            clientrect.centery = int(sdata[1])
        # do calculations
        fpos[0] = fpos[0] + speed[0] * dt
        fpos[1] = fpos[1] + speed[1] * dt
        ballrect.centerx, ballrect.centery = fpos
        if fpos[0] - ballrect.width / 2 < 0: # left edge outside
            speed[0] = -speed[0]
            fpos[0] = screen.get_rect().centerx
            fpos[1] = screen.get_rect().centery
            print "point to server"
        if fpos[0] + ballrect.width / 2 > width:
            speed[0] = -speed[0]
            fpos[0] = screen.get_rect().centerx
            fpos[1] = screen.get_rect().centery
            print "point to client"
        if fpos[1] - ballrect.height / 2 < 0:
            speed[1] = -speed[1]
            fpos[1] = ballrect.height / 2
        if fpos[1] + ballrect.height / 2 > height:
            speed[1] = -speed[1]
            fpos[1] = height - ballrect.height / 2
        if ballrect.colliderect(clientrect): # if it collides with the rectangels
            speed[0] = -speed[0]
            fpos[0] = clientrect.left - ballrect.width / 2
        if ballrect.colliderect(serverrect):
            speed[0] = -speed[0]
            fpos[0] = serverrect.right + ballrect.width / 2
        # send back some data
        client_sock.send("spos," + str(serverrect.centery))
        client_sock.send("bpos," + str(ballrect.centerx) + "," + str(ballrect.centery))
    elif selected == CLIENT:
        # send the server some data
        sock.send("cpos," + str(clientrect.centery))
        # recieve some data
        data = sock.recv(1024)
        sdata = data.split(",")
        if sdata[0] == "spos": # server position
            serverrect.centery = int(sdata[1])
        data = sock.recv(1024)
        sdata = data.split(",")
        if sdata[0] == "bpos": # ball position
            ballrect.centerx = int(sdata[1])
            ballrect.centery = int(sdata[2])

    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.draw.rect(screen, (255, 255, 255), serverrect)
    pygame.draw.rect(screen, (255, 255, 255), clientrect)
    pygame.display.flip()
    prevtime = curtime
