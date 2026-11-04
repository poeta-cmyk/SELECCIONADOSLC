import streamlit as st

st.set_page_config(page_title="Selección de la Liga de Campeones", layout="wide")

CLAVE_CORRECTA = "1234"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "jugadores_registrados" not in st.session_state:
    st.session_state.jugadores_registrados = False
if "lista_jugadores" not in st.session_state:
    st.session_state.lista_jugadores = [f"Jugador {i}" for i in range(1, 21)]

# 1. Página de Control de Acceso
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

# 2. Registro de los 20 jugadores
elif not st.session_state.jugadores_registrados:
    st.title("🏆 Registro de Participantes")
    st.write("Ingrese los nombres de los exactamente **20 jugadores** para el torneo:")
    
    nombres_temporales = []
    for i in range(20):
        nombre = st.text_input(f"Jugador {i+1}", value=st.session_state.lista_jugadores[i], key=f"j_{i}")
        nombres_temporales.append(nombre)
        
    if st.button("Guardar Jugadores e Iniciar Torneo"):
        if len([n for n in nombres_temporales if n.strip() == ""]) > 0:
            st.error("Por favor, asegúrese de que todos los 20 campos tengan un nombre válido.")
        else:
        # Actualizamos la lista con los nombres introducidos
            st.session_state.lista_jugadores = nombres_temporales
            st.session_state.jugadores_registrados = True
            st.rerun()

# 3. Panel Principal del Torneo (Mesas y Parejas)
else:
    st.title("🏆 Selección de la Liga de Campeones - Panel del Torneo")
    st.success("¡Torneo activo con 20 jugadores configurados!")
    
    menu = st.radio("Seleccione una sección:", ["Ver Mesas", "Ver Parejas y Anotar Resultados"], horizontal=True)
    
    if menu == "Ver Mesas":
        st.subheader("🪑 Distribución en las 5 Mesas (Ronda Actual)")
        st.write("Aquí se visualizará cómo van ubicados los jugadores en las 4 o 5 mesas según corresponda.")
        
        # Ejemplo visual preliminar de las 5 mesas (4 jugadores por mesa)
        for m in range(1, 6):
            inicio = (m - 1) * 4
            fin = m * 4
            jugadores_mesa = st.session_state.lista_jugadores[inicio:fin]
            st.info(f"**Mesa {m}**: " + ", ".join(jugadores_mesa))
            
    elif menu == "Ver Parejas y Anotar Resultados":
        st.subheader("⚔️ Parejas de Enfrentamiento y Anotación")
        st.write("Aquí se mostrarán las parejas formadas para la ronda y los botones para registrar los puntajes.")
        
        # Muestra rápida de parejas base para la ronda
        for m in range(1, 6):
            inicio = (m - 1) * 4
            j = st.session_state.lista_jugadores[inicio:fin]
            st.write(f"**Mesa {m}**: [ {j[0]} y {j[1]} ] vs [ {j[2]} y {j[3]} ]")
            st.text_input(f"Resultado Mesa {m} (Ej: Ganan 1 y 2)", key=f"res_mesa_{m}")
            
    if st.button("Reiniciar Registro de Jugadores"):
        st.session_state.jugadores_registrados = False
        st.rerun()
      
