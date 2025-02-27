import sqlite3
import pandas as pd
import streamlit as st
from fpdf import FPDF
# Título de la app
# URL del logo de LaLiga Hypermotion
logo_url = "https://assets.laliga.com/assets/logos/LALIGA_HYPERMOTION_RGB_h_color/LALIGA_HYPERMOTION_RGB_h_color.png"

# Mostrar la imagen en Streamlit con el nuevo parámetro
st.image(logo_url, caption="LALIGA HYPERMOTION", use_container_width=True)



# Configurar la página para que sea más ancha
st.set_page_config(layout="wide")  # ✅ Usa todo el ancho disponible en pantalla
def estampas_que_faltan():
    conn = sqlite3.connect("liga_hypermotion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM JUGADORES WHERE EN_COLECCION = 0")
    jugadores_faltan = cursor.fetchone()[0]  
    conn.close()
    return jugadores_faltan


# Función para obtener las estampas faltantes en formato tabla con equipos y números en columnas
def obtener_estampas_faltantes():
    conn = sqlite3.connect("liga_hypermotion.db")
    query = """
    SELECT E.ID_EQUIPO, E.NOMBRE AS EQUIPO, J.NUMERO, J.NOMBRE AS JUGADOR
    FROM JUGADORES J
    JOIN EQUIPOS E ON J.ID_EQUIPO = E.ID_EQUIPO
    WHERE J.EN_COLECCION = 0
    ORDER BY E.ID_EQUIPO, 
             CASE 
                 WHEN J.NUMERO GLOB '[0-9]*' THEN CAST(J.NUMERO AS INTEGER) 
                 ELSE 9999  -- Para ordenar correctamente los valores P1-P11
             END, 
             J.NUMERO;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Reemplazar números P1-P11 por el nombre del jugador en la columna NUMERO
    df["NUMERO"] = df.apply(
        lambda row: row["JUGADOR"] if row["NUMERO"].startswith("P") and row["NUMERO"][1:].isdigit() and 1 <= int(row["NUMERO"][1:]) <= 11 else row["NUMERO"], axis=1)

    # Convertir la tabla en formato de pivote con los equipos como filas y los números como columnas
    df_pivot = df.groupby(["ID_EQUIPO", "EQUIPO"])["NUMERO"].apply(list).reset_index()
    df_pivot = df_pivot.sort_values(by=["ID_EQUIPO"])  # ✅ Ordenar por ID_EQUIPO

    return df_pivot

# Función para generar el PDF en el formato solicitado
def generar_pdf():
    estampas_faltantes = obtener_estampas_faltantes()
    numero_que_faltan = estampas_que_faltan()

    if estampas_faltantes.empty:
        st.warning("No hay estampas faltantes.")
        return

    #pdf = FPDF(orientation="L", unit="mm", format="A4")  # Formato apaisado: Landscape
    pdf = FPDF(orientation="P", unit="mm", format="A4")  # Formato apaisado: Portrait
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Configurar la fuente
    pdf.set_font("Arial", "B", 14)
    pdf.cell(280, 10, f"Lista de Estampas Faltantes ({numero_que_faltan})", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 10, "Nombre del Equipo", 1, 0, "C")

    # Determinar el número máximo de columnas necesarias
    max_columns = max(estampas_faltantes["NUMERO"].apply(len), default=0)
    for i in range(1, max_columns + 1):
        pdf.cell(25, 10, f"NUM-{i}", 1, 0, "C")
    pdf.ln()

    pdf.set_font("Arial", "", 10)

    # Agregar los datos al PDF
    for _, row in estampas_faltantes.iterrows():
        pdf.cell(60, 8, row["EQUIPO"], 1, 0, "C")

        for i in range(max_columns):
            if i < len(row["NUMERO"]):
                pdf.cell(25, 8, str(row["NUMERO"][i]), 1, 0, "C")
            else:
                pdf.cell(25, 8, "", 1, 0, "C")  # Celda vacía si no hay más datos
        pdf.ln()

    # Guardar el archivo PDF
    pdf_path = "estampas_faltantes.pdf"
    pdf.output(pdf_path)

    return pdf_path

# 📌 **Interfaz en Streamlit**
st.title("📋 Listado de Estampas Faltantes")

faltantes_df = obtener_estampas_faltantes()

if faltantes_df.empty:
    st.info("🎉 ¡Felicidades! No hay estampas faltantes.")
else:
    # ✅ Ocultar el índice y el ID_EQUIPO en la tabla mostrada en pantalla
    df_display = faltantes_df.drop(columns=["ID_EQUIPO"])  # Eliminar ID_EQUIPO
    df_display = df_display.set_index("EQUIPO")  # Usar el nombre del equipo como índice

    # ✅ Mostrar la tabla sin índice visual y con mejor formato
    st.dataframe(df_display, use_container_width=True, height=800)

    # Botón para generar el PDF
    if st.button("📄 Generar PDF"):
        pdf_file = generar_pdf()
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="📥 Descargar PDF",
                data=f,
                file_name="estampas_faltantes.pdf",
                mime="application/pdf",
            )