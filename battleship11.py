#Vel's battleship!
#Ver. 1.1

from random import randint
import socket, time, os, re, json

my_board = []
enemies_board = []
symbol = {
    "water" : ".", 
    "hit_water" : "-",
    "froth" : ",",
    "placed_ship" : "$",
    "ship" : "%",
    "hit_ship" : "*", 
    "sunk_ship" : "*",
    "surrounded_ship" : "#"
    }
messages = {
    "hit_water_my_turn" : "\nNot this time!",
    "hit_ship_my_turn" : "\nYou hit enemy ship!",
    "sunk_ship_my_turn" : "\nYou sunk enemy ship!",
    "hit_water_enemy_turn" : "\nYou're lucky this time!",
    "hit_ship_enemy_turn" : "\nYour ship has been hit!",
    "sunk_ship_enemy_turn" : "\nYour ship has been sunk!"
    }

def board_init(board): #additional rows and cols around the board that won't be printed
    for x in range(12):
        board.append([symbol["water"]] * 12)

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

board_init(my_board)
board_init(enemies_board)

columns=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
space="                                "

def print_boards(board1, board2):
    cls()
    print "\n\n\n\n" + space[:7]+"YOUR NAVY"+space+"ENEMIE'S NAVY"
    print "   "+(" ".join(columns))+space[:24]+(" ".join(columns))
    for i in range(1,len(board1)-1):
        if i<10:
            print " %d" % i,(" ".join(board1[i][1:11])), space[:19], " %d" % i,(" ".join(board2[i][1:11])) #without additional rows and cols around the board
        else:
            print "%d" % i,(" ".join(board1[i][1:11])), space[:19], "%d" % i,(" ".join(board2[i][1:11]))

def random_coordinates(board):
    return (randint(1, 10), randint(1, 10))

def random_dir():
    dir = ['h','v']
    return dir[randint(0,1)]

def prepare_coordinates(coordinates):
    try:
        row = int(re.search('10|[1-9]', coordinates).group())
        col = ord(re.search('[a-j]', coordinates, re.I).group().lower())-96
    except:# AttributeError:
        return (-1,-1)  
    return (row, col)

def surround_ship(coordinates, board, current_symbol, new_symbol, surr_symbol):
    surround_ship_do(coordinates, board, current_symbol, new_symbol, surr_symbol)
    surround_ship_do(coordinates, board, current_symbol, new_symbol, surr_symbol) 

def surround_ship_do(coordinates, board, current_symbol, new_symbol, surr_symbol):
    row=coordinates[0]
    col=coordinates[1]
    new=1
    while new:
        board[row][col]=new_symbol
        for x in range(-1,2):
           for y in range(-1,2):
               if board[row+x][col+y]==current_symbol:
                   new=2
                   row=row+x
                   col=col+y
               elif board[row+x][col+y]!= new_symbol:
                   board[row+x][col+y]=surr_symbol
        if new==2:
            new=1
        else:
            return

ship_coordinates=[]  
def place_ship(coordinates, mast_nr, direction, board):
    row=coordinates[0]
    col=coordinates[1]
    
    if (row==-1):
         return "That's not in the ocean!"
    elif (board[row][col] == symbol["ship"]):
        return "There's a ship there already!"
    elif (board[row][col] == symbol["froth"]):
        return "It's too close to another ship!"
    elif direction=='h':
        for x in range(1,mast_nr):
            if col+x > 10 or board[row][col+x] != symbol["water"]:
                return "Not enough place for your ship!"
        else:
            new_ship=[] #for coordinates of new ship
            for x in range(mast_nr):
                board[row][col+x] = symbol["placed_ship"]
                new_ship.append([row, col+x])                                   
            ship_coordinates.append(new_ship)  #append list of new ship's coordinates to list of ships
            surround_ship(coordinates, my_board, symbol["placed_ship"], symbol["ship"], symbol["froth"])
            return 1
    elif direction=='v':
        for x in range(1,mast_nr):
            if row+x > 10 or board[row+x][col] != symbol["water"]:
                return "Not enough place for your ship!"
        else:
            new_ship=[]
            for x in range(mast_nr):
                board[row+x][col] = symbol["placed_ship"]
                new_ship.append([row+x, col])                    
            ship_coordinates.append(new_ship)
            surround_ship(coordinates, my_board, symbol["placed_ship"], symbol["ship"], symbol["froth"])
            return 1
    else:
        return "Invalid direction! Should be 'h' or 'v'" 
            
ship_kinds = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
print_boards(my_board,enemies_board)

place_method = ''
while place_method!='y' and place_method!='r':
    place_method = raw_input("\nDo you want to place ships by (y)ourself or (r)andomly? ").lower()

result = 0
for mast in ship_kinds:
    while result!=1: #while ship wasn't added to board properly
        if place_method == "y":
            coord = raw_input("\nPut coordinates of %d-masted ship (e.g. i7): "% mast)
            prepared_coord = prepare_coordinates(coord)
            if mast > 1: #don't care about direction for 1-masted ship
                direc = (raw_input("(H)orizontal or (v)ertical? ")).lower()
        else:
            prepared_coord = random_coordinates(my_board) 
            direc = random_dir()
        result = place_ship(prepared_coord,mast,direc,my_board)
        if result!=1: print result
    else:
        result=0
        print_boards(my_board,enemies_board)

conn_method = 0
while conn_method != 's' and conn_method != 'c':
    conn_method = raw_input("Ready for the battle, captain! Do you want to connect as (s)erver or (c)lient? ").lower()

turn = 0 #1- your turn, 0- enemie's turn
if conn_method == 'c':    
    HOST = raw_input("Put server's IP: ")
    PORT = int(raw_input("and port number: "))

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection_status = 1
    while connection_status == 1:
        connection_status = 0
        try:
            conn.connect((HOST, PORT))
        except socket.error:
            print "Server is not available yet..."
            connection_status = 1
            time.sleep(3)
    print "\nConnected! Let's start the battle!\n"
    turn = 1#client is always first
elif conn_method == 's':
    HOST = ''
    PORT = int(raw_input("Put port number: "))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen(1)
    print "Waiting for the enemy..."
    conn, addr = s.accept()
    print "\nConnected by", addr, ". Let's start the battle!\n"

enemies_hit_amount = 0
my_hit_amount = 0

while enemies_hit_amount < 20 and my_hit_amount < 20: #4+3+3+2+2+2+1+1+1+1=20
    while turn == 1:
        shot = raw_input("\nYour turn! Put coordinates of shot (e.g. d6): ")
        prep_shot = prepare_coordinates(shot)
        conn.sendall(json.dumps(prep_shot))
        result = (json.loads(conn.recv(1024))).encode('utf-8')
        enemies_board[prep_shot[0]][prep_shot[1]] = symbol[result]
        if result == "hit_water":
            turn = 0
        else:
            my_hit_amount+=1
            if result=="sunk_ship":
               surround_ship(prep_shot, enemies_board, symbol["hit_ship"], symbol["surrounded_ship"], symbol["hit_water"]) 
        print_boards(my_board, enemies_board) 
        print messages[result+"_my_turn"]
        time.sleep(1)
    else:
        e_shot = json.loads(conn.recv(1024))
        e_shot_display = chr(e_shot[1]+96) + str(e_shot[0])
        if e_shot==[-1,-1]:
            result = "hit_water"
            e_shot_display = "out of the battlefield"
            turn = 1
        elif my_board[e_shot[0]][e_shot[1]] != symbol["ship"]:
            result = "hit_water"
            turn = 1
        else:
            enemies_hit_amount += 1
            result = "hit_ship"
            my_board[e_shot[0]][e_shot[1]] = symbol[result]
            for ship in ship_coordinates:
                if e_shot in ship:
                    ship.remove((e_shot))
                if not ship:
                    result="sunk_ship"
                    ship_coordinates.remove(ship)
        conn.sendall(json.dumps(result))
        my_board[e_shot[0]][e_shot[1]] = symbol[result]
        print_boards(my_board, enemies_board)
        print "\nEnemie's missile: " + e_shot_display
        print messages[result+"_enemy_turn"] 
else:
    if enemies_hit_amount == 20:
        print "Your navy has been sunk!"
    else:
        print "You've sunk the enemy army! Congratulations, Captain!"
    print "Game Over"

    conn.close()

