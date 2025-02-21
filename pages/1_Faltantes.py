
import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF

# Configuración de la página para ocupar toda la pantalla
st.set_page_config(layout="wide")  # Maximiza el uso del ancho de pantalla

# Conectar a la base de datos SQLite
conn = sqlite3.connect("liga_hypermotion.db")

# Obtener los equipos con jugadores faltantes
query_faltantes = """
SELECT DISTINCT E.ID_EQUIPO, E.NOMBRE
FROM EQUIPOS E
JOIN JUGADORES J ON E.ID_EQUIPO = J.ID_EQUIPO
WHERE J.EN_COLECCION = 0
ORDER BY E.ID_EQUIPO;
"""
equipos_df = pd.read_sql(query_faltantes, conn)

# Obtener las estampas que faltan en la colección (EN_COLECCION = FALSE)
query_faltantes_detalle = """
SELECT ID_EQUIPO, NUMERO FROM JUGADORES WHERE EN_COLECCION = 0 ORDER BY ID_EQUIPO, NUMERO;
"""
faltantes_df = pd.read_sql(query_faltantes_detalle, conn)

# Cerrar la conexión
conn.close()

# Crear la tabla con el nombre del equipo
tabla_faltantes = pd.DataFrame()
tabla_faltantes["EQUIPO"] = equipos_df["NOMBRE"]

# Crear un diccionario para mapear los jugadores faltantes a cada equipo
faltantes_dict = faltantes_df.groupby("ID_EQUIPO")["NUMERO"].apply(list).to_dict()

# Crear columnas dinámicas para los números de estampas faltantes
max_faltantes = max(map(len, faltantes_dict.values()), default=0)

for i in range(max_faltantes):
    tabla_faltantes[f"Estampa {i+1}"] = ""

# Rellenar la tabla con las estampas que faltan
for idx, row in equipos_df.iterrows():
    id_equipo = row["ID_EQUIPO"]
    if id_equipo in faltantes_dict:
        for i, num in enumerate(faltantes_dict[id_equipo]):
            tabla_faltantes.at[idx, f"Estampa {i+1}"] = num

# Función para generar un PDF con la tabla filtrada y sin nombres de columnas (excepto EQUIPO)
def generar_pdf(tabla):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Título del documento
    pdf.cell(200, 10, "Listado de Estampas Faltantes", ln=True, align='C')
    pdf.ln(5)
    
    # Encabezados de la tabla (solo se mantiene EQUIPO)
    col_widths = [50] + [20] * (len(tabla.columns) - 1)
    pdf.cell(col_widths[0], 7, "EQUIPO", border=1, align='C')  # Solo nombre de la columna EQUIPO

    for i in range(1, len(tabla.columns)):
        pdf.cell(col_widths[i], 7, "", border=1, align='C')  # Encabezados en blanco
    pdf.ln()

    # Contenido de la tabla
    for _, row in tabla.iterrows():
        for i, value in enumerate(row):
            pdf.cell(col_widths[i], 7, str(value), border=1, align='C')
        pdf.ln()

    # Guardar PDF
    pdf_filename = "./listado_estampas_faltantes.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

# Mostrar la tabla en Streamlit ocupando el máximo espacio posible
st.title("📋 Listado de Estampas Faltantes")

st.dataframe(tabla_faltantes, use_container_width=True, height=1000)  # Mayor altura para más visibilidad

# Botón para generar PDF
if st.button("📄 Generar PDF"):
    pdf_path = generar_pdf(tabla_faltantes)
    st.success("PDF generado con éxito. Puedes descargarlo aquí:")
    st.download_button(label="📥 Descargar PDF", data=open(pdf_path, "rb"), file_name="listado_estampas_faltantes.pdf", mime="application/pdf")
