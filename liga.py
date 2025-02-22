
import streamlit as st
import sqlite3
import os

# Ruta del logo de especiales
LOGO_ESPECIALES = "ESPECIALES.jpg"  # Asegúrate de que este archivo está en el directorio de la aplicación

def pagina_jugadores(equipo):
    st.title(f"👕 Jugadores de {equipo}")

    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()

    # Obtener la URL del escudo del equipo
    cursor.execute("SELECT URL_ESCUDO FROM EQUIPOS WHERE NOMBRE = ?", (equipo,))
    url_escudo = cursor.fetchone()

    if url_escudo and url_escudo[0]:  
        st.markdown(
            f"<p style='text-align: center; font-size:24px; font-weight:bold;'>{equipo} - <img src='{url_escudo[0]}' width='150'></p>",
            unsafe_allow_html=True
        )  

    # Agregar opción para seleccionar entre ver todos o solo los que faltan
    ver_todos = st.radio("Mostrar:", ["Todos", "Solo los que faltan"], index=0)
    mostrar_todos = True if ver_todos == "Todos" else False

    # Línea separadora
    st.markdown("---")

    # Construir la consulta SQL dinámicamente
    consulta = """SELECT NUMERO, NOMBRE, EN_COLECCION 
    FROM JUGADORES 
    WHERE ID_EQUIPO = (SELECT ID_EQUIPO FROM EQUIPOS WHERE NOMBRE = ?)"""

    if not mostrar_todos:
        consulta += " AND EN_COLECCION = 0"

    consulta += " ORDER BY NUM"

    cursor.execute(consulta, (equipo,))
    jugadores = cursor.fetchall()

    # Mostrar los jugadores en dos columnas
    col1, col2 = st.columns(2)

    # Conectar para actualizar en la base de datos
    conn_update = sqlite3.connect("liga_hypermotion.db")
    cursor_update = conn_update.cursor()

    for idx, (numero, nombre, en_coleccion) in enumerate(jugadores):
        checkbox_label = f"{numero} - {nombre}"

        if idx % 2 == 0:
            with col1:
                nuevo_estado = st.checkbox(checkbox_label, value=bool(en_coleccion), key=f"{equipo}_{numero}")
        else:
            with col2:
                nuevo_estado = st.checkbox(checkbox_label, value=bool(en_coleccion), key=f"{equipo}_{numero}")

        # Si el estado cambió, actualizar en la base de datos
        if nuevo_estado != bool(en_coleccion):
            cursor_update.execute("UPDATE JUGADORES SET EN_COLECCION = ? WHERE NUMERO = ?", (int(nuevo_estado), numero))
    
    # Guardar cambios en la base de datos
    conn_update.commit()
    conn_update.close()

    # Botón para volver a la pantalla principal
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


def estampas_que_faltan():
    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM JUGADORES WHERE EN_COLECCION = 0")
    jugadores_faltan = cursor.fetchone()[0]  
    conn.close()
    return jugadores_faltan

def estampas_totales():    
    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM JUGADORES")
    jugadores_total = cursor.fetchone()[0]
    conn.close()

    return jugadores_total

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
    faltan = estampas_que_faltan()
    totales = estampas_totales()
    en_album = totales - faltan


    # URL del logo de LaLiga Hypermotion
    logo_url = "https://assets.laliga.com/assets/logos/LALIGA_HYPERMOTION_RGB_h_color/LALIGA_HYPERMOTION_RGB_h_color.png"

    # Mostrar la imagen en Streamlit con el nuevo parámetro
    st.image(logo_url, caption="LALIGA HYPERMOTION", use_container_width=True)


#    st.title("       Liga Hypermotion 2024/25")

    # Línea separadora antes de mostrar el listado de jugadores
    st.markdown("---")
    # -------------------------------------------------------------------
    # Organizar en cuatro columnas
    col1, col2, col3, col4 = st.columns(4)

    # Estilo para centrar texto
    style = "text-align: center; font-size: 24px; font-weight: bold;"

    # Mostrar los valores en columnas
    with col1:
        st.markdown(f"<p style='{style}'>{totales}</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>TOTAL DE ESTAMPAS</p>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<p style='{style}'>{en_album}</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>EN ÁLBUM</p>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"<p style='{style}'>{faltan}</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>FALTAN</p>", unsafe_allow_html=True)

    with col4:
        st.markdown(f"<p style='{style}'>{porcentaje_completado}%</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>PORCENTAJE COMPLETADO</p>", unsafe_allow_html=True)
      # Línea separadora antes de mostrar el listado de jugadores
    st.markdown("---")
    
    
    # --------------------------------------------------------------------
    st.write(f"**Selecciona un equipo para ver su lista de jugadores**")

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
    
    # Línea separadora antes de mostrar el listado de jugadores
    st.markdown("---")

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
