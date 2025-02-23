import streamlit as st
import sqlite3
import os
# Capturar ancho de la ventana en cada actualización
st.session_state["window_width"] = st.get_option("browser.gatherUsageStats") and st.experimental_get_query_params().get("width", [1024])[0]

# Ruta del logo de especiales
LOGO_ESPECIALES = "ESPECIALES.jpg"  # Asegúrate de que este archivo está en el directorio de la aplicación


import streamlit as st

def detectar_dispositivo():
    """Detecta si el usuario está en un móvil o en un ordenador basándose en el ancho de pantalla."""
    if "window_width" in st.session_state:
        return st.session_state["window_width"] < 800  # Si el ancho es menor a 800px, es móvil
    return False  # Por defecto, PC

# Inicializar detección si no está en session_state
if "is_mobile" not in st.session_state:
    st.session_state["is_mobile"] = detectar_dispositivo()


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

    # Obtener jugadores del equipo
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

        if nuevo_estado != bool(en_coleccion):
            cursor_update.execute("UPDATE JUGADORES SET EN_COLECCION = ? WHERE NUMERO = ?", (int(nuevo_estado), numero))
    
    conn_update.commit()
    conn_update.close()

    if st.button("🔙 Volver a equipos"):
        del st.session_state["equipo_seleccionado"]
        st.rerun()

# 📌 Función para obtener datos generales
def obtener_porcentaje_completado():
    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM JUGADORES WHERE EN_COLECCION = 1")
    jugadores_en_coleccion = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM JUGADORES")
    total_jugadores = cursor.fetchone()[0]
    
    conn.close()
    return round((jugadores_en_coleccion / total_jugadores) * 100, 2) if total_jugadores > 0 else 0

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

# 📌 Función para obtener equipos con escudos ordenados por ID_EQUIPO
def obtener_equipos():
    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ID_EQUIPO, NOMBRE, URL_ESCUDO FROM EQUIPOS WHERE URL_ESCUDO IS NOT NULL ORDER BY ID_EQUIPO ASC")
    equipos = cursor.fetchall()
    conn.close()
    return equipos

# 📌 Mostrar escudos correctamente en móvil y PC
def mostrar_equipos():
    equipos = obtener_equipos()
    
    if not st.session_state["is_mobile"]:
        # ✅ En PC → 4 columnas con el orden correcto
        cols = st.columns(4)
        for idx, (id_equipo, nombre, url_escudo) in enumerate(equipos):
            with cols[idx % 4]:  # Mantener el orden de izquierda a derecha
                if url_escudo:
                    st.image(url_escudo, caption=nombre, use_container_width=True)
                if st.button(f"🔍 Ver {nombre}", key=nombre):
                    st.session_state["equipo_seleccionado"] = nombre
                    st.session_state["mostrar_todos"] = True
                    st.rerun()
    else:
        # ✅ En móviles → Organizar manualmente en filas de 2 equipos por fila
        num_equipos = len(equipos)
        for i in range(0, num_equipos, 2):
            col1, col2 = st.columns(2)
            
            with col1:
                if i < num_equipos:
                    id_equipo, nombre, url_escudo = equipos[i]
                    if url_escudo:
                        st.image(url_escudo, caption=nombre, use_container_width=True)
                    if st.button(f"🔍 Ver {nombre}", key=nombre):
                        st.session_state["equipo_seleccionado"] = nombre
                        st.session_state["mostrar_todos"] = True
                        st.rerun()
            
            with col2:
                if i + 1 < num_equipos:
                    id_equipo, nombre, url_escudo = equipos[i + 1]
                    if url_escudo:
                        st.image(url_escudo, caption=nombre, use_container_width=True)
                    if st.button(f"🔍 Ver {nombre}", key=nombre):
                        st.session_state["equipo_seleccionado"] = nombre
                        st.session_state["mostrar_todos"] = True
                        st.rerun()


# Llamar a la función en la página principal
# mostrar_equipos()
# 📌 Página principal
def pagina_principal():
    st.image("https://assets.laliga.com/assets/logos/LALIGA_HYPERMOTION_RGB_h_color/LALIGA_HYPERMOTION_RGB_h_color.png", caption="LALIGA HYPERMOTION", use_container_width=True)
    st.markdown("---")

    # Contadores
    totales = estampas_totales()
    faltan = estampas_que_faltan()
    en_album = totales - faltan
    porcentaje_completado = obtener_porcentaje_completado()

    col1, col2, col3, col4 = st.columns(4)
    for col, valor, titulo in zip([col1, col2, col3, col4], [totales, en_album, faltan, f"{porcentaje_completado}%"], 
                                  ["TOTAL DE ESTAMPAS", "EN ÁLBUM", "FALTAN", "PORCENTAJE COMPLETADO"]):
        with col:
            st.markdown(f"<p style='text-align: center; font-size: 24px; font-weight: bold;'>{valor}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center;'>{titulo}</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.write("**Selecciona un equipo para ver su lista de jugadores**")
    mostrar_equipos()

# 📌 Lógica de navegación
if "equipo_seleccionado" in st.session_state:
    pagina_jugadores(st.session_state["equipo_seleccionado"])
else:
    pagina_principal()