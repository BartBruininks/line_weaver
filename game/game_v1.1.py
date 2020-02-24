# -*- coding: utf-8 -*-
"""
Made by Bart Bruininks Dec 2019 at the LAN party

A colourful attempt of making my own first game, very much based on achtung
the curve. A single pc multiplayer game you all should have played.
"""
import pygame
import numpy as np
import random



def initiate_music():
    """
    Opens wav 1-9 and plays them silently in a loop. All sounds are shuffled
    for random consistent sounds for each player.
    
    Returns:
        all_sounds (list) of len 9.
    """
    pygame.mixer.set_num_channels(9)
    all_sounds = []
    for line in range(1,10):
        filename = "{}.wav".format(line)
        all_sounds.append(pygame.mixer.Sound(filename))
        
    for line in range(0,9):
        all_sounds[line].set_volume(0)
        all_sounds[line].play(1000)
    
    random.shuffle(all_sounds)
    
    return all_sounds



# -------- Player Object ---------------
class Player:
    """
    All game logic and settings for a single player. Such as controls, death
    positions, movement, etc.
    """
    def __init__(self, identity, FPS):
        """
        Initiating this player.
        """
        self.FPS = FPS
        # Set starting positions
        # Instadeath is possible hardcore rulezzZZ!!!
        self.x = int(random.random()*size[0])
        self.y = int(random.random()*size[1])
        # Random color is a feature, white is invisibraH!!!
        self.color = (int(random.random()*256), 
                      int(random.random()*256), 
                      int(random.random()*256),
                      )
        # Set players death status
        self.alive = True
        # The controls for directing the player in the playfield
        self.controls = {}
        # Are you invinsibraH?
        self.not_drawing = 0
        # Sets the player hitbox for collision detection
        self.set_hitbox(THICKNESS)

        # Old player position
        self.old_x = self.x
        self.old_y = self.y
        # The old player direction
        self.old_move = 'RIGHT'
        # Simple player identifier (integer increments)
        self.id = identity
        
        
    def set_hitbox(self, THICKNESS):
        """
        Sets the hitbox of this player based on its geometry.
        """
        hitbox = pygame.Surface((THICKNESS*2, THICKNESS*2))
        pygame.draw.circle(hitbox, self.color, (THICKNESS,THICKNESS), THICKNESS)
        hitbox_raw = pygame.surfarray.pixels2d(hitbox)
        hitbox = np.reshape(hitbox_raw, (THICKNESS*2, THICKNESS*2))
        hitbox[hitbox != 0] = 1
        self.hitbox = hitbox
            
        
    def set_key(self, direction, all_events):
        """
        Binds a key for this player. 

        Parameters
        ----------
        direction : TYPE
            One of the following strings: RIGHT, LEFT, UP, DOWN
        all_events : TYPE
            All events which were caught since the last frame.

        Returns
        -------
        Adds the key binding to the player.controls dict.

        """
        draw_text('Press a key to bind to {}'.format(direction), screen, True, 0)
        for event in all_events:
            if event.type == pygame.KEYDOWN:
                self.controls[direction] = event.key
                draw_text('{} was assigned to \'{}\''.format(direction, pygame.key.name(self.controls[direction])), 
                          screen,
                          True,
                          700) 
        
        
    def set_controls(self, all_events):
        """
        Binds all controls for this player.
        """
        directions = ['LEFT', 'RIGHT', 'UP', 'DOWN']
        self.set_key(directions[len(self.controls)], all_events)
                
            
    def draw_position(self):
        """
        Draw this player on the playfield.
        """
        if int(COUNTER*random.random()) % (self.FPS//GAP_FREQ) == 0 and self.not_drawing <= 0:
            self.not_drawing = int(random.random() * GAP) + 5
        elif self.not_drawing <= 0:
            # A PBC fixing condition
            if sum(abs(np.array([self.x, self.y]) - np.array([self.old_x, self.old_y]))) <= SPEED * 3:
                #pygame.draw.line(screen, 
                #                 self.color, 
                #                 (self.old_x, self.old_y), 
                #                 (self.x, self.y), 
                #                 THICKNESS)
                # Handling higher drawing precision than FPS
                offset = (self.x-self.old_x,
                          self.y-self.old_y)
                for single_draw in range(1, HYPER_DRAWING + 1):
                    single_draw = single_draw/HYPER_DRAWING
                    pygame.draw.circle(
                        screen, 
                        self.color,
                        (self.old_x + int(offset[0]*single_draw), 
                         self.old_y + int(offset[1]*single_draw)), 
                        THICKNESS,
                        )
    
        self.not_drawing -= 1
        
        
    def move(self):
        """
        Defines the new positions of this player based on keyboard input.
        """
        moved = False
        # Up
        if pressed_keys[self.controls['UP']] == 1:
            self.y = (self.y - SPEED) % size[1]
            self.old_move = 'UP'
            moved = True
        # Down
        if pressed_keys[self.controls['DOWN']] == 1:
            self.y = (self.y + SPEED) % size[1]
            self.old_move = 'DOWN'
            moved = True
        # Right
        if pressed_keys[self.controls['RIGHT']] == 1:
            self.x = (self.x + SPEED) % size[0]
            self.old_move = 'RIGHT'
            moved = True
        # Left
        if pressed_keys[self.controls['LEFT']] == 1:
            self.x = (self.x - SPEED) % size[0]
            self.old_move = 'LEFT'
            moved = True
        # Use old move
        if not moved:
            if self.old_move == 'UP':
                self.y = (self.y - SPEED) % size[1]
            elif self.old_move == 'DOWN':
                self.y = (self.y + SPEED) % size[1]
            elif self.old_move == 'RIGHT':
                self.x = (self.x + SPEED) % size[0]
            elif self.old_move == 'LEFT':
                self.x = (self.x - SPEED) % size[0]
    
        
    def death(self, death_array):
        """
        Checks if this player should rather be dead. This is done by 
        comparing its current position and occupied pixels with the pixels
        in the death array. Overlap == DEATH!, with some slightly more fancy
        
        Also handles turning on your music when you die.
        """
        # Trying to kill a player
        # Obtaining lethal pixels
        temp_death_array = np.copy(death_array[self.x-THICKNESS:self.x+THICKNESS, 
                                               self.y-THICKNESS:self.y+THICKNESS])
        temp_death_array[temp_death_array != 1] = 0
        
        #A reasonable fix to prevent PBC crash due to array size mismatch
        overlap = False
        try:
            temp_death_array += self.hitbox
            overlap = np.isin(2, temp_death_array)
        except ValueError:
            if death_array[(self.x, self.y)] == 1:
                overlap = True
        
        if overlap and not game.immortal:
            pygame.draw.circle(screen, RED, (self.x, self.y), THICKNESS*3)
            self.alive = False
            # Sets the sounds slightly bigger than 0 making it fade in due to 
            # self.update
            all_sounds[self.id-1].set_volume(0.05)
        
        
    def update(self, death_array):
        """
        Prepare this player for the next frame. Also handles sound fading
        propagation over frames.
        """
        if self.alive:
            self.move()
            if COUNTER >= self.FPS*FREE_TIME:
                self.death(death_array)
            if self.alive:
                self.draw_position()
                self.old_x = self.x
                self.old_y = self.y
        # Fading in your sound upon death setting it to a value slightly 
        # bigger than 0
        if all_sounds[self.id-1].get_volume() > 0 and all_sounds[self.id-1].get_volume() < 1:
            all_sounds[self.id-1].set_volume(all_sounds[self.id-1].get_volume()+0.01)
        
        
        
class Game:
    def __init__(self, FPS):
        """
        Setting up the playfield.
        """
        self.clock = pygame.time.Clock()
        self.FPS = FPS
        self.current_player = 1
        self.previous_player = 0
        self.score = dict()
        self.init = True
        self.restart = False # not needed?
        self.progress = 0
        self.immortal = False
        self.death_array = np.zeros(size, dtype=int)
        self.death_tolerance = THICKNESS + 3 


    def intro_menu(self):
        """
        Drawing of the intro menu and changing music.
        """
        # Setting intro music
        for line in range(len(all_sounds)):
            if random.random() > 0.4:
                all_sounds[line].set_volume(1)
        draw_text('Have a seat and relax...', screen, True, 4000)
        draw_text('Press \'Backspace\' to start a new round', screen, True, 3000)
        draw_text('Press \'Home\' to reset players', screen, True, 3000)
        draw_text('Press \'Escape\' to quit', screen, True, 3000)
        
        
    def new_game(self, all_events, progress):
        """
        Drawing the newgame menu and changing the music. Also initiates the
        players.
        """
        # Setting the amount of players
        # Turning off previous sounds
        for line in range(len(all_sounds)):
            all_sounds[self.current_player-2].set_volume(0)
        if progress == 0:
            draw_text('Enter the amount of players', screen, True, 0)
            # Changing or setting intro music
            for line in range(len(all_sounds)):
                if random.random() > 0.4:
                    all_sounds[line].set_volume(1)
            progress += 1

        elif progress == 1:
            for event in all_events:
                if event.type == pygame.KEYDOWN:
                    try:
                        self.number_of_players = int(pygame.key.name(event.key))
                        if self.number_of_players != 0:
                            draw_text('{} player(s) will be initiated'.format(
                                self.number_of_players), screen)
                            # Stopping intro music
                            for line in range(len(all_sounds)):
                                all_sounds[line].set_volume(0)            
                            progress += 1
                    except ValueError:
                        continue
        
        # Inititaing the Player dict and setting the score to 0 and draw the
        # first position of the players.
        elif progress == 2:
            # Initialize the Players dict
            self.players = dict()
            for player in range(1, self.number_of_players+1):
                # Reset score
                game.score[player] = 0
                self.players[player] = Player(player, self.FPS)
 
            # Draw setting up players
            draw_text('Setting up player {}'.format(self.current_player), screen, True, 1500)
            all_sounds[self.current_player-1].set_volume(1)
            
            progress += 1
            
        # Setting the player controls
        elif progress == 3:
            self.players[self.current_player].set_controls(all_events)
            if len(self.players[self.current_player].controls) == 4:
                if self.current_player < self.number_of_players:
                    self.current_player += 1
                    # Draw setting up players and turn on player's sound
                    if all_sounds[self.current_player-1].get_volume() != 1:
                        all_sounds[self.current_player-1].set_volume(1)
                        # Turning off previous player's sound
                        all_sounds[self.current_player-2].set_volume(0)
                    draw_text('Setting up player {}'.format(self.current_player), screen, True, 1500)
                else:
                    self.current_player = 1
                    progress += 1
        
        # Final Player spawning in the field            
        elif progress == 4:
            screen.fill(WHITE)
            self.restart_round()
        
        return progress
    
    
    def update_death_array(self):
        """
        Determining what would be a lethal position in the playfield.
        
        The death array has some decay time in previously occupied pixels 
        to prevent suicide upon making tight corners. All values with a 1
        are actually lethal.
        """
        # Obtaining the currently drawed pixels
        screen_raw = pygame.surfarray.pixels2d(screen)
        screen_array = np.reshape(screen_raw, (size[0], size[1]))
        # Adding all non previously touched pixels to the death array
        self.death_array[(self.death_array == 0) & 
                         (screen_array != 16777215)] = self.death_tolerance
        self.death_array[self.death_array > 1] -= 1
    
    
    def game_loop(self, COUNTER):
        """
        Running a round in the playfield.
        """
        # Handling player movement
        game.update_death_array()
        for player in game.players:
            game.players[player].update(game.death_array)
    
        # End game?
        # box and chopping the players in groups of three.
        if not game.immortal:
            players_alive = 0
            for player in game.players:
                if game.players[player].alive:
                    players_alive += 1
            if players_alive == 1 and len(game.players) > 1:
                for player in game.players:
                    if game.players[player].alive:
                        game.score[player] += 1
                        score_message = ['','','']
                        for player_id in game.players:
                            score_message[(player_id-1) // 3 ] += '     Player {}: {}'.format(player_id, game.score[player_id])
                        draw_text("Player {} won!".format(player), 
                                  screen, 
                                  refresh = False,
                                  duration = 0,
                                  x_offset = 0,
                                  y_offset = -100,
                                  )
                        for position in range(0, 6):
                            if position < 3:
                                draw_text(score_message[position],
                                          screen,
                                          refresh = False,
                                          duration = 0,
                                          x_offset = 0,
                                          y_offset = position*50 + 50,
                                          )
                            if position == 3:
                                draw_text(
                                        '"BACKSPACE" new round',
                                        screen,
                                        refresh = False,
                                        duration = 0,
                                        x_offset = 0,
                                        y_offset = position*50 + 50,
                                        )
                            if position == 4:
                                draw_text(
                                        '"HOME" start menu',
                                        screen,
                                        refresh = False,
                                        duration = 0,
                                        x_offset = 0,
                                        y_offset = position*50 + 50,
                                        )
                            if position == 5:
                                draw_text(
                                        '"ESCAPE" quit',
                                        screen,
                                        refresh = False,
                                        duration = 0,
                                        x_offset = 0,
                                        y_offset = position*50 + 50,
                                        )
                        game.immortal = True  
        self.clock.tick(self.FPS+(COUNTER//self.FPS))
    
    
    def restart_round(self):
        """
        Restarts are round with the current amount of players and score
        preserved.
        """
        screen.fill(WHITE)
        self.immortal = False
        self.restart = False
        self.progress = 0
        self.init = False
        global COUNTER
        COUNTER = 0
        for player in self.players:
            # Random color is a feature, white is invisibraH!!!
            self.players[player].color = (int(random.random()*256), 
                                          int(random.random()*256), 
                                          int(random.random()*256),
                                          )
            self.players[player].alive = True
            self.players[player].not_drawing = 0
            self.players[player].old_x = self.players[player].x
            self.players[player].old_y = self.players[player].y
            self.death_array[:] = 0
            all_sounds[player-1].set_volume(0)
    

def draw_text(message, layer, refresh = True, duration = 1000, 
              x_offset = 0, y_offset = 0):
    """
    Basic function to draw text into the playfield.
    """
    if refresh:
        screen.fill(WHITE)
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(message, True, BLACK, WHITE) 
    textRect = text.get_rect()
    textRect.center = (size[0] // 2 + x_offset, size[1] // 2 + y_offset)
    layer.blit(text, textRect)
    pygame.display.update()
    pygame.time.wait(duration)
        

def handling_input(clear = False):
    """
    Handles the basic input for the whole game. Updating the buffered and 
    unbuffered input, as well as possible termination of the program using
    DONE. Clear will drain the current queue.
    """
    # All events but buffered since last call
    all_events = pygame.event.get()
    # All keys being pressed 
    pressed_keys = pygame.key.get_pressed()
    DONE = False
    for event in all_events:
        if event.type == pygame.QUIT:
            DONE = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                DONE = True
            elif event.key == pygame.K_BACKSPACE:
                if not game.init:
                    game.restart = True
            elif event.key == pygame.K_HOME:
                game.init = True
                game.progress = 0
                game.current_player = 1
                # randomize the music!
                random.shuffle(all_sounds)
                #game.restart = True
    if clear:
        all_events = pygame.event.clear()
    
    return all_events, pressed_keys, DONE 




# --------- Starting the real game implementation ---------
### These vairables can be altered for desired gameplay
# Set initiation
FPS = 60

# These guys are implemented in a very dirty way and just go to global 
#  namespace...
COUNTER = 0
INTRO = True
# Initial immortality period in a round
FREE_TIME = 1.5
# Define movement speed
SPEED = 4
HYPER_DRAWING = SPEED
# Define line thickness
THICKNESS = SPEED // 2 + 1
# Gap size
GAP = 8
GAP_FREQ = 0.5


### Some basic bookkeeping and initiation of things
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# start the game engine
pygame.init()

# start the music
all_sounds = initiate_music()

# Set the width and height of the screen [width, height]
size = (1920, 1080)
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
pygame.display.set_caption("Pencil Panic!")


# Loop until the user clicks the close button.
DONE = False

### Yhea finally we get going :D
# -------- Main Program Loop -----------
game = Game(FPS)
while not DONE:
    # --- Main event loop
    # Updating the buffered and unbuffered input
    all_events, pressed_keys, DONE = handling_input()

    # Start the game and intro
    if INTRO and not DONE:
        game.intro_menu()
        INTRO = False
        all_events, _, _ = handling_input(clear=True)
    
    # Initiating a new game and setting players
    if game.init and not DONE:
        game.progress = game.new_game(all_events, game.progress)
    
    # Running the main game loop
    if not game.init and not DONE:    
        game.game_loop(COUNTER)
    
    # Starting a new round
    if game.restart and not DONE:
        game.restart_round()
    
    # Pushing our frame buffer to display         
    pygame.display.update()
 
    # Iterating the frame counter for use in some logic
    COUNTER += 1
    
# Close the window and quit.
pygame.quit()