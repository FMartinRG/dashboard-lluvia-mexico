#Recordatorio

# Cada vez que reinicies el equipo o abras una nueva terminal, activa el entorno con:

# cd ~/Escritorio
# source env/bin/activate


# archivo: dashboard_lluvia_mexico.py

# dashboard_lluvia_mexico.py
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
import os

# ==================== CONFIG ====================
API_KEY = "21473527536f18d480757d52653c548f"  # Ingresa tu API Key válida
MAPBOX_TOKEN = "open-street-map"  # se úede sustituir con "carto-positron" 

# ================= ESTADOS MÉXICO ======================
estados = [
    {"Estado": "Aguascalientes", "Lat": 21.8853, "Lon": -102.2916},
    {"Estado": "Baja California", "Lat": 32.5149, "Lon": -117.0382},
    {"Estado": "Baja California Sur", "Lat": 24.1426, "Lon": -110.3128},
    {"Estado": "Campeche", "Lat": 19.8450, "Lon": -90.5235},
    {"Estado": "CDMX", "Lat": 19.4326, "Lon": -99.1332},
    {"Estado": "Chiapas", "Lat": 16.75, "Lon": -93.1167},
    {"Estado": "Chihuahua", "Lat": 28.6353, "Lon": -106.0889},
    {"Estado": "Coahuila", "Lat": 25.4382, "Lon": -100.9737},
    {"Estado": "Colima", "Lat": 19.2433, "Lon": -103.7241},
    {"Estado": "Durango", "Lat": 24.0277, "Lon": -104.6532},
    {"Estado": "Estado de México", "Lat": 19.2921, "Lon": -99.6534},
    {"Estado": "Guanajuato", "Lat": 21.0190, "Lon": -101.2574},
    {"Estado": "Guerrero", "Lat": 17.5537, "Lon": -99.5058},
    {"Estado": "Hidalgo", "Lat": 20.1011, "Lon": -98.7591},
    {"Estado": "Jalisco", "Lat": 20.6597, "Lon": -103.3496},
    {"Estado": "Michoacán", "Lat": 19.7008, "Lon": -101.1844},
    {"Estado": "Morelos", "Lat": 18.6813, "Lon": -99.1013},
    {"Estado": "Nayarit", "Lat": 21.7514, "Lon": -104.8455},
    {"Estado": "Nuevo León", "Lat": 25.6866, "Lon": -100.3161},
    {"Estado": "Oaxaca", "Lat": 17.0732, "Lon": -96.7266},
    {"Estado": "Puebla", "Lat": 19.0414, "Lon": -98.2063},
    {"Estado": "Querétaro", "Lat": 20.5888, "Lon": -100.3899},
    {"Estado": "Quintana Roo", "Lat": 21.1619, "Lon": -86.8515},
    {"Estado": "San Luis Potosí", "Lat": 22.1565, "Lon": -100.9855},
    {"Estado": "Sinaloa", "Lat": 24.8091, "Lon": -107.3940},
    {"Estado": "Sonora", "Lat": 29.0729, "Lon": -110.9559},
    {"Estado": "Tabasco", "Lat": 17.9895, "Lon": -92.9475},
    {"Estado": "Tamaulipas", "Lat": 23.7369, "Lon": -99.1411},
    {"Estado": "Tlaxcala", "Lat": 19.3139, "Lon": -98.2404},
    {"Estado": "Veracruz", "Lat": 19.1738, "Lon": -96.1342},
    {"Estado": "Yucatán", "Lat": 20.97, "Lon": -89.62},
    {"Estado": "Zacatecas", "Lat": 22.7709, "Lon": -102.5832},
]

# ================= FUNCIONES =====================
def obtener_lluvia_actual(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
    r = requests.get(url, params=params).json()
    lluvia = r.get("rain", {}).get("1h")
    if lluvia is None:
        lluvia = 0.0
    return round(lluvia, 2)

def obtener_pronostico(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
    r = requests.get(url, params=params).json()
    forecast = r.get("list", [])
    datos = []
    for f in forecast:
        fecha = datetime.fromtimestamp(f["dt"])
        if fecha.hour == 12:
            datos.append({
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Temp Max": f["main"]["temp_max"],
                "Temp Min": f["main"]["temp_min"],
                "Lluvia (mm)": f.get("rain", {}).get("3h", 0),
                "Descripción": f["weather"][0]["description"]
            })
        if len(datos) == 3:
            break
    return pd.DataFrame(datos)

# ================ DASHBOARD =================
st.set_page_config(page_title="Lluvia en México Tiempo Real y Pronóstico", layout="wide")
st.title("Dashboard de Precipitación en México en Tiempo Real y Pronóstico")

# Obtener datos actuales
datos = []
for e in estados:
    lluvia = obtener_lluvia_actual(e["Lat"], e["Lon"])
    datos.append({**e, "Lluvia (mm)": lluvia})

df = pd.DataFrame(datos)
df["Texto Hover"] = df.apply(
    lambda row: f"{row['Estado']}<br>Lluvia: {row['Lluvia (mm)']} mm" if row["Lluvia (mm)"] > 0 else f"{row['Estado']}<br>Sin lluvia",
    axis=1
)
fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
df["Fecha"] = fecha

# Guardar histórico
os.makedirs("historico", exist_ok=True)
archivo = "historico/lluvia_mexico.csv"
if os.path.exists(archivo):
    df.to_csv(archivo, mode="a", index=False, header=False)
else:
    df.to_csv(archivo, index=False)

# Estado seleccionado
estado_sel = st.selectbox("Selecciona un estado:", df["Estado"])
lat_sel = df[df["Estado"] == estado_sel]["Lat"].values[0]
lon_sel = df[df["Estado"] == estado_sel]["Lon"].values[0]

# Mapa
df["Color"] = df["Estado"].apply(lambda x: "lightcoral" if x == estado_sel else "aquamarine")
fig = px.scatter_mapbox(
    df, lat="Lat", lon="Lon", color="Color", size="Lluvia (mm)",
    hover_name="Texto Hover",
    hover_data={"Lluvia (mm)": True, "Lat": False, "Lon": False, "Color": False},
    size_max=20, zoom=4, mapbox_style=MAPBOX_TOKEN
)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# Pronóstico
st.subheader(f"₍^. .^₎⟆ Pronóstico en {estado_sel} (3 días)")
pronostico = obtener_pronostico(lat_sel, lon_sel)
st.dataframe(pronostico, use_container_width=True)

# Histórico
st.subheader(f"ᓚ₍⑅^..^₎♡ Histórico de precipitación en {estado_sel}")
hist = pd.read_csv(archivo, on_bad_lines='skip')  # pandas >=1.3.0
hist["Fecha"] = pd.to_datetime(hist["Fecha"])
estado_hist = hist[hist["Estado"] == estado_sel].sort_values("Fecha")
st.line_chart(estado_hist.set_index("Fecha")["Lluvia (mm)"])

# Exportar
st.subheader("📤 Exportar histórico")
col1, col2 = st.columns(2)
with col1:
    st.download_button("⬇▶︎ •၊၊||၊|။|||| | Descargar Excel", estado_hist.to_csv(index=False).encode(),
                       file_name=f"historico_{estado_sel}.csv")
with col2:
    all_data = hist.sort_values(["Estado", "Fecha"])
    st.download_button("⬇▶︎ •၊၊||၊|။|||| | Todos los estados", all_data.to_csv(index=False).encode(),
                       file_name="lluvia_mexico_completo.csv")
    
