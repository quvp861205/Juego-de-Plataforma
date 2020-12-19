import pygame
from pygame.locals import *

pygame.init()

# limitar la cuadros por segundo
clock = pygame.time.Clock()
fps = 60

# ancho y alto de la ventana del juego
screen_width = 800
screen_height = 800

# variables del juego
tile_size = 40 # tamaño de la cuadricula en pixeles
game_over = 0 # marca si es gameover

# creamos el objeto pantalla
screen = pygame.display.set_mode((screen_width, screen_height))

# inicializamos un titulo a la ventana
pygame.display.set_caption('Platformer')

# cargamos las imagenes del fondo de nubecitas y el sol
sun_img = pygame.image.load('assets/sun.png')
bg_img = pygame.image.load('assets/sky.png')


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
            img_right = pygame.image.load('assets/guy'+str(num)+'.png')
            img_right = pygame.transform.scale(img_right, (40,80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        
        #cargamos imagen de la muerte
        self.dead_image = pygame.image.load('assets/ghost.png') 
        
        # configuramos la imagen del jugador
        self.image = self.images_right[self.index] 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0  #velocidad del salto
        self.jumped = False  # el jugador esta brincnado?
        self.direction = 0 # direccion del jugador izquierda o derecha

    # funcion: controla el jugador y lo dibuja
    def update(self, game_over):
        
        # variables para el movimiento
        dx = 0 #desplazamiento en x
        dy = 0 #desplazamiento en y
        walk_cooldown = 5  # cada 5 ciclos va cambiar animacion el jugador
        
        # 0 es seguir jugando
        if game_over==0:
        
            #controlamos al jugador
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped==False: # tecla espacio para salto
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE]==False: # si no se esta presionando se puede volver a brinbcar
                self.jumped = False
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
            
            #verificar colision con el mundo
            for tile in world.tile_list:
                #verificar colision en x
                if tile[1].colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
                    dx = 0
                #verificar colision en y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #verificar si hay terreno en la parte de debajo brincando
                    if self.vel_y<0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #verificar si hay terreno en la parte de arriba cayendo
                    elif self.vel_y>=0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
            
            #verificar colision con enemigos
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
            
            #verificar colision con lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1            
                
            #actualizar coordenadas de jugador
            self.rect.x += dx
            self.rect.y += dy
            
            #verificamos que el jugador tenga limite inferior que es la ventana
            if self.rect.bottom>screen_height:
                self.rect.bottom = screen_height
                dy = 0
        
        elif game_over==-1:   # si jugador perdio
            self.image = self.dead_image # asignamos imagen de fantasma a jugador
            if self.rect.y>200:  #mientras la posicion sea menor a 200
                self.rect.y -= 5 # subimos a fantasma
        
        #pinta al jugador en pantalla
        screen.blit(self.image, self.rect)        
        #pone un marco blanco alrededor del monito
        pygame.draw.rect(screen, (255,255,255), self.rect, 2)
        
        return game_over
        

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
                    
                # si es 3 es bloque enemigo
                if tile==3:
                    blob = Enemy(col_count*tile_size, row_count * tile_size +5)
                    blob_group.add(blob) #agregamos al grupo el enemigo
                    
                 # si es 6 es bloque de lava
                if tile==6:
                    lava = Lava(col_count*tile_size, row_count * tile_size+(tile_size//2))
                    lava_group.add(lava) #agregamos al grupo el bloque lava
                    
                col_count += 1
            row_count += 1
    
    # funcion: pinta los bloques agregados en el constructor 
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #pone un marco blanco alrededor de cada bloque de colision
            pygame.draw.rect(screen, (255,255,255), tile[1], 2)
            
            
# clase para el comportamiento de los enemigos
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        
    # actualizar comportamiento enemigos
    def update(self):
        self.rect.x += self.move_direction #movemos al enemigo
        self.move_counter += 1  #contamos que tanto se ha movido
        if abs(self.move_counter)>50: # cada 50 movimientos cambia direccion 
            self.move_direction *= -1  #cambiamos direccion
            self.move_counter *=  -1  
        

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assets/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        
            
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

# grupo para lavas
lava_group = pygame.sprite.Group()

# creamos un arreglo para enemigos
blob_group = pygame.sprite.Group()

# Creamos el objeto mundo
world = World(world_data)

# Creamos el objeto jugador
player = Player(100, screen_height-200)



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
        
    if game_over==0: # actualizamos enemigos si no hay game_over
        blob_group.update()
    # pintamos al grupo de enemigos
    blob_group.draw(screen)
    
    # pintamos la lava
    lava_group.draw(screen)
    
    # pinta al jugador
    game_over = player.update(game_over)
    
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run = False
    
    pygame.display.update()

pygame.quit()