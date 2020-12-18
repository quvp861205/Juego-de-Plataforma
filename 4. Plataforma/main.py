import pygame
from pygame.locals import *

pygame.init()

# limitar la cuadros por segundo
clock = pygame.time.Clock()
fps = 60

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

# clase para administrar al jugador
class Player():
    #carga la imagen del jugador
    def __init__(self, x, y):
        self.images_right = []  # arreglo para imagenes monito caminando derecha
        self.images_left = []  # arreglo para imagenes monito caminando izquierda
        self.index = 0
        self.counter = 0
        
        # llenamos el arreglo con imagenes caminando
        for num in range(1,5):
            print( 'assets/guy'+str(num)+'.png')
            img_right = pygame.image.load('assets/guy'+str(num)+'.png')
            img_right = pygame.transform.scale(img_right, (40,80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        
        self.image = self.images_right[self.index]

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0  #velocidad del salto
        self.jumped = False  # el jugador esta brincnado?
        self.direction = 0 # direccion del jugador izquierda o derecha

    # funcion: controla el jugador y lo dibuja
    def update(self):
        
        # variables para el movimiento
        dx = 0
        dy = 0
        walk_cooldown = 5  # cada 5 ciclos va cambiar animacion el jugador
        
        #controlamos al jugador
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and self.jumped==False: # tecla espacio para salto
            self.vel_y = -15
            self.jumped = True
        if key[pygame.K_LEFT]:  # tecla izquierda presionada
            dx -= 5
            self.counter += 1   # aumentamos para generar animacion
            self.direction = -1   # cambiamos de direccion
        
        if key[pygame.K_RIGHT]: # tecla derecha presionada
            dx += 5
            self.counter += 1   # aumentamos para generar animacion
            self.direction = 1   # cambiamos de direccion
            
        if key[pygame.K_RIGHT]==False and key[pygame.K_LEFT]==False:  # si no presiona nada reiniciamos toda animacion
            self.counter = 0
            self.index = 0   
            if self.direction==1:
                self.image = self.images_right[self.index]
            if self.direction==-1:
                self.image = self.images_left[self.index]
            
        # manejo de animaciones
        if self.counter > walk_cooldown:  # hacemos mas lento la animacion
            self.counter = 0
            self.index += 1
            if self.index>=len(self.images_right):
                self.index = 0
            if self.direction==1:
                self.image = self.images_right[self.index]
            if self.direction==-1:
                self.image = self.images_left[self.index]
        
        #agregamos gravedad
        self.vel_y +=1 # gravedad
        if self.vel_y > 10: #limite velocidad salto
            self.vel_y = 10
        dy += self.vel_y
        
        #verificar colision
        
        #actualizar coordenadas de jugador
        self.rect.x += dx
        self.rect.y += dy
        
        #verificamos que el jugador tenga limite inferior que es la ventana
        if self.rect.bottom>screen_height:
            self.rect.bottom = screen_height
            dy = 0
            self.jumped = False
            
        screen.blit(self.image, self.rect)

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

# Creamos el objeto jugador
player = Player(100, screen_height-120)

run = True

while run==True:
    
    #limitamos a 60 ciclos por segundo
    clock.tick(fps)
    
    # pinta el fondo
    screen.blit(bg_img, (0, 0))
    
    # pinta el sol
    screen.blit(sun_img, (100, 100))
    
    # pinta los bloques de tierra
    world.draw()
    
    # pinta el grid
    draw_grid()
    
    # pinta al jugador
    player.update()
    
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run = False
    
    pygame.display.update()

pygame.quit()