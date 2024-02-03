""" Nicolás Vlaeminch Div K | Desafio PyGame """

import pygame
from pygame.locals import *
from pygame import mixer
from constantes import *
from funciones import *

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

reloj = pygame.time.Clock()
fps = FPS

screen = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Plataforma")

# Cargar imagenes
fondo_imagen = pygame.image.load('Juego Plataforma\img\sky.png')
restart_imagen = pygame.image.load('Juego Plataforma\img\img_reiniciar.png')
inicio_imagen = pygame.image.load('Juego Plataforma\img\img_inicio.png')
iniciar_imagen = pygame.image.load('Juego Plataforma\img\img_iniciar.png')
salir_imagen = pygame.image.load('Juego Plataforma\img\img_salir.png')
ranking_imagen = pygame.image.load('Juego Plataforma\img\img_ranking.png')
ingresar_nombre_imagen = pygame.image.load('Juego Plataforma\img\img_ingresa_nombre.png')
nombre_imagen = pygame.image.load('Juego Plataforma\img\img_nombre.png')
jugar_imagen = pygame.image.load('Juego Plataforma\img\img_jugar.png')

# Cargar Sonidos
pygame.mixer.music.load('Juego Plataforma\img\music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
moneda_sonido = pygame.mixer.Sound('Juego Plataforma\img\coin.wav')
moneda_sonido.set_volume(0.5)
ganaste_sonido = pygame.mixer.Sound('Juego Plataforma\img\win.mp3')
ganaste_sonido.set_volume(0.8)

# Banderas y contadores.
game_over = 0
menu_principal_opcion = 1
monedas_recogidas = 0

fuente_1 = pygame.font.SysFont("Arial", 25)
fuente_2 = pygame.font.SysFont("Arial", 80)
fuente_3 = pygame.font.SysFont("Arial", 50)
fuente_input = pygame.font.SysFont("Arial", 50)

ingreso = ""
ingreso_rect = pygame.Rect(200, 400, 200, 100)

personaje = Personaje(100, ALTO_VENTANA - 130)

mundo = Mundo(COORDENADAS_MUNDO_1)
nivel = 1
nivel_maximo = 3
tiempo_iniciado = False
tiempo_inicio = 0
tiempo_juego = 0
ganaste = True
nombre_jugador = "Sin nombre"

#Crear botones
boton_inicio = Button(ANCHO_VENTANA // 2 - 50, ALTO_VENTANA // 2 + 30, inicio_imagen)
boton_restart = Button(ANCHO_VENTANA // 2 - 50, ALTO_VENTANA // 2 + 90, restart_imagen)
boton_ingresar_nombre = Button(ANCHO_VENTANA / 2 - 250, ALTO_VENTANA / 2 - 450, ingresar_nombre_imagen)
boton_nombre = Button(ANCHO_VENTANA / 2 - 250, ALTO_VENTANA / 2 - 250, nombre_imagen)
boton_iniciar = Button(ANCHO_VENTANA / 2 - 150, ALTO_VENTANA / 2 - 50, iniciar_imagen)
boton_raking = Button(ANCHO_VENTANA / 2 - 150, ALTO_VENTANA / 2 + 150, ranking_imagen)
boton_salir = Button(ANCHO_VENTANA / 2 - 150, ALTO_VENTANA / 2 + 350, salir_imagen)
boton_jugar = Button(ANCHO_VENTANA / 2 - 150, ALTO_VENTANA / 2 + 150, jugar_imagen)

crear_tabla("bd_juego.db")

running = True
while running:

    # Mantiene el juego ejecutándose a 60 cuadros por segundo.
    reloj.tick(fps)
    tiempo_init = int(pygame.time.get_ticks() / 1000)

    screen.blit(fondo_imagen, (0, 0))
    texto_monedas = fuente_1.render(f"Puntos: {monedas_recogidas}", True, COLOR_BLANCO)
    texto_temporalizador = fuente_1.render(f"Tiempo: {tiempo_juego} seg", True, COLOR_BLANCO)
    texto_felicidades = fuente_2.render("¡Felicidades!", True, COLOR_AZUL)
    texto_ganaste = fuente_3.render("¡Ganaste!", True, COLOR_AZUL)
    texto_perdiste = fuente_2.render("¡Perdiste!", True, COLOR_AZUL)
    # dibujar_casillas()
    #print(tiempo_juego)

    if menu_principal_opcion == 1:
        ganaste = True
        nivel = 1
        monedas_recogidas = 0
        personaje.reiniciar(100, ALTO_VENTANA - 130)
        mundo = cargar_nivel(nivel)
        game_over = 0

        boton_ingresar_nombre.draw()
        boton_nombre.draw()
        font_input_surface = fuente_input.render(ingreso, True, COLOR_BLANCO)
        screen.blit(font_input_surface, (ANCHO_VENTANA / 2 - 180, ALTO_VENTANA / 2 - 225,))
        if boton_salir.draw():
            running = False
        if boton_iniciar.draw():
            menu_principal_opcion = 2
            tiempo_inicio = tiempo_init
            print("Texto ingresado:", ingreso)
            nombre_jugador = ingreso
            ingreso = "Sin nombre"
        if boton_raking.draw():
            menu_principal_opcion = 3
    elif menu_principal_opcion == 3:
        mostrar_ranking("bd_juego.db", screen)
    elif menu_principal_opcion == 2:
        if game_over != 1 and game_over != -1:
            tiempo_juego = tiempo_init - tiempo_inicio
        mundo.dibujar()
        enemigos_grupo.update()
        enemigos_grupo.draw(screen)
        lavas_grupo.draw(screen)
        salida_grupo.draw(screen)
        monedas_grupo.draw(screen)
        screen.blit(texto_monedas, (10, 10))
        screen.blit(texto_temporalizador, (200, 10))

        game_over = personaje.actualizar_personaje(game_over, mundo)

        # Si esta en 0 el juego esta corriendo.
        if game_over == 0:
            if pygame.sprite.spritecollide(personaje, monedas_grupo, True):
                moneda_sonido.play()
                monedas_recogidas += 10
                #print(monedas_recogidas)

        # Verifica si el jugador murio.
        if game_over == -1:
            screen.blit(texto_perdiste, ((ANCHO_VENTANA // 2) - 165, ANCHO_VENTANA - 575))
            if boton_restart.draw():
                tiempo_inicio = tiempo_init
                nivel = 1
                monedas_recogidas = 0
                personaje.reiniciar(100, ALTO_VENTANA - 130)
                mundo = cargar_nivel(nivel)
                game_over = 0
                ingreso = "Sin nombre"
            elif boton_inicio.draw():
                menu_principal_opcion = 1
                ingreso = "Sin nombre"

        if game_over == 1:
            if nivel_maximo == nivel:
                screen.blit(texto_felicidades, ((ANCHO_VENTANA // 2) - 220, ANCHO_VENTANA - 650))
                screen.blit(texto_ganaste, ((ANCHO_VENTANA // 2) - 100, ANCHO_VENTANA - 550))
                if ganaste:
                    agregar_jugador("bd_juego.db", nombre_jugador, monedas_recogidas)
                    ganaste_sonido.play()
                    ganaste = False
                if boton_restart.draw():
                    menu_principal_opcion = 1
            else:
                nivel += 1
                #print(nivel)
                personaje.reiniciar(100, ALTO_VENTANA - 130)
                mundo = cargar_nivel(nivel)
                game_over = 0

        #print(game_over)

        # Coordenas de las casillas
        # print(mundo.casilla_lista)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_BACKSPACE:
                ingreso = ingreso[0:-1]  # Método slice
            # elif evento.key == pygame.K_RETURN:
            #    if menu_principal_opcion == 1:
            #       print("Texto ingresado:", ingreso)
            #       nombre_jugador = ingreso
            #       ingreso = "Sin nombre"
            #       menu_principal_opcion = 2
            #       tiempo_inicio = tiempo_init
            elif evento.key == pygame.K_ESCAPE:
                if menu_principal_opcion == 3:
                    menu_principal_opcion = 1
            else:
                ingreso += evento.unicode  # Da el texto que se presiona en el teclado

    pygame.display.update()

pygame.quit()
