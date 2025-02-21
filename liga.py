
import streamlit as st
import sqlite3
import os

# Ruta del logo de especiales
LOGO_ESPECIALES = "ESPECIALES.jpg"  # Asegúrate de que este archivo está en el directorio de la aplicación

def pagina_jugadores(equipo):
    st.title(f"👕 Jugadores de {equipo}")

    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()

    cursor.execute(
        """SELECT NUMERO, NOMBRE, EN_COLECCION 
        FROM JUGADORES 
        WHERE ID_EQUIPO = (SELECT ID_EQUIPO FROM EQUIPOS WHERE NOMBRE = ?) 
        ORDER BY NUMERO""",
        (equipo,)
    )
    jugadores = cursor.fetchall()
    conn.close()

    col1, col2 = st.columns(2)

    for idx, (numero, nombre, en_coleccion) in enumerate(jugadores):
        checkbox_label = f"{numero} - {nombre}"

        if idx % 2 == 0:
            with col1:
                tiene = st.checkbox(checkbox_label, value=bool(en_coleccion), key=f"{equipo}_{numero}")
        else:
            with col2:
                tiene = st.checkbox(checkbox_label, value=bool(en_coleccion), key=f"{equipo}_{numero}")

    if st.button("🔙 Volver a equipos"):
        del st.session_state["equipo_seleccionado"]
        st.rerun()



# Función para obtener el porcentaje de jugadores en la colección
def obtener_porcentaje_completado():
    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM JUGADORES WHERE EN_COLECCION = 1")
    jugadores_en_coleccion = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM JUGADORES")
    total_jugadores = cursor.fetchone()[0]
    
    conn.close()

    if total_jugadores == 0:
        return 0  # Evitar división por cero
    return round((jugadores_en_coleccion / total_jugadores) * 100, 2)

# Función para obtener los equipos con escudo válido ordenados por ID_EQUIPO
def obtener_equipos():
    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ID_EQUIPO, NOMBRE, URL_ESCUDO FROM EQUIPOS WHERE URL_ESCUDO IS NOT NULL ORDER BY ID_EQUIPO ASC")
    equipos = cursor.fetchall()
    conn.close()
    return equipos

# Página principal con porcentaje de completado y el logo de especiales al final
def pagina_principal():
    porcentaje_completado = obtener_porcentaje_completado()
    
    st.title("Liga Hypermotion 2024/25")
    st.write(f"**{porcentaje_completado}% Completado - Selecciona un equipo para ver su lista de jugadores**")

    # Obtener los equipos ordenados por ID_EQUIPO
    equipos = obtener_equipos()

    # Mostrar los escudos como botones clickeables
    cols = st.columns(4)  # Número de columnas para organizar los escudos

    for idx, (id_equipo, nombre, url_escudo) in enumerate(equipos):
        with cols[idx % 4]:  # Distribuir los escudos en columnas
            if url_escudo:
                st.image(url_escudo, caption=nombre, use_container_width=True)
            if st.button(f"🔍 Ver {nombre}", key=nombre):
                st.session_state["equipo_seleccionado"] = nombre
                st.session_state["mostrar_todos"] = True  # Por defecto, mostrar todos los jugadores
                st.rerun()  # Refrescar la página para mostrar la lista de jugadores

    # Añadir el logo de especiales al final, alineado con el tamaño de los escudos
    st.markdown("---")
    st.subheader("⚡ Estampas Especiales")

    col_especial = cols[len(equipos) % 4]  # Asegurar alineación con la cuadrícula de equipos

    with col_especial:
        if os.path.exists(LOGO_ESPECIALES):
            st.image(LOGO_ESPECIALES, caption="Especiales", use_container_width=True)

        if st.button("🔍 Ver Estampas Especiales"):
            st.session_state["mostrar_especiales"] = True
            st.rerun()

# Página de estampas especiales con dos columnas y opción de filtro
def pagina_especiales():
    st.title("⚡ Estampas Especiales")

    # Selector para mostrar todas las estampas o solo las que faltan
    mostrar_todos = st.radio("Mostrar:", ["Todos", "Solo los que faltan"], index=0)
    mostrar_todos = True if mostrar_todos == "Todos" else False

    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()

    if mostrar_todos:
        cursor.execute("SELECT NUMERO, NOMBRE, TIPO, EN_COLECCION FROM JUGADORES WHERE ESPECIALES = 1 ORDER BY NUMERO")
    else:
        cursor.execute("SELECT NUMERO, NOMBRE, TIPO, EN_COLECCION FROM JUGADORES WHERE ESPECIALES = 1 AND EN_COLECCION = 0 ORDER BY NUMERO")

    jugadores = cursor.fetchall()
    conn.close()

    if not jugadores:
        st.write("No hay estampas especiales registradas.")
    else:
        col1, col2 = st.columns(2)

        for idx, (numero, nombre, tipo, en_coleccion) in enumerate(jugadores):
            checkbox_label = f"{numero} - {nombre} - {tipo}"

            if idx % 2 == 0:
                with col1:
                    tiene = st.checkbox(checkbox_label, value=bool(en_coleccion), key=f"especiales_{numero}")
            else:
                with col2:
                    tiene = st.checkbox(checkbox_label, value=bool(en_coleccion), key=f"especiales_{numero}")

            # Actualizar en la base de datos si se marca/desmarca
            conn = sqlite3.connect("liga_hypermotion.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE JUGADORES SET EN_COLECCION = ? WHERE NUMERO = ?", (int(tiene), numero))
            conn.commit()
            conn.close()

    if st.button("🔙 Volver a equipos"):
        del st.session_state["mostrar_especiales"]
        st.rerun()

# Definir qué página mostrar
if "mostrar_especiales" in st.session_state:
    pagina_especiales()
elif "equipo_seleccionado" in st.session_state:
    pagina_jugadores(st.session_state["equipo_seleccionado"])
else:
    pagina_principal()
