import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuración de la página
st.set_page_config(page_title="Evaluación Nutricional OMS", layout="centered")

# 2. Cargar los datos con la codificación correcta
@st.cache_data
def load_data():
    # Se utilizan los nombres exactos de tus archivos y codificación latin-1
    df_boys = pd.read_csv("wfl_boys_0-to-2-years_zscores.xlsx - wfl_boys_0 to 2 years_zscores.csv", encoding="latin-1")
    df_girls = pd.read_csv("wfl_girls_0-to-2-years_zscores.xlsx - wfl_girls_0 to 2 years_zscores.csv", encoding="latin-1")
    return df_boys, df_girls

# Función para redondear la talla al 0.5 cm más cercano
def round_to_nearest_half(number):
    return round(number * 2) / 2

# 3. Interfaz de Usuario
st.title("Calculadora de Desnutrición (Peso/Longitud)")
st.markdown("Basado en los patrones de crecimiento de la OMS para **menores de 2 años**.")

df_boys, df_girls = load_data()

# Formularios de entrada
sexo = st.radio("Seleccione el sexo del paciente:", ("Niño", "Niña"))
talla_cm = st.number_input("Ingrese la talla/longitud en cm (ej. 72.3):", min_value=45.0, max_value=110.0, value=70.0, step=0.1)
peso_g = st.number_input("Ingrese el peso exacto en GRAMOS (ej. 8500):", min_value=1000.0, max_value=30000.0, value=8500.0, step=50.0)

if st.button("Calcular Evaluación"):
    # Conversión de gramos a kilogramos
    peso_kg = peso_g / 1000.0
    talla_ajustada = round_to_nearest_half(talla_cm)
    
    # Seleccionar dataset según sexo
    df = df_boys if sexo == "Niño" else df_girls
    
    # Validación de rango de talla en la tabla
    if talla_ajustada < df['Length'].min() or talla_ajustada > df['Length'].max():
        st.error(f"La talla ajustada ({talla_ajustada} cm) está fuera del rango de las tablas para menores de 2 años.")
    else:
        # Extraer variables LMS de la tabla para la talla correspondiente
        row = df[df['Length'] == talla_ajustada].iloc[0]
        L = row['L']
        M = row['M']  # Mediana (Peso ideal)
        S = row['S']
        
        # Calcular Z-score exacto usando la fórmula LMS de la OMS
        if L != 0:
            z_score = (((peso_kg / M) ** L) - 1) / (S * L)
        else:
            z_score = np.log(peso_kg / M) / S
            
        # Clasificación del estado nutricional según el Z-score
        if z_score <= -3:
            estado = "Desnutrición Aguda Severa (≤ -3 SD)"
            color = "#D32F2F"  # Rojo
        elif -3 < z_score <= -2:
            estado = "Desnutrición Aguda Moderada (entre -3 y -2 SD)"
            color = "#F57C00"  # Naranja
        elif -2 < z_score <= 1:
            estado = "Peso Normal"
            color = "#388E3C"  # Verde
        elif 1 < z_score <= 2:
            estado = "Riesgo de Sobrepeso (entre +1 y +2 SD)"
            color = "#FBC02D"  # Amarillo
        elif 2 < z_score <= 3:
            estado = "Sobrepeso (entre +2 y +3 SD)"
            color = "#F57C00"  # Naranja
        else:
            estado = "Obesidad (> +3 SD)"
            color = "#D32F2F"  # Rojo
            
        # Lógica de proximidad para el rango de desnutrición
        proximidad = ""
        if -3 < z_score < -2:
            if z_score < -2.5:
                proximidad = f"⚠️ *Nota:* El valor está entre -2 y -3, pero su comportamiento clínico está **más cercano a -3 SD** ({z_score:.2f}). Se sugiere monitoreo estricto."
            else:
                proximidad = f"ℹ️ *Nota:* El valor está entre -2 y -3, tendiendo a acercarse a **-2 SD** ({z_score:.2f})."
        
        # Mostrar Resultados en la interfaz
        st.divider()
        st.subheader("Resultados de la Evaluación")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Talla ajustada a tabla:** {talla_ajustada} cm")
            st.write(f"**Peso analizado:** {peso_kg:.3f} kg")
        with col2:
            st.success(f"**Peso Ideal (Mediana):** {M:.2f} kg ({int(M * 1000)} g)")
            
        st.metric(label="Desviación Estándar (Z-Score)", value=f"{z_score:.2f}")
        
        st.markdown(f"<h3 style='color: {color};'>{estado}</h3>", unsafe_allow_html=True)
        
        if proximidad:
            st.markdown(proximidad)
