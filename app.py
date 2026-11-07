import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN Y ESTILOS DE LA APLICACIÓN
# ==========================================
st.set_page_config(page_title="Selección de la Liga de Campeones", layout="wide")

st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1E3A8A;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #4B5563;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DEL ESTADO DE LA SESIÓN
# ==========================================
if 'players' not in st.session_state:
    st.session_state.players = [f"Jugador {i+1}" for i in range(20)]

if 'round_num' not in st.session_state:
    st.session_state.round_num = 1

if 'tournament_history' not in st.session_state:
    # Almacena los datos y emparejamientos de cada ronda
    st.session_state.tournament_history = {}

if 'penalties' not in st.session_state:
    # Estructura: {round_num: {player_name: penalty_points}}
    st.session_state.penalties = {}

if 'pairs_history' not in st.session_state:
    # Conjunto para rastrear parejas que ya jugaron juntas: set(frozenset([p1, p2]))
    st.session_state.pairs_history = set()

# ==========================================
# FUNCIONES DE LÓGICA DE TORNEO Y RANKING
# ==========================================
def calculate_ranking():
    """Calcula la tabla de posiciones acumulada con baremos: JG -> DP -> PF"""
    stats = {p: {'JG': 0, 'JP': 0, 'PF': 0, 'PC': 0, 'DP': 0, 'Penalties': 0} for p in st.session_state.players}
    
    # Acumular penalizaciones registradas
    for r, pen_dict in st.session_state.penalties.items():
        for player, pts in pen_dict.items():
            if player in stats:
                stats[player]['Penalties'] += pts

    # Procesar historial de rondas jugadas
    for r in range(1, st.session_state.round_num):
        if r in st.session_state.tournament_history:
            round_data = st.session_state.tournament_history[r]
            for match in round_data:
                pair1, pair2 = match['pair1'], match['pair2']
                score1, score2 = match['score1'], match['score2']
                
                # Descuento directo por penalización en la ronda actual si existió
                p1_pen = st.session_state.penalties.get(r, {}).get(pair1[0], 0) + st.session_state.penalties.get(r, {}).get(pair1[1], 0)
                p2_pen = st.session_state.penalties.get(r, {}).get(pair2[0], 0) + st.session_state.penalties.get(r, {}).get(pair2[1], 0)
                
                adj_score1 = max(0, score1 - p1_pen)
                adj_score2 = max(0, score2 - p2_pen)
                
                # Pareja 1
                for p in pair1:
                    stats[p]['PF'] += adj_score1
                    stats[p]['PC'] += adj_score2
                    if adj_score1 > adj_score2:
                        stats[p]['JG'] += 1
                    else:
                        stats[p]['JP'] += 1
                
                # Pareja 2
                for p in pair2:
                    stats[p]['PF'] += adj_score2
                    stats[p]['PC'] += adj_score1
                    if adj_score2 > adj_score1:
                        stats[p]['JG'] += 1
                    else:
                        stats[p]['JP'] += 1

    for p in stats:
        stats[p]['DP'] = stats[p]['PF'] - stats[p]['PC']

    # Convertir a DataFrame y ordenar estrictamente según los baremos
    df = pd.DataFrame.from_dict(stats, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Jugador'}, inplace=True)
    df.sort_values(by=['JG', 'DP', 'PF'], ascending=[False, False, False], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.index = df.index + 1  # Posición 1 a 20
    return df

def generate_swiss_pairings(ranking_df):
    """
    Genera los cruces Suizos estrictos: 
    Mesa 1: 1º y 3º vs 2º y 4º; Mesa 2: 5º y 7º vs 6º y 8º.
    Aplica permutación si se detecta pareja repetida.
    """
    ordered_players = ranking_df['Jugador'].tolist()
    available = ordered_players.copy()
    pairings = []

    while len(available) >= 4:
        # Intentar cruce estándar (1º con 3º vs 2º con 4º)
        p1 = available[0]
        p2 = available[1]
        p3 = available[2]
        p4 = available[3]

        # Validar si (p1, p3) o (p2, p4) ya jugaron juntos
        if frozenset([p1, p3]) in st.session_state.pairs_history or frozenset([p2, p4]) in st.session_state.pairs_history:
            # Buscar permutación óptima con el siguiente disponible en el ranking
            swap_done = False
            for i in range(4, len(available)):
                alt_p = available[i]
                if frozenset([p1, alt_p]) not in st.session_state.pairs_history and frozenset([p2, p3]) not in st.session_state.pairs_history:
                    # Intercambiar p3 con alt_p
                    available[2], available[i] = available[i], available[2]
                    p3 = available[2]
                    swap_done = True
                    break
            if not swap_done:
                # Si no se puede permutar p3, intentar ajustar p4
                for i in range(4, len(available)):
                    alt_p = available[i]
                    if frozenset([p2, alt_p]) not in st.session_state.pairs_history:
                        available[3], available[i] = available[i], available[3]
                        p4 = available[3]
                        break

        # Confirmar formación de la mesa
        pair1 = (p1, p3)
        pair2 = (p2, p4)
        
        pairings.append({'pair1': pair1, 'pair2': pair2})
        
        # Registrar parejas formadas
        st.session_state.pairs_history.add(frozenset(pair1))
        st.session_state.pairs_history.add(frozenset(pair2))

        # Remover de los disponibles
        for p in [p1, p2, p3, p4]:
            available.remove(p)

    return pairings

# ==========================================
# INTERFAZ DE USUARIO PRINCIPAL
# ==========================================
st.markdown("<h1 class='main-title'>🀄 Selección de la Liga de Campeones</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='sub-title'>Sistema de Gestión de Torneos de Dominó | Ronda Actual: <b>{st.session_state.round_num} / 6</b></p>", unsafe_allow_html=True)

# Vista de Ranking acumulado actual accesible en todo momento
with st.expander("📊 Ver Ranking y Tabla de Posiciones Acumulada", expanded=False):
    current_ranking = calculate_ranking()
    st.dataframe(current_ranking, use_container_width=True)

st.divider()

# ------------------------------------------
# SECCIÓN DE RONDAS (1 a 6)
# ------------------------------------------
current_r = st.session_state.round_num

if current_r <= 6:
    st.subheader(f"📋 Registro de Resultados - Ronda {current_r}")

    # Generar emparejamientos si no existen para la ronda actual
    if current_r not in st.session_state.tournament_history:
        if current_r == 1:
            # Ronda 1: Emparejamiento inicial directo/manual según lista de registro
            r1_players = st.session_state.players
            pairings = []
            for i in range(0, 20, 4):
                pairings.append({
                    'pair1': (r1_players[i], r1_players[i+2]),
                    'pair2': (r1_players[i+1], r1_players[i+3])
                })
            st.session_state.tournament_history[1] = pairings
        else:
            # Rondas 2 a 6: Emparejamiento Suizo estricto guiado por Ranking
            rk_df = calculate_ranking()
            st.session_state.tournament_history[current_r] = generate_swiss_pairings(rk_df)

    active_matches = st.session_state.tournament_history[current_r]

    # Formulario para ingresar anotaciones por Mesa
    with st.form(key=f"form_round_{current_r}"):
        scores = []
        for idx, match in enumerate(active_matches):
            st.markdown(f"##### 🀠 Mesa {idx + 1}")
            c1, c2, c3 = st.columns([3, 1, 3])
            
            with c1:
                st.write(f"**Pareja A:** {match['pair1'][0]} & {match['pair1'][1]}")
                s1 = st.number_input(f"Puntos Pareja A (Mesa {idx+1})", min_value=0, max_value=200, value=0, step=1, key=f"r{current_r}_m{idx}_s1")
            
            with c2:
                st.markdown("<h4 style='text-align: center; margin-top: 25px;'>VS</h4>", unsafe_allow_html=True)
            
            with c3:
                st.write(f"**Pareja B:** {match['pair2'][0]} & {match['pair2'][1]}")
                s2 = st.number_input(f"Puntos Pareja B (Mesa {idx+1})", min_value=0, max_value=200, value=0, step=1, key=f"r{current_r}_m{idx}_s2")
            
            scores.append((s1, s2))
            st.divider()

        # ------------------------------------------
        # PUNTO 1: AMONESTACIONES Y DESCUENTOS DIRECTOS
        # ------------------------------------------
        st.markdown("#### ⚠️ Amonestaciones y Penalizaciones de la Ronda")
        with st.expander("Desplegar panel para registrar descuentos por amonestación", expanded=False):
            st.info("Escriba el monto exacto en puntos a descontar por cada infracción cometida por el jugador en esta ronda.")
            current_penalties = st.session_state.penalties.get(current_r, {})
            updated_penalties = {}
            
            cols = st.columns(4)
            for i, player in enumerate(st.session_state.players):
                with cols[i % 4]:
                    val = current_penalties.get(player, 0)
                    pts_to_deduct = st.number_input(
                        f"Descuento a {player}", 
                        min_value=0, 
                        max_value=200, 
                        value=val, 
                        step=5, 
                        key=f"pen_{current_r}_{player}"
                    )
                    if pts_to_deduct > 0:
                        updated_penalties[player] = pts_to_deduct

        st.markdown("<br>", unsafe_allow_html=True)
        
        # ------------------------------------------
        # PUNTO 2: BOTÓN DE RETROCESO Y AVANCE SIMÉTRICOS
        # ------------------------------------------
        col_back, col_space, col_next = st.columns([2, 1, 2])
        
        with col_back:
            if current_r > 1:
                btn_back = st.form_submit_button("⬅️ Volver a la Ronda Anterior")
            else:
                btn_back = False

        with col_next:
            btn_next = st.form_submit_button("Guardar y Avanzar a la Siguiente Ronda ➡️")

    # Procesar acciones de navegación del formulario
    if btn_back:
        st.session_state.round_num -= 1
        st.rerun()

    if btn_next:
        # Guardar penalizaciones en sesión
        st.session_state.penalties[current_r] = updated_penalties
        
        # Guardar puntuaciones en el historial
        for idx, (s1, s2) in enumerate(scores):
            st.session_state.tournament_history[current_r][idx]['score1'] = s1
            st.session_state.tournament_history[current_r][idx]['score2'] = s2

        st.session_state.round_num += 1
        st.rerun()

else:
    # ------------------------------------------
    # PANTALLA FINAL DE PODIO Y RESULTADOS
    # ------------------------------------------
    st.balloons()
    st.success("🏆 ¡El torneo ha finalizado con éxito!")
    
    final_ranking = calculate_ranking()
    
    st.markdown("### 🥇 Podio de Campeones")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🥇 Primer Lugar (Campeón)", final_ranking.iloc[0]['Jugador'], f"{final_ranking.iloc[0]['JG']} JG | DP: {final_ranking.iloc[0]['DP']}")
    with col2:
        st.metric("🥈 Segundo Lugar", final_ranking.iloc[1]['Jugador'], f"{final_ranking.iloc[1]['JG']} JG | DP: {final_ranking.iloc[1]['DP']}")
    with col3:
        st.metric("🥉 Tercer Lugar", final_ranking.iloc[2]['Jugador'], f"{final_ranking.iloc[2]['JG']} JG | DP: {final_ranking.iloc[2]['DP']}")
        
    st.divider()
    st.markdown("### 📊 Tabla de Posiciones Final Completa")
    st.dataframe(final_ranking, use_container_width=True)

    if st.button("⬅️ Volver a la Ronda 6 para consultar o modificar datos"):
        st.session_state.round_num = 6
        st.rerun()
