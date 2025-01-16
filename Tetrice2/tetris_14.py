import os

from fltk import *
from time import sleep
import random
import time
import json
from copy import deepcopy

widthWindow = 600
heightWindow = 600
score = 0
level = 1
drop_interval = 0.7  # Interval for figure dropping
paused = False  #pause
window_created = False
exit_to_menu = False
bon = False

# Create variables for the game
current_figure = None
cooldown_pourrissement = 15
figure_x = 5
figure_y = 0
cell_size = 0
game_board = [[0] * 10 for _ in range(20)]  # Game board (10 cols x 20 rows)

def lire_polys(fichier):
    resultat = []
    piece_actuelle = []
    with open(fichier, "r") as f:
        contenu = f.readlines()
        for i in range(len(contenu)):
            ligne_piece = []
            if '+' in contenu[i]:
                for c in contenu[i].replace('\n', ''):
                    if c == '+':
                        ligne_piece.append(1)
                    elif c == ' ':
                        ligne_piece.append(0)
                piece_actuelle.append(ligne_piece)
            elif '+' not in contenu[i] and piece_actuelle:
                resultat.append(piece_actuelle)
                piece_actuelle = list()
        if piece_actuelle:
            resultat.append(piece_actuelle)
    max_val = 0
    for pieces in resultat:
        val_temp = max(len(sous_piece) for sous_piece in pieces)
        if max_val < val_temp:
            max_val = val_temp
        for sous_piece in pieces:
            while len(sous_piece) < max_val:
                sous_piece.append(0)
        while len(pieces) < max_val:
            pieces.append([0]*max_val)
            if len(pieces) < max_val:
                pieces.insert(0,[0]*max_val)
    return resultat

# lit le fichier, transforme en matrices et leur attribut un nom (f1, f2, f3,etc) dans le dictionnaire
if bon == True:
    fig = lire_polys("polyominos2.txt")
elif bon == False:
    fig = lire_polys("polyominos.txt")
print(bon)
print(fig)
tri_fig = dict()
for i, mat in enumerate(fig):
    tri_fig[f'f{i+1}'] = mat

# fait une liste qui repertorie tous les noms des matrices (f1, f2, f3,etc)
figures = []
for i in range(len(tri_fig)):
    figures.append(f'f{i+1}')

color = ['light grey',"red", "blue", "yellow", "green", "cyan"]

def new_fig(shape, color_index):
    '''prend une figure et remplace les 1 par la valeur de color_index'''
    print("new_fig : ", color_index, color[color_index])
    fig = deepcopy(shape)
    print('copie de ',shape," : ", fig)
    for row in range(len(shape)):
        for col in range(len(shape[0])):
            if shape[row][col] == 1:
                fig[row][col] = color_index
    return fig

# Creating a play zone
def gameZone():
    '''dessine la zone de jeu (fond, bordure, etc)'''
    global cell_size
    x = 250
    y = 500
    c = 10
    l = 20
    cell_size = x // c

    x_offset = (widthWindow - x) // 2
    y_offset = (heightWindow - y) // 2

    for row in range(l):
        for col in range(c):
            x1 = col * cell_size + x_offset
            y1 = row * cell_size + y_offset
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            rectangle(x1, y1, x2, y2, "grey", "light grey")

    ligne(x_offset, y_offset, x_offset, y_offset + y, "black", 2)
    ligne(x_offset + x + 2, y_offset, x_offset + x + 2, y_offset + y, "black", 2)
    ligne(x_offset, y_offset + y + 1, x_offset + x, y_offset + y + 1, "black", 2)

def draw_figure(figure, x, y):
    '''dessine la figure'''
    x_offset = (widthWindow - 250) // 2
    y_offset = (heightWindow - 500) // 2
    for row in range(len(figure)):  
        for col in range(len(figure[row])):  
            if figure[row][col] != 0:
                x1 = (col + x) * cell_size + x_offset
                y1 = (row + y) * cell_size + y_offset
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                rectangle(x1, y1, x2, y2, "grey", color[figure[row][col]])

def draw_board(changed_cells=None):
    '''dessine la zone de jeu avec les pieces'''
    if changed_cells is None:
        changed_cells = [(row, col) for row in range(20) for col in range(10)]
    
    x_offset = (widthWindow - 250) // 2
    y_offset = (heightWindow - 500) // 2

    for row, col in changed_cells:
        x1 = col * cell_size + x_offset
        y1 = row * cell_size + y_offset
        x2 = x1 + cell_size
        y2 = y1 + cell_size
        if game_board[row][col] != 0:
            new_color = color[game_board[row][col]]
        else:
            new_color = color[0]
        rectangle(x1, y1, x2, y2, "grey", new_color)

def draw_saved_board():
    x_offset = (widthWindow - 250) // 2
    y_offset = (heightWindow - 500) // 2

    for row in range(20):
        for col in range(10):
            x1 = col * cell_size + x_offset
            y1 = row * cell_size + y_offset
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            if game_board[row][col] != 0:
                new_color = color[game_board[row][col]]  # Select the color of the saved shape
            else:
                new_color = color[0]  # Empty cells
            rectangle(x1, y1, x2, y2, "grey", new_color)


def clear_figure(figure, x, y):
    """nettoie derriere le passage d'une piece"""
    x_offset = (widthWindow - 250) // 2
    y_offset = (heightWindow - 500) // 2

    for row in range(len(figure)):
        for col in range(len(figure[row])):
            if figure[row][col] != 0:  # si la case a une autre couleur que 'light grey'
                x1 = (col + x) * cell_size + x_offset
                y1 = (row + y) * cell_size + y_offset
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                rectangle(x1, y1, x2, y2, "grey", color[0])

# Check for figure collisions
# Function to check for collisions
def is_collision(figure, x, y):
    for row, line in enumerate(figure):
        for col, cell in enumerate(line):
            if cell != 0:
                board_x, board_y = col + x, row + y
                if board_x < 0 or board_x >= 10 or board_y >= 20:
                    return True
                if game_board[board_y][board_x] != 0:
                    return True
    return False

# Function to drop figures
def drop_figure():  # Falling figures
    global figure_y
    # Clear the previous figure from the board
    clear_figure(current_figure, figure_x, figure_y)
    figure_y += 1  # Move the figure down by 1 row

    # Check for collisions at the new position
    if is_collision(current_figure, figure_x, figure_y):
        figure_y -= 1  # Reset the position if it collides or goes beyond the limits
        
        # Draw the figure at the last valid position
        draw_figure(current_figure, figure_x, figure_y)
        
        # Place the figure on the board and set it as part of the game state
        place_figure_on_board(current_figure, figure_x, figure_y)
        
        return False  # Stop the figure from falling
    
    # If no collision, draw the figure at the new position
    draw_figure(current_figure, figure_x, figure_y)
    
    return True

# Function to place the figure on the board
def place_figure_on_board(figure, x, y):
    # Iterate through the rows and columns of the shape
    for row in range(len(figure)):  # Go through the lines of the figure
        for col in range(len(figure[row])):  # Go through the columns of the figure
            if figure[row][col] != 0:  # If the shape cell is filled
                # Set the position on the playing field
                game_board[row + y][col + x] = figure[row][col]
# To check the keystrokes
def handle_keys():
    global figure_x, figure_y, current_figure, paused, exit_to_menu

    ev = donne_ev()
    if ev is not None:
        key = touche(ev)
        if key == 'p':  # Toggle pause
            paused = not paused
            if paused:
                show_pause_window()  # Display the pause window
            else:
                efface_tout()  # Clear the screen to resume the game
                rectangle(0, 0, widthWindow - 1, heightWindow - 1, "white", "dark grey")  # Drawing the boundaries of the game
                gameZone()  # Display play area
                draw_board()  # Draw the current board
                draw_figure(current_figure, figure_x, figure_y)  # Show shape

        if not paused:  # Other actions are available only if the game is not paused
            if key == 'Left': # Press to the left
                if not is_collision(current_figure, figure_x - 1, figure_y):
                    figure_x -= 1
                    clear_figure(current_figure, figure_x + 1, figure_y)
            elif key == 'Right': # Press to the right
                if not is_collision(current_figure, figure_x + 1, figure_y):
                    figure_x += 1
                    clear_figure(current_figure, figure_x - 1, figure_y)
            elif key == 'Down': # Press to the down
                if not is_collision(current_figure, figure_x, figure_y + 1):
                    figure_y += 1
                    clear_figure(current_figure, figure_x, figure_y - 1)
                # print('y= ', figure_y)
            elif key == 'Up':
                if figure_x + len(current_figure[0]) >= 11:
                    clear_figure(current_figure, figure_x, figure_y)
                    figure_x -= 1
                    rotation(current_figure)
                    clear_figure(current_figure, figure_x, figure_y)
                elif figure_x - len(current_figure[0]) <= -3:
                    clear_figure(current_figure, figure_x, figure_y)
                    figure_x += 1
                    rotation(current_figure)
                    clear_figure(current_figure, figure_x, figure_y)
                else:
                    clear_figure(current_figure, figure_x, figure_y)
                    rotation(current_figure)
                    clear_figure(current_figure, figure_x, figure_y)
            if key == 'm':  # Exit to the menu
                save_game()  # Save game
                exit_to_menu = True
            elif key == 's':  # Saving the game
                save_game()
            

        draw_figure(current_figure, figure_x, figure_y) # Drawing figures


def rotation(current_figure):
    n = len(current_figure)

    # les colonnes deviennent des lignes et ces dernieres deviennent des colonnes
    for i in range(n):
        for j in range(i, n):
            current_figure[i][j], current_figure[j][i] = current_figure[j][i], current_figure[i][j]

    # on inverse les listes pour faire une rotation dans le sens des aiguilles d'une montre
    for i in range(n):
        current_figure[i].reverse()


def clear(game_board):
    '''fonction pour supprimer les lignes remplies'''
    width = 10
    height = 20
    full_rows = [row for row in range(height) if all(game_board[row][col] != 0 for col in range(width))]
    for row in full_rows:
        for r in range(row, 0, -1):
            game_board[r] = game_board[r - 1]
        game_board[0] = [0] * width
    return len(full_rows)


def display_score():
    '''affiche le score'''
    care_x1 = widthWindow - 140  # point for displaying the invoice
    care_y1 = heightWindow // 8  # point for displaying the invoice
    care_x2 = widthWindow - 50
    care_y2 = heightWindow // 8 + 50
    score_x = (care_x2 + care_x1) // 2  # center for displaying the account number
    score_y = (care_y2 + care_y1) // 2  

    rectangle(care_x1, care_y1, care_x2, care_y2, "black", "white")
    texte(score_x - 10, score_y - 45, "Score:", "white", "center", taille=18)
    texte(score_x, score_y, f"{score}", "black", "center", taille=14)

def display_level():
    '''affiche le niveau'''
    care_x1 = 40  # point for displaying the invoice
    care_y1 = heightWindow // 8  # point for displaying the invoice
    care_x2 = 130
    care_y2 = heightWindow // 8 + 50
    score_x = (care_x2 + care_x1) // 2  # center for displaying the account number
    score_y = (care_y2 + care_y1) // 2  

    rectangle(care_x1, care_y1, care_x2, care_y2, "black", "white")
    texte(score_x - 10, score_y - 45, "Level:", "white", "center", taille=18)
    texte(score_x, score_y, f"{level}", "black", "center", taille=14)

def calculate_points(lines_cleared):
    '''calcul des points selon le niveau actuel et en fonction du nombre de lignes effacées'''
    global level
    points_table = {}
    if level == 1:
        points_table = {
            1: 40,    
            2: 100,   
            3: 300,   
            4: 500    
        }
    elif level == 2:
        points_table = {
            1: 90,    
            2: 150,   
            3: 400,   
            4: 600    
        }
    elif level == 3:
        points_table = {
            1: 150,    
            2: 200,   
            3: 500,   
            4: 800    
        }
    elif level == 4:
        points_table = {
            1: 250,    
            2: 360,   
            3: 700,   
            4: 1000    
        }
    return points_table.get(lines_cleared, 0)

def update_score(lines_cleared):
    '''Met à jour le compte global sur la base des lignes apurées'''
    global score
    points = calculate_points(lines_cleared)
    score += points
    print(f"Points pour ce mouvement: {points},:  Nombre total de points {score}")

def update_level():
    '''met a jour le niveau selon le score actuel du joueur'''
    global score, level, drop_interval, cooldown_pourrissement
    if score >= 250:
        level = 2
        drop_interval = 0.5
        cooldown_pourrissement = round(cooldown_pourrissement*0.9)
    if score >= 500:
        level = 3
        drop_interval = 0.3
        cooldown_pourrissement = round(cooldown_pourrissement * 0.9)
    if score >= 1000:
        level = 4
        drop_interval = 0.1
        cooldown_pourrissement = round(cooldown_pourrissement * 0.9)


def save_game():
    '''sauvegarde les infos du jeu dans un fichier externe'''
    global game_board, current_figure, figure_x, figure_y, color_index, score, level

    save_data = {
        "game_board": game_board,
        "current_figure": current_figure,
        "figure_x": figure_x,
        "figure_y": figure_y,
        "current_color": current_color,
        "score": score,
        "level": level
    }

    with open("save_game.py", "w") as file:
        json.dump(save_data, file)

def load_game():
    '''charge les infos de jeu d'un fichier externe'''
    global game_board, current_figure, figure_x, figure_y, current_color, score, level

    try:
        with open("save_game.py", "r") as file:
            save_data = json.load(file)

        game_board = save_data["game_board"]
        current_figure = save_data["current_figure"]
        figure_x = save_data["figure_x"]
        figure_y = save_data["figure_y"]
        current_color = save_data["current_color"]
        score = save_data["score"]
        level = save_data["level"]

        # Updating the game visualization
        efface_tout()  # Clear the screen
        rectangle(0, 0, widthWindow - 1, heightWindow - 1, "white", "dark grey")  # Frame
        gameZone()  # Field of play
        draw_saved_board()  # Redraw all cells
        draw_figure(current_figure, figure_x, figure_y)  # Draw the current shape

        return True  # Upload successful
    except FileNotFoundError:
        return False  # File not found

def show_pause_window():
    '''afficher le menu pause'''
    efface_tout()
    rectangle(0, 0, widthWindow - 1, heightWindow - 1, "black", "dark grey")
    texte(widthWindow // 2 - 50, heightWindow // 2 - 20, "PAUSE", taille=24, couleur="white")
    texte(widthWindow // 2 - 100, heightWindow // 2 + 20, "Press 'p' to resume", taille=16, couleur="white")
    mise_a_jour()



def main_menu():
    """permet de créer le menu principal du jeu"""
    global window_created, exit_to_menu 

    if not window_created:  
        cree_fenetre(widthWindow, heightWindow)
        window_created = True # met à jour le statut de la fenetre
    else:
        efface_tout()
    x1 = 200
    x2 = 400
    y1 = 100
    y2 = 200
    play_x1, play_y1 = x1, y1
    play_x2, play_y2 = x2, y2
    continue_x1, continue_y1 = x1, y1 + 150
    continue_x2, continue_y2 = x2, y2 + 150
    exit_x1, exit_y1 = x1, y1 + 300
    exit_x2, exit_y2 = x2, y2 + 300
    
    rectangle(0, 0, widthWindow - 1, heightWindow - 1, "white", "dark grey")
    rectangle(play_x1, play_y1, play_x2, play_y2, "blue", "blue")
    texte(300, y1 + 50, "Play", taille=20, couleur="white", ancrage='center')
    
    # ajout du bouton 'continuer'
    if os.path.exists("save_game.py"):
        rectangle(continue_x1, continue_y1, continue_x2, continue_y2, "green", "green")
        texte(300, y1 + 200, "Continue", taille=20, couleur="white", ancrage='center')
    else:
        # si il n'y a pas de sauvegarde on n'affiche pas de bouton 'continuer'
        continue_x1, continue_y1, continue_x2, continue_y2 = 0, 0, 0, 0

    rectangle(exit_x1, exit_y1, exit_x2, exit_y2, "red", "red")
    texte(300, y1 + 350, "Exit", taille=20, couleur="white", ancrage='center')

    while True:
        x, y = attend_clic_gauche()  # on attend un clic et on récupère les coordonnées quand un clic est effectué

        # On vérifie que le bouton 'Play' est pressé
        if play_x1 <= x <= play_x2 and play_y1 <= y <= play_y2:
            return "play"
        # On vérifie que le bouton 'Continue' est pressé
        elif continue_x1 <= x <= continue_x2 and continue_y1 <= y <= continue_y2:
            return "continue_game"
        # On vérifie que le bouton 'Exit' est pressé
        elif exit_x1 <= x <= exit_x2 and exit_y1 <= y <= exit_y2:
            return "exit"

def menu_chois():
    x1, x2 = 200, 400
    y1, y2 = 100, 200
    play_clasic_x1, play_clasic_y1 = x1, y1
    play_clasic_x2, play_clasic_y2 = x2, y2
    play_bonus_x1, play_bonus_y1 = x1, y1 + 150
    play_bonus_x2, play_bonus_y2 = x2, y2 + 150

    rectangle(0, 0, widthWindow - 1, heightWindow - 1, "white", "dark grey")
    rectangle(play_clasic_x1, play_clasic_y1, play_clasic_x2, play_clasic_y2, "blue", "blue")
    texte(300, y1 + 50, "Play Clasic", taille=20, couleur="white", ancrage="center")
    rectangle(play_bonus_x1, play_bonus_y1, play_bonus_x2, play_bonus_y2, "green", "green")
    texte(300, y1 + 200, "Play Bonus", taille=20, couleur="white", ancrage="center")

    while True:
        x, y = attend_clic_gauche() 

        if play_clasic_x1 <= x <= play_clasic_x2 and play_clasic_y1 <= y <= play_clasic_y2:  # Play Clasic
            return "clasic"
        elif play_bonus_x1 <= x <= play_bonus_x2 and play_bonus_y1 <= y <= play_bonus_y2:  # Play Bonus
            return "bonus"

def main_game():
    """boucle principale du jeu"""
    global current_figure, figure_x, figure_y, current_color, drop_interval, score, level, paused, exit_to_menu, cooldown_pourrissement
    temps1 = time.time()
    if current_figure is None:
        current_color = random.randrange(1, len(color))
        fig_aleatoire = figures[random.randrange(0,len(figures))]  # -> str
        current_figure = new_fig(tri_fig[fig_aleatoire], current_color)
        print("if current_fig is None : ", current_color)
        figure_x, figure_y = 3, -1
        score = 0
        level = 1

    last_drop_time = time.time()
    # print(last_drop_time)
    # print(drop_interval)
    efface_tout()  # Clear the screen
    rectangle(0, 0, widthWindow - 1, heightWindow - 1, "white", "dark grey")  # Draw game border

    gameZone()  # Draw the game zone (grid)
    draw_saved_board()

    while not exit_to_menu:

        handle_keys()  # Handle user inputs (left, right, rotate, etc.)
        if paused:
            show_pause_window()  # Display the pause screen
            sleep(0.1)  # Avoid excessive workload
            continue  # Skip game logic while the game is paused
        display_score()  # Display the current score
        display_level()

        temps_actuel = time.time()
        if temps_actuel - temps1 >= cooldown_pourrissement:
            # print('hey!')
            blocks = []
            for row in range(len(game_board)):
                for col in range(len(game_board[0])):
                    if game_board[row][col] != 0:
                        blocks.append((row, col))
            if blocks:
                coos = random.randrange(0,len(blocks))
                game_board[blocks[coos][0]][blocks[coos][1]] = 0
                print(len(blocks))
                blocks.pop(coos)
                print(len(blocks))
            temps1 = time.time()
            draw_board()
        if time.time() - last_drop_time >= drop_interval: 
            if not drop_figure():  # If the figure has reached the bottom or collided
                cleared_rows = clear(game_board)  # Clear filled rows
                if cleared_rows > 0:
                    update_score(cleared_rows)  # Add points for cleared rows
                    update_level()
                draw_board()  # Redraw the game board (after clearing rows)

                # Generate a new figure
                print("len ", len(color))
                current_color = random.randrange(1, len(color))
                print("couleur = ", color[current_color],"indice: ", current_color)
                fig_aleatoire = figures[random.randrange(0, len(figures))]  # -> str
                current_figure = new_fig(tri_fig[fig_aleatoire], current_color)
                print(current_figure)
                figure_x, figure_y = 3, 0
                # print(current_color)
                # print(current_figure)
                # print(game_board)
                if is_collision(current_figure, figure_x, figure_y):
                    if bon == True or bon == False:  # If in Bonus mode, prevent returning to menu
                        continue  # Skip game over logic for bonus mode
                    break 

            last_drop_time = time.time()  # Update the last drop time
        clear(game_board)  # Clear the game board for the next cycle
        mise_a_jour()  # Update the screen
        sleep(0.1)  # Control the game loop speed
    if exit_to_menu:  # If you exit the menu, save the game
        save_game()  # Saving the game
        start_game() 
    current_figure = None
# launching the program
def start_game():
    global bon, fig, tri_fig, figures
    while True:
        action = main_menu()
        if action == "play":
            mode = menu_chois()
            if mode == "clasic":
                bon = False
            elif mode == "bonus":
                bon = True
            if bon:
                fig = lire_polys("polyominos2.txt")
            else:
                fig = lire_polys("polyominos.txt")

            print("Mode de jeu:", "Bonus" if bon else "Classic")
            print("Figure:", fig)
            tri_fig = {f'f{i+1}': mat for i, mat in enumerate(fig)}
            figures = [f'f{i+1}' for i in range(len(tri_fig))]
            main_game()
        elif action == "continue_game":
            if load_game():  # Loads the game if the file exists
                main_game()  # Called to continue the game
            else:
                texte(300, 300, "No saved game found.", taille=20, couleur="red", ancrage="center")
                sleep(2)
        elif action == "exit":
            efface_tout()
            exit()  # Closing the program


if __name__ == '__main__':
    start_game()
