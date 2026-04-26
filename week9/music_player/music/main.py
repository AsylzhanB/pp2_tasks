import pygame
import sys
from pp2_tasks.week9.music_player.music.player import MusicPlayer

pygame.init()

WIDTH, HEIGHT = 600, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")

font = pygame.font.SysFont(None, 36)

player = MusicPlayer("music")

clock = pygame.time.Clock()

while True:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_n:
                player.next_track()
            elif event.key == pygame.K_b:
                player.prev_track()
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    track_text = font.render("Track: " + player.get_current_track(), True, (255,255,255))
    screen.blit(track_text, (20, 50))

    status = "Playing" if player.is_playing else "Stopped"
    status_text = font.render("Status: " + status, True, (200,200,200))
    screen.blit(status_text, (20, 100))

    pygame.display.flip()
    clock.tick(30)