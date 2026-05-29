import socket

HOST = '0.0.0.0'
PORT = 8001

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

print("Server is running...")
clients = []
symbols = ["X", "O"]
board = [" "] * 9
curr = 0
game_over = False


def send_line(sock, text):
    sock.sendall((text + "\n").encode())


def broadcast(text):
    for c in clients:
        send_line(c, text)


def check_win():
    wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]

    for a, b, c in wins:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]

    if " " not in board:
        return "draw"

    return None


def send_board():
    broadcast("BOARD;" + ";".join(board))


for i in range(2):
    client, addr = server.accept()
    clients.append(client)
    print("Join:", addr)
    send_line(client, f"INFO;Ты играешь за {symbols[i]}")

broadcast("INFO;Оба игрока подключились, игра начинается")
send_board()
send_line(clients[curr], "YOUR_TURN")
send_line(clients[1 - curr], "INFO;Ход соперника")

buffers = ["", ""]

while not game_over:
    player = clients[curr]

    try:
        data = player.recv(1024).decode()
        if not data:
            break

        buffers[curr] += data

        while "\n" in buffers[curr]:
            line, buffers[curr] = buffers[curr].split("\n", 1)
            line = line.strip()

            if not line:
                continue

            parts = line.split(";")

            if parts[0] == "MOVE":
                try:
                    move = int(parts[1])
                except:
                    send_line(player, "INFO;Некорректный ход")
                    send_line(player, "YOUR_TURN")
                    continue

                if move < 0 or move > 8:
                    send_line(player, "INFO;Клетка вне диапазона 0-8")
                    send_line(player, "YOUR_TURN")
                    continue

                if board[move] != " ":
                    send_line(player, "INFO;Клетка уже занята")
                    send_line(player, "YOUR_TURN")
                    continue

                board[move] = symbols[curr]
                send_board()

                result = check_win()
                if result == "draw":
                    broadcast("END;Ничья")
                    game_over = True
                    break
                elif result in ["X", "O"]:
                    broadcast(f"END;Победил {result}")
                    game_over = True
                    break

                curr = 1 - curr
                send_line(clients[curr], "YOUR_TURN")
                send_line(clients[1 - curr], "INFO;Ход соперника")

    except Exception as e:
        print("Ошибка:", e)
        break

for c in clients:
    try:
        c.close()
    except:
        pass

server.close()
print("Server closed")