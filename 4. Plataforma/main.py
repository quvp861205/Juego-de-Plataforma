import pygame
from pygame.locals import *

pygame.init()

# ancho y alto de la ventana del juego
screen_width = 800
screen_height = 800

# tamaño de la cuadricula en pixeles
tile_size = 40

# creamos el objeto pantalla
screen = pygame.display.set_mode((screen_width, screen_height))

# inicializamos un titulo a la ventana
pygame.display.set_caption('Platformer')

# cargamos las imagenes del fondo de nubecitas y el sol
sun_img = pygame.image.load('assets/sun.png')
bg_img = pygame.image.load('assets/sky.png')

# pinta una cuadricula separado por "tile_size"
def draw_grid():

    for line in range(0, 20):
        #                          color linea  ,  punto incio       ,   punt final
        pygame.draw.line(screen, (255, 255, 255), (0, line*tile_size), (screen_width, line*tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line*tile_size, 0), (line*tile_size, screen_height))


# clase para pintar los assets del mapa
class World():

    # funcion: carga el bloque de tierra y recorre el "world_data", poniendo el bloque donde haya 1
    def __init__(self, data):
        self.tile_list = []
    
        dirt_img = pygame.image.load('assets/dirt.png')
        grass_img = pygame.image.load('assets/grass.png')
        
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                
                # si es 1 entonces es bloque de tierra
                if tile==1:
                
                    # adaptamos el tamaño del assets a la cuadricula
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    
                    # asignamos la ubicaion del assets
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    
                    # agregamos a la lista el objeto imagen ya configurado tamaño y posicion
                    self.tile_list.append(tile)
                
                # si es 2 es bloque pasto
                if tile==2:
                
                    # adaptamos el tamaño del assets a la cuadricula
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    
                    # asignamos la ubicaion del assets
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    
                    # agregamos a la lista el objeto imagen ya configurado tamaño y posicion
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1
    
    # funcion: pinta los bloques agregados en el constructor 
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            
        
            
# Mapa para indicar con 1 donde se va poner la imagen
world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1], 
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1], 
[1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1], 
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]


# Creamos el objeto mundo
world = World(world_data)

run = True

while run==True:
    
    # pinta el fondo
    screen.blit(bg_img, (0, 0))
    
    # pinta el sol
    screen.blit(sun_img, (100, 100))
    
    # pinta los bloques de tierra
    world.draw()
    
    # pinta el grid
    draw_grid()
    
    
    
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run = False
    
    pygame.display.update()

pygame.quit()