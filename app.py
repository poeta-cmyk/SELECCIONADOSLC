import random
import streamlit as st

st.set_page_config(page_title="Selección de la Liga de Campeones", layout="wide")

# Inicializar Estado de la Sesión
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "step" not in st.session_state:
    st.session_state.step = "login"
if "players" not in st.session_state:
    st.session_state.players = {}
if "round_num" not in st.session_state:
    st.session_state.round_num = 1
if "history_pairs" not in st.session_state:
    st.session_state.history_pairs = []

# --- PANTALLA 1: ACCESO ---
if not st.session_state.authenticated:
    st.title("Selección de la Liga de Campeones")
    password = st.text_input("Ingrese la clave de acceso:", type="password")
    if st.button("Ingresar"):
        if password == "LC1234":
            st.session_state.authenticated = True
            st.session_state.step = "register"
            st.rerun()
        else:
            st.error("Clave incorrecta. Intente de nuevo.")

# --- PANTALLA 2: REGISTRO DE 20 JUGADORES (2 Columnas) ---
elif st.session_state.step == "register":
    st.title("Selección de la Liga de Campeones - Registro de Jugadores")
    st.write("Ingrese los nombres de los 20 participantes:")

    col1, col2 = st.columns(2)
    player_names = {}

    with col1:
        st.subheader("Columna 1 (J1 - J10)")
        for i in range(1, 11):
            player_names[f"J{i}"] = st.text_input(f"J{i}", value=f"Jugador {i}", key=f"name_J{i}")

    with col2:
        st.subheader("Columna 2 (J11 - J20)")
        for i in range(11, 21):
            player_names[f"J{i}"] = st.text_input(f"J{i}", value=f"Jugador {i}", key=f"name_J{i}")

    if st.button("Generar la primera ronda"):
        st.session_state.players = {
            name: {
                "name": name,
                "jj": 0,
                "jg": 0,
                "jp": 0,
                "p_plus": 0,
                "p_minus": 0,
                "diff": 0,
            }
            for name in player_names.values()
        }
        st.session_state.player_keys = list(player_names.values())
        st.session_state.round_num = 1
        st.session_state.step = "round_1"
        st.rerun()

# --- MOTOR DE RONDAS Y AMONESTADOS ---
elif st.session_state.step.startswith("round_"):
    r_num = st.session_state.round_num
    st.title(f"Selección de la Liga de Campeones - Ronda {r_num}")

    # Sección Amonestados (Desplegable)
    with st.expander("⚠️ Jugadores Amonestados (Desplegar para señalar infracciones en esta ronda)"):
        st.write("Marque los jugadores que cometieron falta en esta ronda (-20 P(+) individuales):")
        round_penalties = {}
        for p in st.session_state.player_keys:
            round_penalties[p] = st.checkbox(p, key=f"pen_{r_num}_{p}")

    st.divider()
    st.subheader(f"Emparejamientos - Ronda {r_num}")

    # Lógica de emparejamiento estricta por ranking
    if r_num == 1:
        if f"tables_r{r_num}" not in st.session_state:
            shuffled = list(st.session_state.player_keys)
            random.shuffle(shuffled)
            st.session_state[f"tables_r{r_num}"] = [
                [shuffled[i], shuffled[i+1], shuffled[i+2], shuffled[i+3]]
                for i in range(0, 20, 4)
            ]
        current_tables = st.session_state[f"tables_r{r_num}"]
    else:
        if f"tables_r{r_num}" not in st.session_state:
            sorted_players = sorted(
                st.session_state.players.values(),
                key=lambda x: (x["jg"], x["diff"]),
                reverse=True
            )
            ranked_names = [p["name"] for p in sorted_players]

            current_tables = []
            for m in range(5):
                table_group = ranked_names[m*4 : (m*4)+4]
                p1 = table_group[0]
                candidates = table_group[1:]
                
                selected_p2 = None
                if r_num >= 4:
                    for cand in candidates:
                        if {p1, cand} not in st.session_state.history_pairs:
                            selected_p2 = cand
                            break
                
                if not selected_p2:
                    selected_p2 = candidates[0]
                
                rest = [c for c in candidates if c != selected_p2]
                p3, p4 = rest[0], rest[1]

                current_tables.append([p1, selected_p2, p3, p4])

            st.session_state[f"tables_r{r_num}"] = current_tables

        current_tables = st.session_state[f"tables_r{r_num}"]

    # Captura de resultados por mesa
    table_results = []
    for t_idx, table in enumerate(current_tables):
        st.markdown(f"### Mesa {t_idx + 1}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.text(f"Pareja A: {table[0]} & {table[1]}")
            score_a = st.number_input(f"Puntos Pareja A (Mesa {t_idx + 1})", 0, 1000, 0, key=f"score_a_{r_num}_{t_idx}")
        with col_b:
            st.text(f"Pareja B: {table[2]} & {table[3]}")
            score_b = st.number_input(f"Puntos Pareja B (Mesa {t_idx + 1})", 0, 1000, 0, key=f"score_b_{r_num}_{t_idx}")
        
        table_results.append({
            "pair_a": [table[0], table[1]],
            "score_a": score_a,
            "pair_b": [table[2], table[3]],
            "score_b": score_b
        })
        st.divider()

    btn_label = "Generar el Ranking" if r_num == 6 else f"Generar la ronda {r_num + 1}"
    if st.button(btn_label):
        for tr in table_results:
            pA1, pA2 = tr["pair_a"]
            pB1, pB2 = tr["pair_b"]
            sA, sB = tr["score_a"], tr["score_b"]

            st.session_state.history_pairs.append({pA1, pA2})
            st.session_state.history_pairs.append({pB1, pB2})

            for p in [pA1, pA2]:
                st.session_state.players[p]["jj"] += 1
                st.session_state.players[p]["p_plus"] += sA
                st.session_state.players[p]["p_minus"] += sB
            for p in [pB1, pB2]:
                st.session_state.players[p]["jj"] += 1
                st.session_state.players[p]["p_plus"] += sB
                st.session_state.players[p]["p_minus"] += sA

            for p in st.session_state.player_keys:
                if round_penalties.get(p, False):
                    st.session_state.players[p]["p_plus"] -= 20

            for p in st.session_state.player_keys:
                st.session_state.players[p]["diff"] = st.session_state.players[p]["p_plus"] - st.session_state.players[p]["p_minus"]

            a_won_board = sA > sB
            b_won_board = sB > sA

            if a_won_board:
                pA1_score_adj = sA - (20 if round_penalties.get(pA1, False) else 0)
                if pA1_score_adj <= sB:
                    st.session_state.players[pA1]["jp"] += 1
                else:
                    st.session_state.players[pA1]["jg"] += 1

                pA2_score_adj = sA - (20 if round_penalties.get(pA2, False) else 0)
                if pA2_score_adj <= sB:
                    st.session_state.players[pA2]["jp"] += 1
                else:
                    st.session_state.players[pA2]["jg"] += 1

                st.session_state.players[pB1]["jp"] += 1
                st.session_state.players[pB2]["jp"] += 1

            elif b_won_board:
                st.session_state.players[pA1]["jp"] += 1
                st.session_state.players[pA2]["jp"] += 1

                pB1_score_adj = sB - (20 if round_penalties.get(pB1, False) else 0)
                if pB1_score_adj <= sA:
                    st.session_state.players[pB1]["jp"] += 1
                else:
                    st.session_state.players[pB1]["jg"] += 1

                pB2_score_adj = sB - (20 if round_penalties.get(pB2, False) else 0)
                if pB2_score_adj <= sA:
                    st.session_state.players[pB2]["jp"] += 1
                else:
                    st.session_state.players[pB2]["jg"] += 1
            else:
                for p in [pA1, pA2, pB1, pB2]:
                    st.session_state.players[p]["jp"] += 1

    if r_num < 6:
        st.session_state.round_num += 1
        st.session_state.step = f"round_{st.session_state.round_num}"
        st.rerun()
    else:
        st.session_state.step = "ranking"
        st.rerun()

# --- PANTALLA 3: RANKING FINAL Y ANIMACIÓN ---
elif st.session_state.step == "ranking":
    st.title("🏆 Selección de la Liga de Campeones - Ranking Final")
    st.balloons()

    final_sorted = sorted(
        st.session_state.players.values(),
        key=lambda x: (x["jg"], x["diff"]),
        reverse=True
    )

    st.subheader("🎉 Podio de Ganadores")
    podium_cols = st.columns(3)
    medals = ["🥇 1er Lugar", "🥈 2do Lugar", "🥉 3er Lugar"]
    for idx in range(min(3, len(final_sorted))):
        with podium_cols[idx]:
            st.markdown(f"### {medals[idx]}")
            st.write(f"**{final_sorted[idx]['name']}**")
            st.write(f"JG: {final_sorted[idx]['jg']} | Dif: {final_sorted[idx]['diff']}")

    st.divider()
    st.subheader("Tabla General de Posiciones")

    table_data = []
    for rank, p in enumerate(final_sorted, 1):
        table_data.append({
            "Pos": rank,
            "Jugador": p["name"],
            "JJ": p["jj"],
            "JG": p["jg"],
            "JP": p["jp"],
            "P(+)": p["p_plus"],
            "P(-)": p["p_minus"],
            "Dif": p["diff"]
        })

    st.dataframe(table_data, use_container_width=True)
