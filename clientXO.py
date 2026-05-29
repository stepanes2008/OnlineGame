import socket
import threading
import pygame

HOST = "127.0.0.1"
PORT = 8001

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

pygame.init()
w, h = 600, 700
screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("Крестики-нолики онлайн")

font_big = pygame.font.SysFont("arial", 120)
font_mid = pygame.font.SysFont("arial", 36)
font_small = pygame.font.SysFont("arial", 28)

board = [" "] * 9
my_symbol = ""
status_text = "Подключение..."
my_turn = False
running = True
lock = threading.Lock()


def send_line(text):
    client.sendall((text + "\n").encode())


def receive():
    global board, my_symbol, status_text, my_turn, running

    buffer = ""

    while running:
        try:
            data = client.recv(1024).decode()
            if not data:
                status_text = "Сервер отключён"
                running = False
                break

            buffer += data

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                if not line:
                    continue

                parts = line.split(";")

                if parts[0] == "INFO":
                    status_text = ";".join(parts[1:])

                    if "Ты играешь за" in status_text:
                        my_symbol = status_text.split()[-1]

                elif parts[0] == "BOARD":
                    with lock:
                        board = parts[1:10]

                elif parts[0] == "YOUR_TURN":
                    my_turn = True
                    status_text = "Твой ход"

                elif parts[0] == "END":
                    my_turn = False
                    status_text = ";".join(parts[1:])

        except:
            status_text = "Сервер отключён"
            running = False
            break


def draw_board():
    screen.fill((255, 255, 255))

    status_surface = font_small.render(status_text, True, (20, 20, 20))
    screen.blit(status_surface, (20, 20))

    info_text = f"Твой символ: {my_symbol}" if my_symbol else "Ожидание символа..."
    info_surface = font_small.render(info_text, True, (50, 50, 50))
    screen.blit(info_surface, (20, 60))

    top = 100
    cell = 200

    pygame.draw.line(screen, (0, 0, 0), (200, top), (200, top + 600), 4)
    pygame.draw.line(screen, (0, 0, 0), (400, top), (400, top + 600), 4)
    pygame.draw.line(screen, (0, 0, 0), (0, top + 200), (600, top + 200), 4)
    pygame.draw.line(screen, (0, 0, 0), (0, top + 400), (600, top + 400), 4)

    with lock:
        for i in range(9):
            row = i // 3
            col = i % 3
            x = col * cell + 70
            y = top + row * cell + 35

            if board[i] == "X":
                text = font_big.render("X", True, (200, 50, 50))
                screen.blit(text, (x, y))
            elif board[i] == "O":
                text = font_big.render("O", True, (50, 50, 200))
                screen.blit(text, (x, y))

    pygame.display.flip()


thread = threading.Thread(target=receive, daemon=True)
thread.start()

clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if my_turn:
                mx, my = event.pos

                if my >= 100:
                    col = mx // 200
                    row = (my - 100) // 200

                    if 0 <= col < 3 and 0 <= row < 3:
                        idx = row * 3 + col

                        with lock:
                            if board[idx] == " ":
                                send_line(f"MOVE;{idx}")
                                my_turn = False
                                status_text = "Ожидание хода соперника"

    draw_board()
    clock.tick(60)

client.close()
pygame.quit()