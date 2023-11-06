import pygame, sys, random
from pygame import mixer

pygame.init()


def draw_floor():
    screen.blit(floor_surface, (floor_x, 450))
    screen.blit(floor_surface, (floor_x + SCREEN_WIDTH, 450))


def create_new_pipe():
    # renvoie un élément sélectionné au hasard dans la séquence spécifiée
    random_height = random.choice(pipe_height)                                               
    bottom_pipe = pipe_surface.get_rect(midtop=(360, random_height))
    # espace entre les pipes
    top_pipe = pipe_surface.get_rect(midbottom=(360, random_height - 160))                   
    return bottom_pipe, top_pipe


def move_pipe(pipes):
    global can_update_score
    for pipe in pipes:
        pipe.centerx -= 2

    visible_pipes = [pipe for pipe in pipes if pipe.right >= 0]
    if len(visible_pipes) < len(pipes):                                         
        can_update_score = True

    return visible_pipes


def draw_pipe(pipes):
    for pipe_rect in pipes:
        if pipe_rect.bottom >= SCREEN_HEIGHT:
            screen.blit(pipe_surface, pipe_rect)
        else:
            # False, True (flip sur x, flip sur y)
            flipped_pipe = pygame.transform.flip(pipe_surface, False, True)                    
            screen.blit(flipped_pipe, pipe_rect)


def game_over(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            game_collision_sound.play()
            game_collision_sound.set_volume(0.3)
            return False

        if bird_rect.top < 0 or bird_rect.bottom >= 450:
            game_collision_sound.play()
            game_collision_sound.set_volume(0.3)
            return False

    return True


def display_score():
    if is_playing:
        score_surface = game_font.render(str(score), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(score_surface, score_rect)

    else:
        score_surface = game_font.render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f"High Score: {high_score}", True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(SCREEN_WIDTH / 2, 412))
        screen.blit(high_score_surface, high_score_rect)


def update_score():
    global score, can_update_score, high_score                                              
    if len(pipe_list) > 0:
        for pipe in pipe_list:
            if pipe.centerx < bird_rect.centerx and can_update_score:
                score += 1
                game_point_sound.play()
                game_point_sound.set_volume(0.3)
                if score > high_score:
                    high_score = score
                    with open('data.txt', mode='w') as file:                                                        
                        file.write(str(high_score))

                can_update_score = False


def update_bird_image():
    global bird_index, bird_surface, bird_rect
    if bird_index < 2:
        bird_index += 1
    else:
        bird_index = 0

    bird_surface = bird_images[bird_index]
    y = bird_rect.centery                                                               
    bird_rect = bird_surface.get_rect(center=(100, y))

def rotate_bird(surface):
    rotated_bird_surface = pygame.transform.rotate(surface, - bird_movement * 5)
    return rotated_bird_surface

# VARIABLES
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
game_on = True
clock = pygame.time.Clock()
floor_x = 0
bird_movement = 0
gravity = 0.25
pipe_height = [200, 300, 400]
is_playing = False
score = 0
high_score = 0
# ferme automatiquement le fichier qd on ferme le jeux
with open('data.txt') as file:                                                      
    saved_score = file.read()
    high_score = int(saved_score)

game_font = pygame.font.Font('04B_19.TTF', 30)
can_update_score = True
bird_jump_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
game_point_sound = pygame.mixer.Sound('sound/sfx_point.wav')
game_collision_sound = pygame.mixer.Sound('sound/sfx_hit.wav')

# SURFACES
bg_surface = pygame.image.load('assets/background-day.png').convert()              
floor_surface = pygame.image.load('assets/base.png').convert()

bird_mid_surface = pygame.image.load('assets/yellowbird-midflap.png').convert()
bird_down_surface = pygame.image.load('assets/yellowbird-downflap.png').convert()
bird_top_surface = pygame.image.load('assets/yellowbird-upflap.png').convert()
bird_images = [bird_down_surface, bird_mid_surface, bird_top_surface]
bird_index = 0
bird_surface = bird_images[bird_index]
bird_rect = bird_surface.get_rect(center=(100, 225))

pipe_surface = pygame.image.load('assets/pipe-green.png').convert()
game_over_surface = pygame.image.load('assets/message.png').convert_alpha()             
game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
pipe_list = []
CREATEPIP = pygame.USEREVENT
# s'enclenche à 1300 millisecondes
pygame.time.set_timer(CREATEPIP, 1300)                                             
UPDATEBIRD = pygame.USEREVENT + 1                                                  
pygame.time.set_timer(UPDATEBIRD, 200)

pygame.display.set_caption("Bird")
windowIcon = pygame.image.load("assets/bird_icon.png")
pygame.display.set_icon(windowIcon)

# MUSIC
mixer.music.load("sound/061017funbgm.wav")
mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)

while game_on:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and is_playing == True:
                bird_movement = 0
                bird_movement -= 5
                bird_jump_sound.play()
                bird_jump_sound.set_volume(0.3)
            if event.key == pygame.K_SPACE and is_playing == False:
                is_playing = True

        if event.type == CREATEPIP:
            pipe_list.extend(create_new_pipe())                                    

        if event.type == UPDATEBIRD:
            update_bird_image()

    screen.blit(bg_surface, (0, 0))

    if is_playing:
        # PIPES
        pipe_list = move_pipe(pipe_list)
        draw_pipe(pipe_list)

        # BIRD
        rotated_bird = rotate_bird(bird_surface)
        screen.blit(rotated_bird, bird_rect)
        bird_movement = bird_movement + gravity
        bird_rect.centery += bird_movement

        is_playing = game_over(pipe_list)
        update_score()

    else:
        pipe_list.clear()
        bird_movement = 0
        bird_rect.center = (100, 225)
        score = 0
        can_update_score = True
        screen.blit(game_over_surface, game_over_rect)

    display_score()

    # FLOORS
    draw_floor()
    floor_x -= 1
    if floor_x <= -SCREEN_WIDTH:
        floor_x = 0

    pygame.display.update()
    clock.tick(60)
