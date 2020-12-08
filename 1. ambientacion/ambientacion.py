import sys, pygame

#inicializamos pygame
pygame.init()

#muestro una ventana de 800x600
size = 800, 600

screen = pygame.display.set_mode(size)

#cambio el titulo de la ventana
pygame.display.set_caption("Juego Ball")

#comenzamos el buclo del juego
run = True

while run:
    #capturamos los eventos que se han producido
    for event in pygame.event.get():
        #si el evento es salir de la ventana, terminamos
        if event.type==pygame.QUIT: run = False
        
#salgo de pygame
pygame.quit();