import streamlit as st
import sqlite3

# Título de la app
# URL del logo de LaLiga Hypermotion
logo_url = "https://assets.laliga.com/assets/logos/LALIGA_HYPERMOTION_RGB_h_color/LALIGA_HYPERMOTION_RGB_h_color.png"

# Mostrar la imagen en Streamlit con el nuevo parámetro
st.image(logo_url, caption="LALIGA HYPERMOTION", use_container_width=True)



# Estilos personalizados para agrandar la fuente y ajustar el input
st.markdown(
    """
    <style>
        .big-font {
            font-size: 24px !important;
            font-weight: bold;
            text-align: center;
        }
        .custom-input input {
            font-size: 28px !important;
            font-weight: bold;
            text-align: center;
            width: 200px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

import streamlit as st
import sqlite3

# Conectar con la base de datos
def obtener_estampa(numero):
    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT NUMERO, NOMBRE, CANTIDAD_REPES FROM JUGADORES WHERE NUMERO = ?", (numero,))
    resultado = cursor.fetchone()
    
    conn.close()
    return resultado

# Función para actualizar la cantidad de repes en la base de datos
def actualizar_repetidas(numero, cantidad):
    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()
    
    cursor.execute("UPDATE JUGADORES SET CANTIDAD_REPES = ? WHERE NUMERO = ?", (cantidad, numero))
    conn.commit()
    
    conn.close()

# Inicializar variables en session_state si no existen
if "numero_estampa" not in st.session_state:
    st.session_state.numero_estampa = ""
if "cantidad_repes" not in st.session_state:
    st.session_state.cantidad_repes = 1

st.title("📌 Añadir Estampas Repetidas")

# Input para ingresar el número de la estampa
numero = st.text_input("Introduce el número de la estampa:", value=st.session_state.numero_estampa)

# Botón para buscar estampa
if st.button("Buscar Estampa"):
    estampa = obtener_estampa(numero.strip())
    
    if estampa:
        nombre, cantidad_repes = estampa[1], estampa[2]
        st.success(f"📍 Estampa encontrada: **{nombre}** - Repetidas: {cantidad_repes}")

        # Guardar en session_state
        st.session_state.numero_estampa = numero.strip()
        st.session_state.cantidad_repes = cantidad_repes

    else:
        st.error("❌ No se encontró la estampa en la base de datos.")

# Mostrar opciones solo si hay una estampa cargada
if st.session_state.numero_estampa:
    col1, col2, col3 = st.columns([1, 2, 1])

    # Funciones para actualizar en tiempo real
    def aumentar():
        st.session_state.cantidad_repes += 1

    def disminuir():
        if st.session_state.cantidad_repes > 1:
            st.session_state.cantidad_repes -= 1

    with col1:
        st.button("➖", key="menos", on_click=disminuir)

    with col2:
        st.markdown(f"<h3 style='text-align: center;'>📦 Cantidad: {st.session_state.cantidad_repes}</h3>", unsafe_allow_html=True)

    with col3:
        st.button("➕", key="mas", on_click=aumentar)

    # Botón para guardar los cambios en la base de datos
    if st.button("Guardar Cambios"):
        actualizar_repetidas(st.session_state.numero_estampa, st.session_state.cantidad_repes)
        st.success(f"✅ Se ha actualizado la cantidad de repetidas a {st.session_state.cantidad_repes}")