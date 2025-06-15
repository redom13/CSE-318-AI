import pygame

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BG_COLOR = (30, 30, 30)
PLAYER_SPEED = 5 # Define player speed
FPS = 60  # Frames per second

# Creating the Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # It takes a tuple of width and height

# Bg 
bgImage = pygame.image.load('bg.png')  # Load your background image

# Title and icon
pygame.display.set_caption("Space Invaders")
try:
    icon = pygame.image.load('spaceship.png')  # Load your icon image
    pygame.display.set_icon(icon)
except pygame.error as e:
    print(f"Error loading icon: {e}")

# Player
player_img = pygame.image.load('space-invaders.png')  # Load your player image
player_width = player_img.get_width()
player_height = player_img.get_height()
playerX = 370  # Initial X position
playerY = 480  # Initial Y position

def player(x, y):
    screen.blit(player_img, (x, y))  # Draw the player image at the specified position

# Player movement functionality (no longer used for direct event handling)
# def move(event):
#     global playerX, playerY
#     if event.key == pygame.K_LEFT and playerX > 0:
#         playerX -= 5  # Move left
#     elif event.key == pygame.K_RIGHT and playerX < WIDTH - 64: # Assuming player width is 64
#         playerX += 5  # Move right
#     elif event.key == pygame.K_UP and playerY > 0:
#         playerY -= 5  # Move up
#     elif event.key == pygame.K_DOWN and playerY < HEIGHT - 64: # Assuming player height is 64
#         playerY += 5  # Move down
        

running = True
clock = pygame.time.Clock()  # Create a clock object to control the frame rate

while running:
    # screen.fill(BG_COLOR)  # Fill the screen with the background color
    screen.blit(bgImage, (0, 0))  # Draw the background image
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # We don't need to handle KEYDOWN for movement here anymore
        # elif event.type == pygame.KEYDOWN:
        #     move(event) 

    # Get the state of all keyboard keys
    keys = pygame.key.get_pressed()
    
    # Continuous movement logic
    if keys[pygame.K_LEFT] and playerX > 0:
        playerX -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] and playerX < WIDTH - player_width:
        playerX += PLAYER_SPEED
    if keys[pygame.K_UP] and playerY > 0:
        playerY -= PLAYER_SPEED
    if keys[pygame.K_DOWN] and playerY < HEIGHT - player_height:
        playerY += PLAYER_SPEED
    
    player(playerX, playerY)  # Draw the player
    pygame.display.flip()  # Update the display

    clock.tick(FPS)  # Control the frame rate

pygame.quit()