import pygame

# inicializamos pygame
pygame.init()

# muestro una ventana 800x600
size = 800, 600
screen = pygame.display.set_mode(size)

# cambio el titulo de la ventana
pygame.display.set_caption("Juego BALL")

# inicializamos variables
width, height = 800, 600
speed = [1, 1]
white = 255, 255, 255

# crea un objeto imagen y obtengo su rectangulo
ball = pygame.image.load("ball.png")
ballrect = ball.get_rect()

# comenzamos con el bucle del juego
run = True

while run:
    # Espero un tiempo (milisegundos) para que la pelota no vaya muy rapida
    pygame.time.delay(2)

    # capturamos los eventos que se han producido
    for event in pygame.event.get():

        # si el evento es salir de la ventana, terminamos
        if event.type == pygame.QUIT: run = False



    #detecto limites verticales y cambio direccion
    if ballrect.right > width - 0 or ballrect.left < 0:
        speed[0] = -speed[0]

    #detecto limites horizontales y cambio direccion
    if ballrect.bottom > height - 0 or ballrect.top < 0:
        speed[1] = -speed[1]

    # Muevo la pelota
    ballrect = ballrect.move(speed)

    # pinto el fondo de blanco, dibujo la pelota y actualizo la pantalla
    screen.fill(white)
    screen.blit(ball, ballrect)
    pygame.display.flip()

# salgo de pygame
pygame.quit()
