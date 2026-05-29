import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 8001))
server.listen()

print("Server is running")
clients = []
symbols = ["X", "O"]

board = [" "] * 9

curr = 0

def print_board():
    return f"""
{ board [0] } | { board [1] } | { board [2] }
{ board [3] } | { board [4] } | { board [5] }
{ board [6] } | { board [7] } | { board [8] }
"""

def check_win():
    wins = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    for combo in wins:
        a, b, c = combo
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]

    if ' ' not in board:
        return 'nch'

    return None

for i in range(2):
    client, addr = server.accept()
    clients.append(client)
    print('Join', addr)
    client.send(f"Ты играешь за { symbols[i] }".encode())

while True:
    player = clients[curr]
    symbol = symbols[curr]

    player.send("Your turn".encode())
    move = player.recv(1024).decode()

    print(move)
    try:
        move = int(move)
        if board[move] == ' ':
            board[move] = symbol

            game_state = print_board()
            for c in clients:
                c.send(";".join(board).encode())

            win = check_win()

            if win:
                if win == "nch":
                    msg = "Ничья"
                else:
                    msg = "Победил" + win

                for c in clients:
                    c.send(msg.encode())
                break

            curr = 1 - curr
    except:
        pass

server.close()

# print("Server started")
# players = {}
#
# lock = threading.Lock()
#
# def handle_client(conn):
#     global players
#
#     players[conn] = [100, 100]
#
#     try:
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#
#             dx, dy = pickle.loads(data)
#
#             with lock:
#                 players[conn][0] += dx
#                 players[conn][1] += dy
#
#             with lock:
#                 state = pickle.dumps(players)
#                 for c in players:
#                     c.send(state)
#     except:
#         pass
#
#     with lock:
#         del players[conn]
#         conn.close()
#
# while True:
#     conn, addr = server.accept()
#     threading.Thread(target=handle_client, args=(conn, )).start()