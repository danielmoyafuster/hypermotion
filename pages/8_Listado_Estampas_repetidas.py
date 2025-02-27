import sqlite3
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# URL del logo de LaLiga Hypermotion
logo_url = "https://assets.laliga.com/assets/logos/LALIGA_HYPERMOTION_RGB_h_color/LALIGA_HYPERMOTION_RGB_h_color.png"

# Mostrar la imagen en Streamlit con el nuevo parámetro
st.image(logo_url, caption="LALIGA HYPERMOTION", use_container_width=True)


import sqlite3
import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas

# Ruta de la base de datos
db_path = "liga_hypermotion.db"

# Conectar con la base de datos y obtener los datos ordenados
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

query = """
SELECT EQUIPOS.ID_EQUIPO, EQUIPOS.NOMBRE AS EQUIPO, 
       CASE 
           WHEN EQUIPOS.ID_EQUIPO = 26 THEN JUGADORES.NOMBRE 
           ELSE JUGADORES.NUMERO 
       END AS VALOR,
       (JUGADORES.CANTIDAD_REPES - 1) AS REPES_EXTRAS
FROM JUGADORES
JOIN EQUIPOS ON JUGADORES.ID_EQUIPO = EQUIPOS.ID_EQUIPO
WHERE JUGADORES.CANTIDAD_REPES > 1
ORDER BY EQUIPOS.ID_EQUIPO ASC, JUGADORES.NUM ASC;
"""

df_repetidas = pd.read_sql_query(query, conn)
conn.close()

# Crear una nueva columna con el formato "VALOR (CANTIDAD_REPES - 1)"
df_repetidas["FORMATO"] = df_repetidas.apply(lambda row: f"{row['VALOR']} ({row['REPES_EXTRAS']})", axis=1)

# Agrupar por equipo, asegurando que el orden se mantenga
df_pivot = df_repetidas.groupby(["ID_EQUIPO", "EQUIPO"])["FORMATO"].apply(lambda x: ", ".join(x)).reset_index()
df_pivot = df_pivot.sort_values(by="ID_EQUIPO", ascending=True).drop(columns=["ID_EQUIPO"])  # Elimina ID tras ordenar

# **Resetear el índice para evitar que Streamlit lo muestre**
df_pivot = df_pivot.reset_index(drop=True)

# Mostrar los datos en Streamlit sin índice
st.title("📌 Listado de Estampas Repetidas")
st.dataframe(df_pivot, width=1000, height=600)

# Ruta donde se guardará el PDF
pdf_path = "Listado_Estampas_Repetidas.pdf"

# Función para generar el PDF optimizando el espacio de las filas
def generar_pdf(path, df):
    c = canvas.Canvas(path, pagesize=landscape(A4))
    width, height = landscape(A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "📌 Listado de Estampas Repetidas")

    c.setFont("Helvetica-Bold", 12)
    y_position = height - 100
    c.drawString(50, y_position, "Equipo")
    c.drawString(150, y_position, "Estampas Repetidas")
    c.line(50, y_position - 10, width - 50, y_position - 10)

    c.setFont("Helvetica", 11)
    y_position -= 30

    for index, row in df.iterrows():
        equipo_nombre = row["EQUIPO"]
        estampas_str = row["FORMATO"]
        
        c.drawString(50, y_position, equipo_nombre[:15])
        
        text_object = c.beginText(150, y_position)
        text_object.setFont("Helvetica", 11)

        max_chars_per_line = 100
        estampas_partes = [estampas_str[i:i+max_chars_per_line] for i in range(0, len(estampas_str), max_chars_per_line)]
        for line in estampas_partes:
            text_object.textLine(line)

        c.drawText(text_object)

        espacio_por_linea = 15
        altura_fila = max(20, espacio_por_linea * len(estampas_partes))
        y_position -= altura_fila

        if y_position < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y_position = height - 100

    c.save()

# Botón para generar y descargar el PDF en Streamlit
if st.button("📄 Generar PDF"):
    generar_pdf(pdf_path, df_pivot)
    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ Descargar PDF", f, file_name="Listado_Estampas_Repetidas.pdf", mime="application/pdf")