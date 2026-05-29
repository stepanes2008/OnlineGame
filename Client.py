import socket
import threading
import pygame

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 8001))

pygame.init()
w, h = 600, 600
screen = pygame.display.set_mode((w, h))
dt = ['', '', '', '', '', '', '', '', '']
def receive():
    while True:
        try:
            msg = client.recv(1024).decode()
            dt = msg.split(';')

            if msg == "Your turn":
                move = input("Выберите клетку (0-8) ")
                client.send(move.encode())

        except:
            print('Сервер отключён')
            break

def draw():
    while True:
        screen.fill((255, 255, 255))
        pygame.draw.line(screen, (0, 0, 0), (0, 200), (600, 200))
        pygame.draw.line(screen, (0, 0, 0), (0, 200), (600, 200))
        pygame.draw.line(screen, (0, 0, 0), (0, 200), (600, 200))
        pygame.draw.line(screen, (0, 0, 0), (0, 200), (600, 200))

thread = threading.Thread(target=receive)
thread2 = threading.Thread(target=draw)
thread.start()
thread2.start()