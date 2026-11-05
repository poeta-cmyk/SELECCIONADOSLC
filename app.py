import streamlit as st

st.set_page_config(page_title="Selección de la Liga de Campeones", layout="wide")

# Nueva clave de acceso
CLAVE_CORRECTA = "LC1234"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "jugadores_registrados" not in st.session_state:
    st.session_state.jugadores_registrados = False
if "lista_jugadores" not in st.session_state:
    st.session_state.lista_jugadores = [f"Jugador {i}" for i in range(1, 21)]

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

# 2. Registro de Participantes (20 jugadores exactos)
elif not st.session_state.jugadores_registrados:
    st.title("🏆 Registro de Participantes")
    st.write("Ingrese los nombres de los 20 jugadores:")
    
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

# 3. Panel del Torneo
else:
    st.title("🏆 Selección de la Liga de Campeones")
    
    menu = st.radio("Seleccione una opción:", ["Ver Mesas", "Ver Parejas y Anotar Resultados"], horizontal=True)
    
    if menu == "Ver Mesas":
        st.subheader("🪑 Distribución en las 5 Mesas")
        
        cols = st.columns(5)
        for m in range(5):
            inicio = m * 4
            fin = inicio + 4
            jugadores_mesa = st.session_state.lista_jugadores[inicio:fin]
            
            with cols[m]:
                st.markdown(f"### Mesa {m+1}")
                for idx, j in enumerate(jugadores_mesa, 1):
                    st.info(f"**P{idx}:** {j}")
            
    elif menu == "Ver Parejas y Anotar Resultados":
        st.subheader("⚔️ Parejas y Anotación de Puntajes")
        
        for m in range(5):
            inicio = m * 4
            fin = inicio + 4
            j = st.session_state.lista_jugadores[inicio:fin]
            
            with st.container():
                st.markdown(f"#### Mesa {m+1}")
                st.write(f"🤝 **Pareja 1:** {j[0]} y {j[1]}")
                st.write(f"🤝 **Pareja 2:** {j[2]} y {j[3]}")
                
                col1, col2 = st.columns(2)
                col1.number_input(f"Puntos Pareja 1 (Mesa {m+1})", min_value=0, step=1, key=f"p1_m{m+1}")
                col2.number_input(f"Puntos Pareja 2 (Mesa {m+1})", min_value=0, step=1, key=f"p2_m{m+1}")
                st.divider()
            
    if st.button("Reiniciar Registro de Jugadores"):
        st.session_state.jugadores_registrados = False
        st.rerun()
