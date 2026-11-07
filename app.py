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
    st.session_state.tournament_history = {}

if 'penalties' not in st.session_state:
    st.session_state.penalties = {}

if 'pairs_history' not in st.session_state:
    st.session_state.pairs_history = set()

# ==========================================
# FUNCIONES DE LÓGICA DE TORNEO Y RANKING
# ==========================================
def calculate_ranking():
    stats = {p: {'JG': 0, 'JP': 0, 'PF': 0, 'PC': 0, 'DP': 0, 'Penalties': 0} for p in st.session_state.players}
    
    for r, pen_dict in st.session_state.penalties.items():
        for player, pts in pen_dict.items():
            if player in stats:
                stats[player]['Penalties'] += pts

    for r in range(1, st.session_state.round_num):
        if r in st.session_state.tournament_history:
            round_data = st.session_state.tournament_history[r]
            for match in round_data:
                pair1, pair2 = match['pair1'], match['pair2']
                score1, score2 = match['score1'], match['score2']
                
                for p in pair1:
                    stats[p]['PF'] += score1
                    stats[p]['PC'] += score2
                    if score1 > score2:
                        stats[p]['JG'] += 1
                    else:
                        stats[p]['JP'] += 1
                
                for p in pair2:
                    stats[p]['PF'] += score2
                    stats[p]['PC'] += score1
                    if score2 > score1:
                        stats[p]['JG'] += 1
                    else:
                        stats[p]['JP'] += 1

    for p in stats:
        stats[p]['DP'] = stats[p]['PF'] - stats[p]['PC']

    df = pd.DataFrame.from_dict(stats, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Jugador'}, inplace=True)
    df.sort_values(by=['JG', 'DP', 'PF'], ascending=[False, False, False], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.index = df.index + 1
    return df

# ==========================================
# INTERFAZ DE USUARIO PRINCIPAL
# ==========================================
st.markdown("<h1 class='main-title'>🀄 Selección de la Liga de Campeones</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='sub-title'>Sistema de Gestión de Torneos de Dominó | Ronda Actual: <b>{st.session_state.round_num} / 6</b></p>", unsafe_allow_html=True)

with st.expander("📊 Ver Ranking y Tabla de Posiciones Acumulada", expanded=False):
    current_ranking = calculate_ranking()
    st.dataframe(current_ranking, use_container_width=True)

st.divider()

current_r = st.session_state.round_num

if current_r <= 6:
    st.subheader(f"📋 Registro de Resultados - Ronda {current_r}")

    if current_r not in st.session_state.tournament_history:
        if current_r == 1:
            r1_players = st.session_state.players
            pairings = []
            for i in range(0, 20, 4):
                pairings.append({
                    'pair1': (r1_players[i], r1_players[i+2]),
                    'pair2': (r1_players[i+1], r1_players[i+3])
                })
            st.session_state.tournament_history[1] = pairings
        else:
            rk_df = calculate_ranking()
            ordered_players = rk_df['Jugador'].tolist()
            pairings = []
            for i in range(0, 20, 4):
                pairings.append({
                    'pair1': (ordered_players[i], ordered_players[i+2]),
                    'pair2': (ordered_players[i+1], ordered_players[i+3])
                })
            st.session_state.tournament_history[current_r] = pairings

    active_matches = st.session_state.tournament_history[current_r]

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

        st.markdown("#### ⚠️ Amonestaciones")
        with st.expander("Desplegar panel de amonestaciones", expanded=False):
            current_penalties = st.session_state.penalties.get(current_r, {})
            updated_penalties = {}
            cols = st.columns(4)
            for i,
