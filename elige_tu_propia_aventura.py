import sqlite3
# ==========================================
# 1. CONEXION CON LA BASE DE DATOS
# ==========================================

conexion = sqlite3.connect("aventura.db")
cursor = conexion.cursor()

# Tabla del jugador
cursor.execute("""
CREATE TABLE IF NOT EXISTS jugador (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    escena_actual TEXT
)
""")

# Tabla del inventario
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    objeto TEXT
)
""")

# Tabla de decisiones
cursor.execute("""
CREATE TABLE IF NOT EXISTS decisiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision TEXT,
    escena TEXT
)
""")

conexion.commit()


# ==========================================
# 2. FUNCIONES PARA GUARDAR EL PROGRESO
# ==========================================


# ==========================================
# 3. CARGAR O CREAR UNA PARTIDA
# ==========================================

cursor.execute("SELECT * FROM jugador WHERE id = 1")
jugador = cursor.fetchone()

if jugador:

    print("\n¡Bienvenido nuevamente!")
    print("Partida encontrada.")

    opcion = input(
        "\n1. Continuar partida"
        "\n2. Empezar una nueva"
        "\nElige: "
    )

    while opcion not in ["1", "2"]:

        opcion = input("Opción incorrecta. Elige 1 o 2: ")

    if opcion == "1":

        nombre = jugador[1]
        escena = jugador[2]

        # Comprobamos si la aventura ya terminó
        if escena == "terminado":

            print("\n¡Ya completaste esta aventura!")

            opcion = input(
                "\n1. Empezar una nueva aventura"
                "\n2. Salir"
                "\nElige: "
            )

            while opcion not in ["1", "2"]:
                opcion = input("Elige 1 o 2: ")

            if opcion == "2":

                conexion.close()
                exit()

            else:

                nombre = input("\nIngresa tu nombre: ")
                escena = "inicio"

                cursor.execute("DELETE FROM inventario")
                cursor.execute("DELETE FROM decisiones")

                cursor.execute("""
                UPDATE jugador
                SET nombre = ?, escena_actual = ?
                WHERE id = 1
                """, (nombre, escena))

                conexion.commit()

        else:

            print("\nContinuando partida de", nombre)

    else:

        nombre = input("\nIngresa tu nombre: ")
        escena = "inicio"

        cursor.execute("DELETE FROM inventario")
        cursor.execute("DELETE FROM decisiones")

        cursor.execute("""
        UPDATE jugador
        SET nombre = ?, escena_actual = ?
        WHERE id = 1
        """, (nombre, escena))

        conexion.commit()

else:

    nombre = input("\nIngresa tu nombre: ")
    escena = "inicio"

    cursor.execute("""
    INSERT INTO jugador (id, nombre, escena_actual)
    VALUES (1, ?, ?)
    """, (nombre, escena))

    conexion.commit()


# ==========================================
# 4. COMIENZO DE LA AVENTURA
# ==========================================

print("\n================================")
print("       EL BOSQUE MISTERIOSO")
print("================================")

print("\nBienvenido,", nombre)

while True:

    print("\n--------------------------------")

    mostrar_inventario()

    # ======================================
    # ESCENA 1: INICIO
    # ======================================

    if escena == "inicio":

        print("\nDespiertas en medio de un bosque.")
        print("No recuerdas cómo llegaste hasta aquí.")
        print("Frente a ti hay dos caminos.")

        opciones = {
            "1": "Adentrarte en el bosque",
            "2": "Buscar un refugio"
        }

        eleccion = elegir_opcion(opciones)

        guardar_decision(opciones[eleccion], escena)

        if eleccion == "1":

            escena = "bosque"

        else:

            escena = "refugio"

        guardar_escena(escena)


    # ======================================
    # ESCENA 2: BOSQUE
    # ======================================

    elif escena == "bosque":

        print("\nLlegas a una zona más profunda del bosque.")
        print("Encuentras una cueva y un río.")

        opciones = {
            "1": "Explorar la cueva",
            "2": "Seguir el río"
        }

        eleccion = elegir_opcion(opciones)

        guardar_decision(opciones[eleccion], escena)

        if eleccion == "1":

            escena = "cueva"

        else:

            escena = "rio"

        guardar_escena(escena)


    # ======================================
    # ESCENA 3: CUEVA
    # ======================================

    elif escena == "cueva":

        print("\nEntras en una cueva oscura.")
        print("Después de caminar unos metros,")
        print("encuentras una llave antigua.")

        opciones = {
            "1": "Agarrar la llave y salir",
            "2": "Ignorar la llave y salir"
        }

        eleccion = elegir_opcion(opciones)

        guardar_decision(opciones[eleccion], escena)

        if eleccion == "1":

            agregar_objeto("Llave antigua")

        escena = "bosque"

        guardar_escena(escena)


    # ======================================
    # ESCENA 4: RIO
    # ======================================

    elif escena == "rio":

        print("\nLlegas a un río.")
        print("Hay un puente que parece llevar a una salida.")

        opciones = {
            "1": "Cruzar el puente",
            "2": "Volver al bosque"
        }

        eleccion = elegir_opcion(opciones)

        guardar_decision(opciones[eleccion], escena)

        if eleccion == "1":

            cursor.execute("""
            SELECT * FROM inventario
            WHERE objeto = 'Llave antigua'
            """)

            llave = cursor.fetchone()

            if llave:

                escena = "tesoro"

            else:

                escena = "final"

        else:

            escena = "bosque"

        guardar_escena(escena)


    # ======================================
    # ESCENA 5: REFUGIO
    # ======================================

    elif escena == "refugio":

        print("\nEncuentras una pequeña cabaña.")
        print("De la nada se cierra brucamente la puerta.")
        print("No puedes salir.")

        opciones = {
            "1": "Retractarte",
            "2": "Salir del juego"
        }

        eleccion = elegir_opcion(opciones)

        guardar_decision(opciones[eleccion], escena)

        if eleccion == "1":

            escena = "bosque"

            guardar_escena(escena)

        else:

            break


    # ======================================
    # FINAL 1: CON LLAVE
    # ======================================

    elif escena == "tesoro":

        print("\n================================")
        print("          ¡FELICIDADES!")
        print("================================")

        print("\nLa llave abre una puerta secreta.")
        print("Detrás de ella encuentras un tesoro.")
        print("\n¡Has ganado la aventura!")

        guardar_escena("terminado")

        break


    # ======================================
    # FINAL 2: SIN LLAVE
    # ======================================

    elif escena == "final":

        print("\n================================")
        print("       FIN DE LA AVENTURA")
        print("================================")

        print("\nLlegas hasta una puerta cerrada.")
        print("No tienes la llave para abrirla.")
        print("No puedes continuar.")

        guardar_escena("terminado")

        break


# ==========================================
# 5. MOSTRAR HISTORIAL DE DECISIONES
# ==========================================

print("\n================================")
print("       HISTORIAL DE DECISIONES")
print("================================")

cursor.execute("""
SELECT decision, escena
FROM decisiones
""")

historial = cursor.fetchall()

if historial:

    for decision in historial:

        print("\nEscena:", decision[1])
        print("Decisión:", decision[0])

else:

    print("Todavía no tomaste decisiones.")


# ==========================================
# 6. CERRAR LA BASE DE DATOS
# ==========================================

conexion.close()

print("\nTu progreso fue guardado.")
print("¡Hasta la próxima!")
