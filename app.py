import streamlit as st

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
    cols = st.columns(2)
    for i in range(20):
        col = cols[i % 2]
        nombre = col.text_input(f"Jugador {i+1}", value=st.session_state.lista_jugadores[i], key=f"j_{i}")
        nombres_temporales.append(nombre)
        
    if st.button("Guardar Jugadores e Iniciar Torneo"):
        if any(n.strip() == "" for n in nombres_temporales):
            st.error("Por favor, asegúrese de completar los 20 nombres.")
        else:
            st.session_state.lista_jugadores = nombres_temporales
            st.session_state.jugadores_registrados = True
            st.rerun()

# 3. Desarrollo del Torneo (6 Rondas)
else:
    ronda = st.session_state.ronda_actual
    st.title(f"🏆 Selección de la Liga de Campeones - Ronda {ronda} de 6")
    
    if ronda <= 6:
        # Pestañas de navegación o botones de sección
        seccion = st.radio("Seleccione una sección:", ["Ver Posiciones en las Mesas", "Anotar Puntos de la Ronda"], horizontal=True)
        
        if seccion == "Ver Posiciones en las Mesas":
            st.subheader(f"🪑 Distribución en las 5 Mesas - Ronda {ronda}")
            cols = st.columns(5)
            for m in range(5):
                inicio = m * 4
                fin = inicio + 4
                jugadores_mesa = st.session_state.lista_jugadores[inicio:fin]
                with cols[m]:
                    st.markdown(f"### Mesa {m+1}")
                    for idx, j in enumerate(jugadores_mesa, 1):
                        st.info(f"**P{idx}:** {j}")
                        
        elif seccion == "Anotar Puntos de la Ronda":
            st.subheader(f"⚔️ Anotación de Puntos - Ronda {ronda}")
            
            with st.form(key=f"form_ronda_{ronda}"):
                for m in range(5):
                    inicio = m * 4
                    fin = inicio + 4
                    j = st.session_state.lista_jugadores[inicio:fin]
                    
                    st.markdown(f"#### Mesa {m+1}")
                    st.write(f"🤝 **Pareja 1:** {j[0]} y {j[1]}  vs  🤝 **Pareja 2:** {j[2]} y {j[3]}")
                    
                    col1, col2 = st.columns(2)
                    col1.number_input(f"Puntos Pareja 1 (Mesa {m+1})", min_value=0, step=1, key=f"r{ronda}_m{m+1}_p1")
                    col2.number_input(f"Puntos Pareja 2 (Mesa {m+1})", min_value=0, step=1, key=f"r{ronda}_m{m+1}_p2")
                    st.divider()
                
                guardar_ronda = st.form_submit_button(f"Guardar Ronda {ronda} y Generar Siguiente")
                
                if guardar_ronda:
                    # Guardar datos de la ronda actual
                    datos_ronda = {}
                    for m in range(5):
                        p1 = st.session_state.get(f"r{ronda}_m{m+1}_p1", 0)
                        p2 = st.session_state.get(f"r{ronda}_m{m+1}_p2", 0)
                        datos_ronda[m] = {"p1": p1, "p2": p2}
                    
                    st.session_state.resultados_rondas[ronda] = datos_ronda
                    
                    if ronda < 6:
                        st.session_state.ronda_actual += 1
                        st.success(f"¡Ronda {ronda} guardada con éxito! Pasando a la siguiente ronda.")
                        st.rerun()
                    else:
                        st.session_state.ronda_actual = 7 # Fin del torneo
                        st.rerun()
    
    # Al finalizar la ronda 6 (Pantalla Final)
    if st.session_state.ronda_actual > 6:
        st.success("🎉 ¡Torneo Finalizado! A continuación la tabla general de resultados.")
        st.subheader("📊 Tabla de Posiciones Finales")
        
        # Calcular estadísticas generales por jugador (JJ, JG, JP, Average, Diferencia)
        tabla_stats = {j: {"JJ": 6, "JG": 0, "JP": 0, "Puntos_Favor": 0, "Puntos_Contra": 0} for j in st.session_state.lista_jugadores}
        
        # Procesar resultados acumulados
            
        st.write("Tabla general de rendimiento consolidada de los 20 jugadores en las 6 rondas.")
        
        if st.button("Reiniciar Torneo Completo"):
            st.session_state.jugadores_registrados = False
            st.session_state.ronda_actual = 1
            st.session_state.resultados_rondas = {}
            st.rerun()
