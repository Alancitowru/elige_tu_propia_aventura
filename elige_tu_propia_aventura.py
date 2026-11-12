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
    objeto TEXT,
    jugador_id INTEGER
)
""")

# Tabla de decisiones
cursor.execute("""
CREATE TABLE IF NOT EXISTS decisiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision TEXT,
    escena TEXT,
    jugador_id INTEGER
)
""")

# Añade la relación con el jugador a bases de datos creadas con una versión anterior.
for tabla in ("inventario", "decisiones"):
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [columna[1] for columna in cursor.fetchall()]
    if "jugador_id" not in columnas:
        cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN jugador_id INTEGER")
    cursor.execute(f"UPDATE {tabla} SET jugador_id = 1 WHERE jugador_id IS NULL")

conexion.commit()


# ==========================================
# 2. FUNCIONES PARA GUARDAR EL PROGRESO
# ==========================================
def guardar_escena(escena, jugador_id):
    cursor.execute("""
    UPDATE jugador
    SET escena_actual = ?
    WHERE id = ?
    """, (escena, jugador_id))
    conexion.commit()

def guardar_decision(decision, escena, jugador_id):
    cursor.execute("""
    INSERT INTO decisiones (decision, escena, jugador_id)
    VALUES (?, ?, ?)
    """, (decision, escena, jugador_id))
    
    conexion.commit()

def elegir_opcion(opciones):
    print("\nOpciones:")
    for key, value in opciones.items():
        print(f"{key}. {value}")
    
    eleccion = input("Elige una opción: ")
    
    while eleccion not in opciones:
        eleccion = input("Opción incorrecta. Elige nuevamente: ")
    
    return eleccion

def agregar_objeto(objeto, jugador_id):
    cursor.execute("""
    INSERT INTO inventario (objeto, jugador_id)
    VALUES (?, ?)
    """, (objeto, jugador_id))
    conexion.commit()

def mostrar_inventario(jugador_id):
    cursor.execute(
        "SELECT objeto FROM inventario WHERE jugador_id = ?",
        (jugador_id,)
    )
    objetos = cursor.fetchall()

    print("\n--- INVENTARIO ---")

    if objetos:

        for objeto in objetos:
            print("-", objeto[0])

    else:

        print("No tienes objetos todavía.")

def consultar_estadisticas():
    nombre_consultado = input(
        "\nIngresa el nombre del usuario que quieres consultar: "
    ).strip()
    while not nombre_consultado:
        nombre_consultado = input(
            "El nombre no puede estar vacío. Intenta nuevamente: "
        ).strip()

    cursor.execute("""
    SELECT id, nombre, escena_actual
    FROM jugador
    WHERE nombre = ? COLLATE NOCASE
    """, (nombre_consultado,))
    jugadores_consultados = cursor.fetchall()

    if not jugadores_consultados:
        print(f"\nNo se encontraron estadísticas para {nombre_consultado}.")
        return

    for jugador_consultado in jugadores_consultados:
        jugador_consultado_id = jugador_consultado[0]
        cursor.execute(
            "SELECT COUNT(*) FROM decisiones WHERE jugador_id = ?",
            (jugador_consultado_id,)
        )
        total_decisiones = cursor.fetchone()[0]

        cursor.execute(
            "SELECT objeto FROM inventario WHERE jugador_id = ?",
            (jugador_consultado_id,)
        )
        objetos = [fila[0] for fila in cursor.fetchall()]

        print("\n================================")
        print(f"ESTADÍSTICAS DE {jugador_consultado[1]}")
        print("================================")
        print("Estado de la aventura:", jugador_consultado[2])
        print("Decisiones tomadas:", total_decisiones)
        print("Objetos en el inventario:", ", ".join(objetos) if objetos else "Ninguno")

# ==========================================
# 3. CARGAR O CREAR UNA PARTIDA
# ==========================================

cursor.execute("SELECT * FROM jugador WHERE id = 1")
jugador = cursor.fetchone()

if jugador:
    opciones_menu = {
        "1": "Continuar partida",
        "2": "Empezar una nueva",
        "3": "Consultar estadísticas de un jugador"
    }
else:
    opciones_menu = {
        "1": "Empezar una nueva partida",
        "2": "Consultar estadísticas de un jugador"
    }

while True:
    opcion = elegir_opcion(opciones_menu)

    if (jugador and opcion == "3") or (not jugador and opcion == "2"):
        consultar_estadisticas()
    else:
        break

if jugador:
    if opcion == "1":

        nombre = jugador[1]
        escena = jugador[2]

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

                cursor.execute("DELETE FROM decisiones WHERE jugador_id = ?", (jugador[0],))
                cursor.execute("DELETE FROM inventario WHERE jugador_id = ?", (jugador[0],))

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

        cursor.execute("DELETE FROM decisiones WHERE jugador_id = ?", (jugador[0],))
        cursor.execute("DELETE FROM inventario WHERE jugador_id = ?", (jugador[0],))

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

jugador_id = jugador[0] if jugador else 1

# ==========================================
# 4. COMIENZO DE LA AVENTURA
# ==========================================

print("\n================================")
print("       EL BOSQUE MISTERIOSO")
print("================================")

print("\nBienvenido,", nombre)

while True:

    print("\n--------------------------------")

    mostrar_inventario(jugador_id)

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

        guardar_decision(opciones[eleccion], escena, jugador_id)

        if eleccion == "1":

            escena = "bosque"

        else:

            escena = "refugio"

        guardar_escena(escena, jugador_id)


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

        guardar_decision(opciones[eleccion], escena, jugador_id)

        if eleccion == "1":

            escena = "cueva"

        else:

            escena = "rio"

        guardar_escena(escena, jugador_id)


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

        guardar_decision(opciones[eleccion], escena, jugador_id)

        if eleccion == "1":

            agregar_objeto("Llave antigua", jugador_id)

        escena = "bosque"

        guardar_escena(escena, jugador_id)


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

        guardar_decision(opciones[eleccion], escena, jugador_id)

        if eleccion == "1":

            cursor.execute("""
            SELECT * FROM inventario
            WHERE objeto = 'Llave antigua' AND jugador_id = ?
            """, (jugador_id,))

            llave = cursor.fetchone()

            if llave:

                escena = "tesoro"

            else:

                escena = "final"

        else:

            escena = "bosque"

        guardar_escena(escena, jugador_id)


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

        guardar_decision(opciones[eleccion], escena, jugador_id)

        if eleccion == "1":

            escena = "bosque"

            guardar_escena(escena, jugador_id)

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

        guardar_escena("terminado", jugador_id)

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

        guardar_escena("terminado", jugador_id)

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
WHERE jugador_id = ?
""", (jugador_id,))

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
