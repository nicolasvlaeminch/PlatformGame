import pygame
from constantes import *
import sqlite3

tierra_imagen = pygame.image.load('Juego Plataforma\img\dirt.png')
cesped_imagen = pygame.image.load('Juego Plataforma\img\grass.png')

tierra_tamano = pygame.transform.scale(tierra_imagen, (CASILLA_TAMANO, CASILLA_TAMANO))
cesped_tamano = pygame.transform.scale(cesped_imagen, (CASILLA_TAMANO, CASILLA_TAMANO))
screen = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))

# Recargar el nivel correspondiente.
def cargar_nivel(nivel:int):
    enemigos_grupo.empty()
    lavas_grupo.empty()
    salida_grupo.empty()
    monedas_grupo.empty()

    if nivel == 1:
        mundo = Mundo(COORDENADAS_MUNDO_1)
    elif nivel == 2:
        mundo = Mundo(COORDENADAS_MUNDO_2)
    else:
        mundo = Mundo(COORDENADAS_MUNDO_3)

    return mundo

def dibujar_casillas():
	for linea in range(0, 20):
		pygame.draw.line(screen, COLOR_BLANCO, (0, linea * CASILLA_TAMANO), (ANCHO_VENTANA, linea * CASILLA_TAMANO))
		pygame.draw.line(screen, COLOR_BLANCO, (linea * CASILLA_TAMANO, 0), (linea * CASILLA_TAMANO, ALTO_VENTANA))

class Button():
	def __init__(self, x:int, y:int, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		# Dar posicion de mouse
		pos = pygame.mouse.get_pos()

		# Verifica las condiciones al pasar el mouse y hacer clic
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		# Dibuja el boton
		screen.blit(self.image, self.rect)

		return action

class Personaje():
    def __init__(self, x:int, y:int):
        self.reiniciar(x, y)

    def actualizar_personaje(self, game_over:int, mundo:list):
        dx = 0
        dy = 0
        cooldown_caminar = 5
        salto_sonido = pygame.mixer.Sound('Juego Plataforma\img\jump.wav')
        salto_sonido.set_volume(0.5)
        game_over_sonido = pygame.mixer.Sound('Juego Plataforma\img\game_over.wav')
        game_over_sonido.set_volume(0.5)

        if game_over == 0:
        # Tecla presionada
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.salto is False and self.flotando is False:
                salto_sonido.play()
                self.vel_y = -15
                self.salto = True
            if key[pygame.K_SPACE] is False:
                self.salto = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.contador += 1
                self.izquierda_o_derecha = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.contador += 1
                self.izquierda_o_derecha = 1
            if (key[pygame.K_LEFT] is False) and (key[pygame.K_RIGHT] is False):
                self.contador = 0
                self.index = 0
                if self.izquierda_o_derecha == 1:
                    self.imagen = self.imagenes_derecha[self.indice]
                if self.izquierda_o_derecha == -1:
                    self.imagen = self.imagenes_izquierda[self.indice]

            # Manejo de animacion
            if self.contador > cooldown_caminar:
                self.contador = 0
                self.indice += 1
                if self.indice >= len(self.imagenes_derecha):
                    self.indice = 0
                if self.izquierda_o_derecha == 1:
                    self.imagen = self.imagenes_derecha[self.indice]
                if self.izquierda_o_derecha == -1:
                    self.imagen = self.imagenes_izquierda[self.indice]


            # Agregar gravedad
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Comprueba si hay colisiones
            self.flotando = True

            for casilla in mundo.casilla_lista:
                # Comprueba si hay colisión en la direccion X.
                if casilla[1].colliderect(self.rect.x + dx, self.rect.y, self.ancho, self.alto):
                    dx = 0
                # Comprueba si hay colisión en la direccion Y.
                if casilla[1].colliderect(self.rect.x, self.rect.y + dy, self.ancho, self.alto):
                    # Verificar si está debajo del suelo, es decir, saltando.
                    if self.vel_y < 0:
                        dy = casilla[1].bottom - self.rect.top
                        self.vel_y = 0
                    # Verificar si está por encima del suelo, es decir, cayendo.
                    elif self.vel_y >= 0:
                        dy = casilla[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.flotando = False

        # VERIFICIAR COLICIONES DE OBJETOS EN EL JUEGO.
            # Verifica colision con enemigos
            if pygame.sprite.spritecollide(self, enemigos_grupo, False, pygame.sprite.collide_rect):
                game_over = -1
                game_over_sonido.play()
            # Verifica colision con la lava
            if pygame.sprite.spritecollide(self, lavas_grupo, False):
                game_over = -1
                game_over_sonido.play()
			# Verifica colision con la salida
            if pygame.sprite.spritecollide(self, salida_grupo, False):
                game_over = 1

            # Actualizar las coordenadas del jugador
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.imagen = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5

        # Dibuja el personaje en la pantalla.
        screen.blit(self.imagen, self.rect)
        # pygame.draw.rect(screen, COLOR_BLANCO, self.rect, 2)

        return game_over

    def reiniciar(self, x:int, y:int):
        self.imagenes_derecha = []
        self.imagenes_izquierda = []
        self.indice = 0
        self.contador = 0
        for num in range(1, 5):
            imagen_derecha = pygame.image.load(f'Juego Plataforma\img\guy{num}.png')
            imagen_derecha = pygame.transform.scale(imagen_derecha, (40, 80))
            imagen_izquierda = pygame.transform.flip(imagen_derecha, True, False)
            self.imagenes_derecha.append(imagen_derecha)
            self.imagenes_izquierda.append(imagen_izquierda)
        self.dead_image = pygame.image.load('Juego Plataforma\img\ghost.png')
        self.imagen = self.imagenes_derecha[self.indice]
        self.rect = self.imagen.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.ancho = self.imagen.get_width()
        self.alto = self.imagen.get_height()
        self.vel_y = 0
        self.salto = False
        self.izquierda_o_derecha = 0
        self.flotando = True


class Mundo():
    # Constructor de la clase Mundo
    def __init__(self, data):
        # Lista que almacenara información sobre cada casilla del mundo
        self.casilla_lista = []

        # Contadores para seguir la posición actual al recorrer la matriz 'data'
        contador_filas = 0
        for fila in data:
            contador_columnas = 0
            for casilla in fila:
                # Si la casilla es igual a 1, significa que hay tierra
                if casilla == 1:
                    # Crea un rectángulo imaginario para representar la posición de la casilla en la pantalla
                    tierra_posicion = tierra_tamano.get_rect()
                    tierra_posicion.x = contador_columnas * CASILLA_TAMANO
                    tierra_posicion.y = contador_filas * CASILLA_TAMANO
                    # Almacena la casilla como una lista en 'casilla_lista'
                    casilla = [tierra_tamano, tierra_posicion]
                    self.casilla_lista.append(casilla)
                if casilla == 2:
                    # Crea un rectángulo imaginario para representar la posición de la casilla en la pantalla
                    tierra_posicion = cesped_tamano.get_rect()
                    tierra_posicion.x = contador_columnas * CASILLA_TAMANO
                    tierra_posicion.y = contador_filas * CASILLA_TAMANO
                    # Almacena la casilla como una lista en 'casilla_lista'
                    casilla = [cesped_tamano, tierra_posicion]
                    self.casilla_lista.append(casilla)
                if casilla == 3:
                    enemigo = Enemigo(contador_columnas * CASILLA_TAMANO, contador_filas * CASILLA_TAMANO + 15)
                    enemigos_grupo.add(enemigo)
                if casilla == 6:
                    lava = Lava(contador_columnas * CASILLA_TAMANO, contador_filas * CASILLA_TAMANO + (CASILLA_TAMANO // 2))
                    lavas_grupo.add(lava)
                if casilla == 7:
                    moneda = Moneda(contador_columnas * CASILLA_TAMANO + (CASILLA_TAMANO // 2), contador_filas * CASILLA_TAMANO + (CASILLA_TAMANO // 2))
                    monedas_grupo.add(moneda)
                if casilla == 8:
                    salida = Salida(contador_columnas * CASILLA_TAMANO, contador_filas * CASILLA_TAMANO - (CASILLA_TAMANO // 2))
                    salida_grupo.add(salida)

                contador_columnas += 1
            contador_filas += 1

    # Metodo para dibujar las casillas en la pantalla
    def dibujar(self):
        for casilla in self.casilla_lista:
            # Dibuja la imagen de la tierra en la posición especificada por el rectángulo
            screen.blit(casilla[0], casilla[1])
            # Marca las casillas con un marco blanco
            # pygame.draw.rect(screen, COLOR_BLANCO, casilla[1], 2)

# Definir la clase Enemigo que hereda de pygame.sprite.Sprite
class Enemigo(pygame.sprite.Sprite):
	def __init__(self, x:int, y:int):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('Juego Plataforma\img\enemigo.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.direccion_movimiento = 1
		self.contador_movimiento = 0

	def update(self):
    # Se mueve en el eje X hasta alcanzar el limite y cambia de direccion.
		self.rect.x += self.direccion_movimiento
		self.contador_movimiento += 1
		if abs(self.contador_movimiento) > 50:
			self.direccion_movimiento *= -1
			self.contador_movimiento *= -1

# Definir la clase Lava que hereda de pygame.sprite.Sprite
class Lava(pygame.sprite.Sprite):
	def __init__(self, x:int , y:int):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('Juego Plataforma\img\lava.png')
		self.image = pygame.transform.scale(img, (CASILLA_TAMANO, CASILLA_TAMANO // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

# Definir la clase Salida que hereda de pygame.sprite.Sprite
class Salida(pygame.sprite.Sprite):
	def __init__(self, x:int, y:int):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('Juego Plataforma\img\exit.png')
		self.image = pygame.transform.scale(img, (CASILLA_TAMANO, int(CASILLA_TAMANO * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

# Definir la clase Moneda que hereda de pygame.sprite.Sprite
class Moneda(pygame.sprite.Sprite):
	def __init__(self, x:int, y:int):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('Juego Plataforma\img\coin.png')
		self.image = pygame.transform.scale(img, (CASILLA_TAMANO // 2, int(CASILLA_TAMANO // 2)))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)

enemigos_grupo = pygame.sprite.Group()
lavas_grupo = pygame.sprite.Group()
salida_grupo = pygame.sprite.Group()
monedas_grupo = pygame.sprite.Group()


def mostrar_ranking(archivo:str, pantalla):
    """
    Recibe la ruta del archivo y la pantalla en la que se va a imprimir.
    Esta funcion nos permite mostrar el ranking con los 10 mejores score ordenados de forma descendente.
    """

    with sqlite3.connect(archivo) as conexion:
            cursor = conexion.execute("SELECT * FROM Jugadores ORDER BY Score DESC LIMIT 10")

            encabezado = 'Nombre       Puntos'
            font_nombre = pygame.font.SysFont("Arial", TAMANO_FUENTE_ENCABEZADO) 
            texto_nombre = font_nombre.render(encabezado, True, COLOR_NARANJA)
            pantalla.blit(texto_nombre, (TEXTO_IZQUIERDO, TEXTO_SUPERIOR))

            for i, elemento in enumerate(cursor):
                font_nombre = pygame.font.SysFont("Arial", TAMANO_FUENTE)
                texto_nombre = font_nombre.render(str(elemento[1]), True, COLOR_NARANJA)
                pantalla.blit(texto_nombre, (TEXTO_IZQUIERDO, i * 60 + 250))

                font_puntos = pygame.font.SysFont("Arial", TAMANO_FUENTE)
                texto_puntos = font_puntos.render(str(elemento[2]), True, COLOR_NARANJA)
                pantalla.blit(texto_puntos, (TEXTO_IZQUIERDO * 2.5, i * 60 + 250))

def crear_tabla(archivo:str):
    """
    Recibe la ruta del archivo.
    Esta funcion nos permite crear la tabla en la que se almacenaran los datos del jugador (Nombre y Score).
    """


    with sqlite3.connect(archivo) as conexion:
            try:
                sentencia = ''' create  table Jugadores
                                (
                                    Id integer primary key autoincrement,
                                    Nombre text,
                                    Score real
                                )
                            '''
                conexion.execute(sentencia)
                print("Se creo la tabla Jugadores")                       
            except sqlite3.OperationalError:
                print("La tabla Jugadores ya existe")

def agregar_jugador(archivo:str, texto:str, score:float):
    """
    Recibe la ruta del archivo, nombre del jugador y puntuacion obtenida.
    Esta funcion nos permite agregar a la base de datos el nombre y la puntuacion obtenida por el jugador.
    """

    with sqlite3.connect(archivo) as conexion:
                    try:
                        conexion.execute("insert into Jugadores(Nombre,Score) values (?,?)", (texto,score)) #Insertar dentro 
                        conexion.commit() # Actualiza los datos realmente en la tabla
                        print("SE AGREGO EL JUGADOR CORRECTAMENTE")
                    except:
                        print("Error")
