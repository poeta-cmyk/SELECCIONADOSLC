import streamlit as st
import pandas as pd

st.set_page_config(page_title="Selección de la Liga de Campeones", layout="wide")

CLAVE_CORRECTA = "LC1234"

# Inicializar estados
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "jugadores_registrados" not in st.session_state:
    st.session_state.jugadores_registrados = False
if "lista_jugadores" not in st.session_state:
    st.session_state.lista_jugadores = [f"Jugador {i}" for i in range(1, 21)]
if "ronda_actual" not in st.session_state:
    st.session_state.ronda_actual = 1
if "resultados_rondas" not in st.session_state:
    st.session_state.resultados_rondas = {}

# 1. Control de Acceso
if not st.session_state.autenticado:
    st.title("🏆 Selección de la Liga de Campeones")
    st.subheader("Control de Acceso")
    
    clave = st.text_input("Ingrese la clave de acceso:", type="password")
    
    if st.button("Ingresar"):
        if clave == CLAVE_CORRECTA:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Clave incorrecta. Intente nuevamente.")

# 2. Registro de Participantes (20 jugadores)
elif not st.session_state.jugadores_registrados:
    st.title("🏆 Registro de Participantes (20 Jugadores)")
    st.write("Ingrese los nombres de los jugadores:")
    
    nombres_temporales = []
    for i in range(20):
        nombre = st.text_input(f"Jugador {i+1}", value=st.session_state.lista_jugadores[i], key=f"j_{i}")
        nombres_temporales.append(nombre)
        
    if st.button("Guardar Jugadores e Iniciar Torneo"):
        if any(n.strip() == "" for n in nombres_temporales):
            st.error("Por favor, asegúrese de completar los 20 nombres.")
        else:
            st.session_state.lista_jugadores = nombres_temporales
            st.session_state.jugadores_registrados = True
            st.rerun()

# 3. Función de Rotación
def obtener_emparejamientos_ronda(jugadores, ronda):
    n = len(jugadores)
    idx = list(range(n))
    shift = (ronda - 1) % (n - 1)
    if shift > 0:
        idx = [idx[0]] + idx[1:][-shift:] + idx[1:][:-shift]
    
    mesas = []
    for m in range(5):
        m_idx = idx[m*4 : (m+1)*4]
        mesa_jugadores = [jugadores[i] for i in m_idx]
        mesas.append(mesa_jugadores)
    return mesas

# 4. Desarrollo del Torneo (Rondas 1 a 6 y Final)
else:
    ronda = st.session_state.ronda_actual
    
    if ronda <= 6:
        st.title(f"🏆 Ronda {ronda} de 6")
        
        mesas_ronda = obtener_emparejamientos_ronda(st.session_state.lista_jugadores, ronda)
        
        seccion = st.radio("Seleccione una sección:", ["Ver Posiciones en las Mesas", "Anotar Puntos de la Ronda"], horizontal=True)
        
        if seccion == "Ver Posiciones en las Mesas":
            st.subheader(f"🪑 Distribución en las 5 Mesas - Ronda {ronda}")
            
            for m in range(5):
                jugadores_mesa = mesas_ronda[m]
                with st.container():
                    st.markdown(f"### 🪑 Mesa {m+1}")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.info(f"**P1:** {jugadores_mesa[0]}")
                    c2.info(f"**P2:** {jugadores_mesa[1]}")
                    c3.info(f"**P3:** {jugadores_mesa[2]}")
                    c4.info(f"**P4:** {jugadores_mesa[3]}")
                    st.divider()
                        
        elif seccion == "Anotar Puntos de la Ronda":
            st.subheader(f"⚔️ Anotación de Puntos - Ronda {ronda}")
            
            with st.form(key=f"form_ronda_{ronda}"):
                for m in range(5):
                    j = mesas_ronda[m]
                    st.markdown(f"#### Mesa {m+1}")
                    st.write(f"🤝 **Pareja 1:** {j[0]} y {j[1]}  vs  🤝 **Pareja 2:** {j[2]} y {j[3]}")
                    
                    col1, col2 = st.columns(2)
                    col1.number_input(f"Puntos Pareja 1 (Mesa {m+1})", min_value=0, step=1, key=f"r{ronda}_m{m+1}_p1")
                    col2.number_input(f"Puntos Pareja 2 (Mesa {m+1})", min_value=0, step=1, key=f"r{ronda}_m{m+1}_p2")
                    st.divider()
                
                guardar_ronda = st.form_submit_button(f"Guardar Ronda {ronda} y Generar Siguiente")
                
                if guardar_ronda:
                    datos_ronda = {}
                    for m in range(5):
                        p1 = st.session_state.get(f"r{ronda}_m{m+1}_p1", 0)
                        p2 = st.session_state.get(f"r{ronda}_m{m+1}_p2", 0)
                        datos_ronda[m] = {"p1": p1, "p2": p2}
                    
                    st.session_state.resultados_rondas[ronda] = datos_ronda
                    
                    if ronda < 6:
                        st.session_state.ronda_actual += 1
                        st.success(f"¡Ronda {ronda} guardada con éxito! Generando ronda siguiente.")
                        st.rerun()
                    else:
                        st.session_state.ronda_actual = 7
                        st.rerun()
                        
    if ronda > 6:
        st.title("🏆 Torneo Finalizado - Resultados Generales")
        st.success("¡Se han completado las 6 rondas del torneo de forma exitosa!")
        st.subheader("📊 Tabla de Posiciones Finales")
        
        stats = {j: {"JJ": 6, "JG": 0, "JP": 0, "PF": 0, "PC": 0} for j in st.session_state.lista_jugadores}
        
        for r_num in range(1, 7):
            if r_num in st.session_state.resultados_rondas:
                mesas_r = obtener_emparejamientos_ronda(st.session_state.lista_jugadores, r_num)
                res_r = st.session_state.resultados_rondas[r_num]
                
                for m in range(5):
                    p1_pts = res_r[m]["p1"]
                    p2_pts = res_r[m]["p2"]
                    j = mesas_r[m]
                    
                    stats[j[0]]["PF"] += p1_pts
                    stats[j[0]]["PC"] += p2_pts
                    stats[j[1]]["PF"] += p1_pts
                    stats[j[1]]["PC"] += p2_pts
                    
                    stats[j[2]]["PF"] += p2_pts
                    stats[j[2]]["PC"] += p1_pts
                    stats[j[3]]["PF"] += p2_pts
                    stats[j[3]]["PC"] += p1_pts
                    
                    if p1_pts > p2_pts:
                        stats[j[0]]["JG"] += 1; stats[j[1]]["JG"] += 1
                        stats[j[2]]["JP"] += 1; stats[j[3]]["JP"] += 1
                    elif p2_pts > p1_pts:
                        stats[j[2]]["JG"] += 1; stats[j[3]]["JG"] += 1
                        stats[j[0]]["JP"] += 1; stats[j[1]]["JP"] += 1

        tabla_final = []
        for j, data in stats.items():
            dif = data["PF"] - data["PC"]
            avg = (data["PF"] / data["PC"]) if data["PC"] > 0 else data["PF"]
            tabla_final.append({
                "Jugador": j,
                "JJ": data["JJ"],
                "JG": data["JG"],
                "JP": data["JP"],
                "Puntos Favor": data["PF"],
                "Puntos Contra": data["PC"],
                "Diferencia": dif,
                "Average": round(avg, 3)
            })
        
        df_final = pd.DataFrame(tabla_final).sort_values(by=["JG", "Diferencia", "Average"], ascending=False).reset_index(drop=True)
        st.dataframe(df_final, use_container_width=True)
        
        if st.button("Reiniciar Torneo Completo"):
            st.session_state.jugadores_registrados = False
            st.session_state.ronda_actual = 1
            st.session_state.resultados_rondas = {}
            st.rerun()
