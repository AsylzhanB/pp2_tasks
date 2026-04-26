import pygame
from ball import Ball

pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball Game")

WHITE = (255, 255, 255)

ball = Ball(WIDTH // 2, HEIGHT // 2, 25, WIDTH, HEIGHT)

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        ball.move(0, -ball.speed)
    if keys[pygame.K_s]:
        ball.move(0, ball.speed)
    if keys[pygame.K_a]:
        ball.move(-ball.speed, 0)
    if keys[pygame.K_d]:
        ball.move(ball.speed, 0)
    if keys[pygame.K_UP]:
        ball.move(0, -ball.speed)
    if keys[pygame.K_DOWN]:
        ball.move(0, ball.speed)
    if keys[pygame.K_LEFT]:
        ball.move(-ball.speed, 0)
    if keys[pygame.K_RIGHT]:
        ball.move(ball.speed, 0)

    screen.fill(WHITE)
    ball.draw(screen)

    pygame.display.flip()

pygame.quit()