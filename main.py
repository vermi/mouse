import pygame
import random
from collections import deque
import io
import os

# Initialize Pygame
pygame.init()

# Load the mouse sprite
mouse_sprite = pygame.image.load("mouse.png")
cheese_sprite = pygame.image.load("cheese.png")
hedge_sprite = pygame.image.load("hedge.png")

# Load the chomp sound effect
chomp_sfx = pygame.mixer.Sound("chomp.mp3")

# Screen dimensions
SCREEN_WIDTH = 1500  # Default width to accommodate the maze and border
SCREEN_HEIGHT = 1200  # Default height to ensure equal borders
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Mono's Mouse Maze")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
SKY_BLUE = (135, 206, 235)

# Maze dimensions
MAZE_WIDTH = 20
MAZE_HEIGHT = 15

# Load 8-bit font
font_path = "daydream.ttf"  # Replace with the path to your 8-bit font file
font_size = 30
font = pygame.font.Font(font_path, font_size)
large_font = pygame.font.Font(font_path, font_size * 2)

# Function to play background music
def play_background_music():
    pygame.mixer.music.load("mouse.wav")
    pygame.mixer.music.play(-1)  # Loop the music

# Maze generation using Depth-First Search
def generate_maze(width, height):
    maze = [[1] * width for _ in range(height)]
    stack = [(0, 0)]
    visited = set((0, 0))

    while stack:
        x, y = stack[-1]
        maze[y][x] = 0
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                if sum(1 for dx2, dy2 in [(-1, 0), (1, 0), (0, -1), (0, 1)] if 0 <= nx + dx2 < width and 0 <= ny + dy2 < height and maze[ny + dy2][nx + dx2] == 0) <= 1:
                    neighbors.append((nx, ny))
        if neighbors:
            stack.append(random.choice(neighbors))
            visited.add(stack[-1])
        else:
            stack.pop()
    return maze

def place_cheese(maze):
    while True:
        cx, cy = random.randint(0, MAZE_WIDTH - 1), random.randint(0, MAZE_HEIGHT - 1)
        if maze[cy][cx] == 0 and (cx, cy) != (0, 0):
            return cx, cy

def place_exit(maze):
    boundaries = [(x, 0) for x in range(MAZE_WIDTH)] + [(x, MAZE_HEIGHT - 1) for x in range(MAZE_WIDTH)] + \
                 [(0, y) for y in range(MAZE_HEIGHT)] + [(MAZE_WIDTH - 1, y) for y in range(MAZE_HEIGHT)]
    random.shuffle(boundaries)
    for ex, ey in boundaries:
        if maze[ey][ex] == 0:
            return ex, ey
    return None

def is_solvable(maze, start, end):
    queue = deque([start])
    visited = set()
    while queue:
        x, y = queue.popleft()
        if (x, y) == end:
            return True
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and maze[ny][nx] == 0 and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))
    return False

def reset_level():
    global maze, mouse_x, mouse_y, cheese_x, cheese_y, exit_x, exit_y, level_score, start_ticks, alive, cheese_collected
    while True:
        maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
        mouse_x, mouse_y = 0, 0
        cheese_x, cheese_y = place_cheese(maze)
        exit_x, exit_y = place_exit(maze)
        if is_solvable(maze, (mouse_x, mouse_y), (exit_x, exit_y)):
            break
    level_score = 1000
    start_ticks = pygame.time.get_ticks()
    alive = True
    cheese_collected = False

def trigger_game_over():
    global alive, game_over_screen
    print("Game Over Triggered")
    alive = False
    game_over_screen = True
    print(f"alive: {alive}, game_over_screen: {game_over_screen}")
    pygame.display.flip()  # Force the display to update

def draw_start_screen():
    screen.fill(BLACK)
    title_text = large_font.render("Mono's Mouse Maze", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(title_text, title_rect)
    
    mouse_centered = pygame.transform.scale(mouse_sprite, (200, 200))
    screen.blit(mouse_centered, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100))
    
    play_text = large_font.render("PLAY GAME", True, WHITE)
    play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5))
    screen.blit(play_text, play_rect)
    
    arrow_text = large_font.render(">", True, WHITE)
    arrow_rect = arrow_text.get_rect(midright=(play_rect.left - 10, play_rect.centery))
    if pygame.time.get_ticks() // 500 % 2 == 0:
        screen.blit(arrow_text, arrow_rect)
    pygame.display.flip()

def draw_game_over_screen(selection):
    print("Drawing game over screen")  # Debugging statement
    screen.fill(BLACK)
    zoomed_mouse_sprite = pygame.transform.scale(mouse_sprite, (cell_size * 5, cell_size * 5))
    screen.blit(zoomed_mouse_sprite, ((SCREEN_WIDTH - cell_size * 5) // 2, (SCREEN_HEIGHT - cell_size * 5) // 2))
    
    game_over_text = large_font.render(f"Total Score: {total_score}", True, WHITE)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + cell_size * 4))
    screen.blit(game_over_text, game_over_rect)
    
    restart_color = SKY_BLUE if selection == "RESTART" else WHITE
    quit_color = SKY_BLUE if selection == "QUIT" else WHITE

    restart_text = font.render("RESTART", True, restart_color)
    quit_text = font.render("QUIT", True, quit_color)
    
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 1.2))
    quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 1.2))

    screen.blit(restart_text, restart_rect)
    screen.blit(quit_text, quit_rect)
    
    pygame.display.flip()
    return restart_rect, quit_rect

def draw_pause_menu(selection):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)  # Increase alpha for more opacity
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    menu_text = large_font.render("PAUSE MENU", True, WHITE)
    menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(menu_text, menu_rect)

    resume_color = SKY_BLUE if selection == "RESUME" else WHITE
    end_color = SKY_BLUE if selection == "END GAME" else WHITE

    resume_text = font.render("RESUME", True, resume_color)
    end_text = font.render("END GAME", True, end_color)

    resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    end_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    screen.blit(resume_text, resume_rect)
    screen.blit(end_text, end_rect)

    pygame.display.flip()  # Ensure display is updated after drawing the pause menu

reset_level()
total_score = 0
direction = 'right'
level = 1
paused = False
alive = True
start_screen = True
game_over_screen = False
selection = "RESTART"
pause_menu_selection = "RESUME"  # Initialize the pause menu selection

# Start background music
play_background_music()

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)  # Background color outside the maze

    # Handle resizing
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    cell_size = min((SCREEN_WIDTH - 400) // MAZE_WIDTH, (SCREEN_HEIGHT - 400) // MAZE_HEIGHT)
    offset_x = (SCREEN_WIDTH - MAZE_WIDTH * cell_size) // 2
    offset_y = (SCREEN_HEIGHT - MAZE_HEIGHT * cell_size) // 2
    scaled_mouse_sprite = pygame.transform.scale(mouse_sprite, (cell_size, cell_size))
    scaled_cheese_sprite = pygame.transform.scale(cheese_sprite, (cell_size, cell_size))
    scaled_hedge_sprite = pygame.transform.scale(hedge_sprite, (cell_size, cell_size))
    font = pygame.font.Font(font_path, font_size)

    # Event handling in the main game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and not start_screen and not game_over_screen:
                paused = not paused
                if paused:
                    pause_start_ticks = pygame.time.get_ticks()
                else:
                    # Adjust start_ticks to account for the pause duration
                    start_ticks += pygame.time.get_ticks() - pause_start_ticks
            elif paused:
                if event.key == pygame.K_q:
                    # End game when Q is pressed while paused
                    total_score += level_score  # Add current level score to total score
                    level_score = 0  # Set level score to 0 to trigger game over
                    trigger_game_over()
                    paused = False
                elif event.key == pygame.K_RETURN:
                    if pause_menu_selection == "RESUME":
                        paused = False
                        start_ticks += pygame.time.get_ticks() - pause_start_ticks
                    elif pause_menu_selection == "END GAME":
                        total_score += level_score  # Add current level score to total score
                        level_score = 0  # Set level score to 0 to trigger game over
                        trigger_game_over()
                        paused = False
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    pause_menu_selection = "RESUME" if pause_menu_selection == "END GAME" else "END GAME"
            if start_screen and event.key == pygame.K_RETURN:
                start_screen = False

    if start_screen:
        draw_start_screen()
    elif game_over_screen:
        print("Drawing game over screen")
        restart_rect, quit_rect = draw_game_over_screen(selection)
        pygame.display.flip()  # Ensure display is updated after drawing the game over screen
        # Only allow game over screen to process restart or quit
        while game_over_screen:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if selection == "RESTART":
                            reset_level()
                            total_score = 0
                            direction = 'right'
                            level = 1
                            paused = False
                            alive = True
                            game_over_screen = False
                        elif selection == "QUIT":
                            running = False
                            game_over_screen = False
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        selection = "RESTART" if selection == "QUIT" else "QUIT"
                draw_game_over_screen(selection)
                pygame.display.flip()
    elif not paused and alive:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and mouse_x > 0 and maze[mouse_y][mouse_x - 1] == 0:
            mouse_x -= 1
            direction = 'left'
        if keys[pygame.K_RIGHT] and mouse_x < MAZE_WIDTH - 1 and maze[mouse_y][mouse_x + 1] == 0:
            mouse_x += 1
            direction = 'right'
        if keys[pygame.K_UP] and mouse_y > 0 and maze[mouse_y - 1][mouse_x] == 0:
            mouse_y -= 1
        if keys[pygame.K_DOWN] and mouse_y < MAZE_HEIGHT - 1 and maze[mouse_y + 1][mouse_x] == 0:
            mouse_y += 1

        # Decrease score over time
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
        level_score = max(1000 - int(elapsed_time) * 10, 0)
        if level_score == 0:
            trigger_game_over()

        # Check for cheese collection
        if not cheese_collected and mouse_x == cheese_x and mouse_y == cheese_y:
            total_score += 250
            cheese_collected = True
            chomp_sfx.play()  # Play the chomp sound effect

        # Check for exit
        if mouse_x == exit_x and mouse_y == exit_y:
            total_score += level_score
            level += 1
            reset_level()

    if alive and not start_screen and not game_over_screen:
        # Draw maze
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                if maze[y][x] == 0:
                    pygame.draw.rect(screen, WHITE, (x * cell_size + offset_x, y * cell_size + offset_y, cell_size, cell_size))
                else:
                    screen.blit(scaled_hedge_sprite, (x * cell_size + offset_x, y * cell_size + offset_y))

        # Draw mouse with direction
        if direction == 'left':
            flipped_mouse_sprite = pygame.transform.flip(scaled_mouse_sprite, True, False)
            screen.blit(flipped_mouse_sprite, (mouse_x * cell_size + offset_x, mouse_y * cell_size + offset_y))
        else:
            screen.blit(scaled_mouse_sprite, (mouse_x * cell_size + offset_x, mouse_y * cell_size + offset_y))

        # Draw cheese
        if not cheese_collected:
            screen.blit(scaled_cheese_sprite, (cheese_x * cell_size + offset_x, cheese_y * cell_size + offset_y))

        # Draw the exit as a red X
        exit_text = font.render("X", True, RED)
        screen.blit(exit_text, (exit_x * cell_size + offset_x + 10, exit_y * cell_size + offset_y + 10))

        # Update and draw score
        score_text = font.render(f"Level Score: {level_score}", True, WHITE)
        total_score_text = font.render(f"Total Score: {total_score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(total_score_text, (10, 50))

        paused_flash = pygame.time.get_ticks() // 500 % 2  # Flashing "PAUSED" text control
        if paused:
            draw_pause_menu(pause_menu_selection)
            if paused_flash == 0:
                paused_text = font.render("PAUSED", True, WHITE)
                paused_rect = paused_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
                screen.blit(paused_text, paused_rect)

    pygame.display.flip()
    clock.tick(10)  # Adjust the tick rate to control the sensitivity

pygame.quit()
