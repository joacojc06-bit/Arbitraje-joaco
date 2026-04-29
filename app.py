import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="JC Studio - Arbitraje", layout="centered")
st.title("⚽ JC Studio - Global Scanner")

API_KEY = 'dd57844b14a3ad7ec676b31840176d9e'
ARG_TIME = pytz.timezone('America/Argentina/Buenos_Aires')
CAPITAL = st.sidebar.number_input("Capital Total ($)", value=100000)

CASAS_LOCALES = ['Betsson', 'Betwarrior', 'Codere', 'bplay', '1xBet', 'Pinnacle', 'Bet365', 'Betfair']

def escanear_global():
    oportunidades = []
    try:
        res_dep = requests.get(f'https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}')
        lista_deportes = res_dep.json()
    except: return []

    for depo in lista_deportes[:20]:
        sport_key = depo['key']
        url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={API_KEY}&regions=la,us&markets=h2h'
        try:
            data = requests.get(url).json()
            for juego in data:
                home, away = juego['home_team'], juego['away_team']
                mejores, bookies = {}, {}
                for b in juego['bookmakers']:
                    if b['title'] in CASAS_LOCALES:
                        m = b['markets'][0]['outcomes']
                        for o in m:
                            if o['name'] not in mejores or o['price'] > mejores[o['name']]:
                                mejores[o['name']] = o['price']
                                bookies[o['name']] = b['title']
                
                if len(mejores) >= 2:
                    inv = sum(1/p for p in mejores.values())
                    if inv < 0.99:
                        profit = (1 - inv) * 100
                        res = {"Evento": f"{home} vs {away}", "Deporte": depo['title'], "Profit": f"{profit:.2f}%"}
                        inst = ""
                        for n, c in mejores.items():
                            monto = round((CAPITAL / (c * inv)) / 100) * 100
                            inst += f"**{n}**: ${monto} en *{bookies[n]}* (@{c}) \n\n"
                        res["Guía"] = inst
                        oportunidades.append(res)
        except: continue
    return oportunidades

if st.button('🚀 ANALIZAR MERCADO AHORA'):
    with st.spinner('Buscando ineficiencias...'):
        resultados = escanear_global()
        if resultados:
            st.success(f"¡Se encontraron {len(resultados)} oportunidades!")
            for r in resultados:
                with st.expander(f"📈 {r['Profit']} - {r['Evento']} ({r['Deporte']})"):
                    st.markdown(r['Guía'])
        else:
            st.info("No hay ineficiencias ahora. Reintentá en unos minutos.")

st.sidebar.write(f"Hora Arg: {datetime.now(ARG_TIME).strftime('%H:%M:%S')}")
