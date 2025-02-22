import streamlit as st
import sqlite3
import pandas as pd

# Función para conectar a la base de datos
def obtener_estampas_faltantes():
    conn = sqlite3.connect("liga_hypermotion.db")
    query = """
    SELECT J.ID_EQUIPO, J.EN_COLECCION, J.NUMERO, J.NOMBRE, E.NOMBRE AS EQUIPO
    FROM JUGADORES J
    JOIN EQUIPOS E ON J.ID_EQUIPO = E.ID_EQUIPO
    WHERE J.EN_COLECCION = 0
    ORDER BY J.NUM ASC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Función para actualizar el estado de EN_COLECCION
def actualizar_estampa(numero, nuevo_estado):
    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE JUGADORES SET EN_COLECCION = ? WHERE NUMERO = ?", (nuevo_estado, numero))
    conn.commit()
    conn.close()

def faltan():
    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM JUGADORES WHERE EN_COLECCION = 0")
    faltantes = cursor.fetchone()[0]
    return faltantes
  

# Título de la app
# URL del logo de LaLiga Hypermotion
logo_url = "https://assets.laliga.com/assets/logos/LALIGA_HYPERMOTION_RGB_h_color/LALIGA_HYPERMOTION_RGB_h_color.png"

# Mostrar la imagen en Streamlit con el nuevo parámetro
st.image(logo_url, caption="LALIGA HYPERMOTION", use_container_width=True)

estampas_que_faltan = faltan()
# Línea separadora antes de mostrar el listado de jugadores
st.markdown("---")

# Estilo para centrar texto
style = "text-align: center; font-size: 24px; font-weight: bold;"

# Mostrar los valores en columnas
st.markdown(f"<p style='{style}'>Faltan {estampas_que_faltan} estampas</p>", unsafe_allow_html=True)

# st.title(f"Faltan {estampas_que_faltan} estampas")
# Línea separadora antes de mostrar el listado de jugadores
st.markdown("---")

# Obtener los datos de la base de datos
faltantes_df = obtener_estampas_faltantes()

if faltantes_df.empty:
    st.info("🎉 ¡Felicidades! No hay estampas faltantes.")
else:
    # Mostrar la tabla con checkboxes
    nueva_lista = []
    
    for index, row in faltantes_df.iterrows():
        checkbox = st.checkbox(f"{row['NUMERO']} - {row['NOMBRE']} ({row['EQUIPO']})", value=bool(row['EN_COLECCION']), key=f"chk_{row['NUMERO']}")
        nueva_lista.append((row['NUMERO'], checkbox))
    
    # Si se han cambiado valores, actualizar la base de datos
    for numero, estado in nueva_lista:
        nuevo_estado = 1 if estado else 0
        actualizar_estampa(numero, nuevo_estado)

    # Recargar datos actualizados
    st.rerun()
    