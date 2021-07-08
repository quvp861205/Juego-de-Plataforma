import pygame
from pygame.locals import *
from pygame import mixer

import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512) # manejo del sonido
mixer.init()  # manejo del sonido
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
main_menu = True
level = 0 # nivel al que vamos a jugar
max_levels = 7
score = 0 # puntuacion

# creamos el objeto pantalla
screen = pygame.display.set_mode((screen_width, screen_height))

# inicializamos un titulo a la ventana
pygame.display.set_caption('Platformer')

# tipo de letra y color para la puntuacion
font_score = pygame.font.SysFont('Bauhaus 93', 30)
white = (255,255,255)

# tipo de fuente para los mensajes del juego
font = pygame.font.SysFont('Bauhaus 93', 70)
blue = (0, 0, 255)

# cargamos las imagenes del fondo de nubecitas y el sol
sun_img = pygame.image.load('assets/sun.png')
bg_img = pygame.image.load('assets/sky.png')
restart_img = pygame.image.load('assets/restart_btn.png')  # reiniciar el juego
start_img = pygame.image.load('assets/start_btn.png') # iniciar por primera vez
exit_img = pygame.image.load('assets/exit_btn.png') # salir del juego

# funcion para producir los sonidos
pygame.mixer.music.load('assets/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('assets/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('assets/jump.wav')
jump_fx.set_volume(0.5)
gameover_fx = pygame.mixer.Sound('assets/game_over.wav')
gameover_fx.set_volume(0.5)

# funcion para pintal el score
def draw_text( text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# permite inicializar un nivel incluye ambiente, enemigos, jugador, etc
def reset_level(level):
    player.reset(100, screen_height-200)
    blob_group.empty()
    platform_group.empty()
    lava_group.empty()
    exit_group.empty()
    coin_group.empty()
    
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    
    return world
    

# clase para agregar botones
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
        
    def draw(self):
        action = False
        
        # obtenemos posicion del mouse
        pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos): # verificamos si esta sobre el boton
            if pygame.mouse.get_pressed()[0]==1 and self.clicked is False: # verificamos si hace click izquierdo
                self.clicked = True
                action = True
        
        if pygame.mouse.get_pressed()[0]==0: # Soltar el click
            self.clicked = False
        
        #pintamos el boton
        screen.blit(self.image, self.rect) 
        
        return action
        

# clase para administrar al jugador
class Player():
    #carga la imagen del jugador
    def __init__(self, x, y):
        self.reset(x, y) # inicializamos parametros del monito

    # funcion: controla el jugador y lo dibuja
    def update(self, game_over):
        
        # variables para el movimiento
        dx = 0 #desplazamiento en x
        dy = 0 #desplazamiento en y
        walk_cooldown = 5  # cada 5 ciclos va cambiar animacion el jugador
        col_thresh = 20 # se utiliza para la colision con la plataforma
        
        # 0 es seguir jugando
        if game_over==0:
        
            #controlamos al jugador
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped==False and self.in_air==False: # tecla espacio para salto, in_air evita que salte multiple veces
                jump_fx.play()
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
            self.in_air = True
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
                        self.in_air = False
            
            #verificar colision con enemigos
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                gameover_fx.play()
            
            #verificar colision con lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1 
                gameover_fx.play()

            #verificar colision con puertas de salida
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1 # pasa al siguiente nivel
            
            #verificar colision con plataformas
            for platform in platform_group:
                #colision en direccion x con plataforma
                if platform.rect.colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
                    dx = 0 # detenemos movimiento en x
                
                #colision en direccio y con plataforma
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #verficar si hay contacto debajo de la plataforma
                    if abs(( self.rect.top + dy ) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0 # le quita la velocidad del salto                        
                        
                        dy = platform.rect.bottom - self.rect.top + 1
                        
                        # valida que la plataforma no vaya aplastar al jugador en caso que baje mucho
                        if platform.rect.bottom > (tile_size+self.height):
                            dy = 0       
                        
                    #verificar si hay contacto arriba de la plataforma
                    elif abs( (self.rect.bottom+dy) - platform.rect.top ) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1 #-1 para que no se atore en las esquinas de la plataforma
                        dy = 0
                        self.in_air = False
                   
                    #moverse junto con la plataforma
                    if platform.move_x != 0: # moverse en el eje x
                        self.rect.x += platform.move_direction
                   
                   
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
        #pygame.draw.rect(screen, (255,255,255), self.rect, 2)
        
        return game_over
        
    # reiniciamos los parametros dl jugador porque perdio
    def reset(self, x, y):
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
        self.jumped = False  # el jugador esta brincando?, para que tenga que soltar y presionar la tecla espacio
        self.direction = 0 # direccion del jugador izquierda o derecha
        self.in_air = True # esta brincando?, para que no haga saltos en el aire
        
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
                
                # si es 4 es bloque plataforma movil
                if tile==4:
                    platform = Platform(col_count*tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                
                # si es 5 es bloque plataforma movil
                if tile==5:
                    platform = Platform(col_count*tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform) 
                
                
                 # si es 6 es bloque de lava
                if tile==6:
                    lava = Lava(col_count*tile_size+20, row_count * tile_size+(tile_size))
                    lava_group.add(lava) #agregamos al grupo el bloque lava
                
                # si es 7 es bloque de moneda
                if tile==7:
                    coin = Coin(col_count*tile_size + (tile_size//2), row_count * tile_size+(tile_size//2) )
                    coin_group.add(coin) #agregamos al grupo el bloque coin
                    
                # si es 8 entonces es una puerta de salida de la mision
                if tile==8:
                    exit = Exit(col_count*tile_size, row_count * tile_size - (tile_size//2))
                    exit_group.add(exit)
                    
                col_count += 1
            row_count += 1
    
    # funcion: pinta los bloques agregados en el constructor 
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #pone un marco blanco alrededor de cada bloque de colision
            # pygame.draw.rect(screen, (255,255,255), tile[1], 2)
            
            
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

# clase para la plataforma movil y fija
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assets/platform.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0 # contador para limitar el movmiento
        self.move_counter = 0 # contador para limitar el movmiento
        self.move_direction = 1 # indica hacia que direccion se va mover
        self.move_x = move_x # indica si se va mover horizontalmente
        self.move_y = move_y # indica si se va mover verticalmente
        
    # actualizar comportamiento de la plataforma
    def update(self):
        self.rect.x += self.move_direction * self.move_x #movemos la plataforma horizontalmente 
        self.rect.y += self.move_direction * self.move_y #movemos la plataforma verticalmente
        self.move_counter += 1  #contamos que tanto se ha movido
        if abs(self.move_counter)>50: # cada 50 movimientos cambia direccion 
            self.move_direction *= -1  #cambiamos direccion
            self.move_counter *=  -1
        
        
# clase para la lava
class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assets/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


# clase para las monedas
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assets/coin.png')
        self.image = pygame.transform.scale(img, (tile_size//2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# clase que pinta una puerta para salir de la mision
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assets/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size*1.5)))
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

# grupo de puntos
coin_group = pygame.sprite.Group()

# creamos un arreglo para enemigos
blob_group = pygame.sprite.Group()

# creamos un arreglo para plataformas moviles
platform_group = pygame.sprite.Group()


# creamos un grupo de puertas para pasar al siguiente mision
exit_group = pygame.sprite.Group()

# se agrega un a moneda a un lado del texto de la puntuacion
score_coin = Coin(tile_size//2-10, tile_size//2)
coin_group.add(score_coin)

# Cargamos el nivel y creamos el mundo
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# botones para el juego
restart_button = Button(screen_width//2-50, screen_height//2+100, restart_img)
start_button = Button(screen_width//2-300, screen_height//2+100, start_img)
exit_button = Button(screen_width//2+50, screen_height//2+100, exit_img)


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
    
    
    # Validar si va mostrar el menu o el juego
    if main_menu==True: # carga los botones de inicio
        if exit_button.draw()==True:
            run = False
        if start_button.draw()==True:
            main_menu = False
    
    else: # empieza el juego        
    
        # pinta los bloques de tierra
        world.draw()
            
        if game_over==0: # actualizamos comportamientos cuando no haya gameover
            blob_group.update() # actualizamos movimiento enemigos
            platform_group.update() # actualiamos comportamiento plataformas
            
            # veficamos colisiones con las monedas, si las hay, las destruye e incrementamos la puntuacion
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text('X ' + str(score), font_score, white, tile_size-10, 10)
            
        # pintamos al grupo de enemigos
        blob_group.draw(screen)
        
        # pintamos el grupo de plataformas moviles
        platform_group.draw(screen)
        
        # pintamos la lava
        lava_group.draw(screen)
        
        # pintamos las monedas
        coin_group.draw(screen)
        
        # pintamos la puerta de salida de la mision
        exit_group.draw(screen)
        
        # pinta al jugador
        game_over = player.update(game_over)
        
           
         # si hay game_over ha muerto el jugador
        if game_over==-1:
            draw_text('GAME OVER', font, blue, (screen_width//2)-150, screen_height//2)
            if restart_button.draw(): # usuario hizo click en boton restart
                level = 0 # hacemos que si muere vuelva a empezar desde el primer nivel
                world_data = []
                world = reset_level(level) # permite inicializar un nivel incluye ambiente, enemigos, jugador, etc
                game_over = 0
                score = 0 # reiniciamos puntuacion
                
        
        # jugador ha completado nivel
        if game_over==1: 
            level += 1
            if level <= max_levels: # si hay siguiente nivel
                # reset level
                world_data = []
                world = reset_level(level) # permite inicializar un nivel incluye ambiente, enemigos, jugador, etc
                game_over = 0
            else: 
                draw_text("¡¡¡ TU HAZ GANADO !!!", font, blue, (screen_width//2)-200, screen_height//2)
                # reiniciar el juego otra vez cuando se pasan todos los niveles
                if restart_button.draw():
                    level = 0
                    world_data = []
                    world = reset_level(level) # permite inicializar un nivel incluye ambiente, enemigos, jugador, etc
                    game_over = 0
                    score = 0 # reiniciamos puntuacion ya que acabaron los niveles
    
    # evento para cerrar la aplicacion del juego
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run = False
    
    pygame.display.update()

pygame.quit()
