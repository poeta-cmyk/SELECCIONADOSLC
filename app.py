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
if "penalties_history" not in st.session_state:
    st.session_state.penalties_history = {}

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

# --- PANTALLA 2: REGISTRO DE 20 JUGADORES Y OPCIÓN MANUAL ---
elif st.session_state.step == "register":
    st.title("Selección de la Liga de Campeones - Registro y Configuración Inicial")
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

    st.divider()
    st.subheader("Modo de inicio de la Primera Ronda")

    b_col1, b_col2 = st.columns(2)

    with b_col1:
        if st.button("🎲 Generar primera ronda (Automática / Sorteo)"):
            names_list = list(player_names.values())
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
                for name in names_list
            }
            st.session_state.player_keys = names_list
            random.shuffle(names_list)
            st.session_state["tables_r1"] = [
                [names_list[i], names_list[i+1], names_list[i+2], names_list[i+3]]
                for i in range(0, 20, 4)
            ]
            st.session_state.round_num = 1
            st.session_state.step = "round_1"
            st.rerun()

    with b_col2:
        if st.button("🛠️ Generar ronda manualmente"):
            st.session_state.modo_manual = True
            st.rerun()

    if st.session_state.get("modo_manual", False):
        st.info("Asigne los jugadores manualmente para cada una de las 5 mesas de la primera ronda:")
        all_names = list(player_names.values())
        manual_tables = []

        for m in range(5):
            st.markdown(f"**Mesa {m+1}**")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1:
                p1 = st.selectbox(f"M{m+1} - J1", all_names, key=f"m_{m}_p1")
            with m_col2:
                p2 = st.selectbox(f"M{m+1} - J2", all_names, key=f"m_{m}_p2")
            with m_col3:
                p3 = st.selectbox(f"M{m+1} - J3", all_names, key=f"m_{m}_p3")
            with m_col4:
                p4 = st.selectbox(f"M{m+1} - J4", all_names, key=f"m_{m}_p4")
            manual_tables.append([p1, p2, p3, p4])

        if st.button("✅ Guardar mesas manuales e iniciar torneo"):
            flat_manual = [p for mesa in manual_tables for p in mesa]
            if len(set(flat_manual)) < 20:
                st.error("Error: Hay jugadores repetidos en las mesas. Cada uno debe ser único.")
            else:
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
                    for name in all_names
                }
                st.session_state.player_keys = all_names
                st.session_state["tables_r1"] = manual_tables
                st.session_state.round_num = 1
                st.session_state.step = "round_1"
                st.rerun()

# --- MOTOR DE RONDAS Y AMONESTADOS ---
elif st.session_state.step.startswith("round_"):
    r_num = st.session_state.round_num
    st.title(f"Selección de la Liga de Campeones - Ronda {r_num} de 6")

    # Botón de Ranking Acumulado accesible en todo momento
    with st.expander("📊 Ver Ranking y Tabla de Posiciones Acumulada"):
        sorted_preview = sorted(
            st.session_state.players.values(),
            key=lambda x: (x["jg"], x["diff"]),
            reverse=True
        )
        preview_data = [{"Pos": i+1, "Jugador": p["name"], "JG": p["jg"], "JP": p["jp"], "Dif": p["diff"]} for i, p in enumerate(sorted_preview)]
        st.dataframe(preview_data, use_container_width=True)

    # Sección Amonestados con monto libre/personalizado
    with st.expander("⚠️ Jugadores Amonestados (Desplegar para registrar descuentos personalizados en esta ronda)"):
        st.write("Anote el monto exacto del descuento en puntos para cada jugador infractor en esta ronda:")
        round_penalties = {}
        cols_pen = st.columns(4)
        for idx_p, p in enumerate(st.session_state.player_keys):
            with cols_pen[idx_p % 4]:
                current_val = st.session_state.get("penalties_history", {}).get(r_num, {}).get(p, 0)
                pen_val = st.number_input(f"{p}", min_value=0, max_value=200, value=current_val, step=5, key=f"pen_{r_num}_{p}")
                if pen_val > 0:
                    round_penalties[p] = pen_val

    st.divider()
    st.subheader(f"Emparejamientos - Ronda {r_num}")

    table_key_cache = f"tables_r{r_num}"
    if table_key_cache not in st.session_state:
        if r_num == 1:
            shuffled = list(st.session_state.player_keys)
            random.shuffle(shuffled)
            st.session_state[table_key_cache] = [
                [shuffled[i], shuffled[i+1], shuffled[i+2], shuffled[i+3]]
                for i in range(0, 20, 4)
            ]
        else:
            sorted_players = sorted(
                st.session_state.players.values(),
                key=lambda x: (x["jg"], x["diff"]),
                reverse=True
            )
            ranked_names = [p["name"] for p in sorted_players]

            current_tables = []
            for m in range(5):
                table_group = ranked_names[m*4 : (m*4)+4]
                # Emparejamiento interno estricto: 1º con 3º y 2º con 4º
                p1 = table_group[0]
                p2 = table_group[1]
                p3 = table_group[2]
                p4 = table_group[3]

                # Control de repetición de pareja (Swiss pairing refinement)
                if frozenset([p1, p3]) in st.session_state.history_pairs or frozenset([p2, p4]) in st.session_state.history_pairs:
                    # Buscar alternativa en el grupo o intercambiar
                    for alt_idx in range(len(table_group)):
                        for alt_idx2 in range(alt_idx + 1, len(table_group)):
                            cand1 = table_group[alt_idx]
                            cand2 = table_group[alt_idx2]
                            if frozenset([cand1, cand2]) not in st.session_state.history_pairs:
                                p1, p3 = cand1, cand2
                                remaining = [x for x in table_group if x not in [p1, p3]]
                                p2, p4 = remaining[0], remaining[1]
                                break

                current_tables.append([p1, p3, p2, p4])

            st.session_state[table_key_cache] = current_tables

    current_tables = st.session_state[table_key_cache]

    # Captura de resultados por mesa dentro de un formulario para incluir los botones simétricos
    with st.form(key=f"form_round_{r_num}"):
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

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botones simétricos: Retroceso al lado de Avanzar
        col_back, col_space, col_next = st.columns([2, 1, 2])
        
        with col_back:
            btn_back = st.form_submit_button("⬅️ Volver a la Ronda Anterior") if r_num > 1 else False

        with col_next:
            btn_label = "Generar el Ranking Final" if r_num == 6 else f"Procesar Ronda {r_num} y Avanzar"
            btn_next_action = st.form_submit_button(f"{btn_label} ➡️")

    # Procesar lógica de retroceso
    if btn_back:
        st.session_state.round_num -= 1
        st.session_state.step = f"round_{st.session_state.round_num}"
        st.rerun()

    # Procesar avance de ronda
    if btn_next_action:
        # Guardar amonestaciones de la ronda
        if "penalties_history" not in st.session_state:
            st.session_state.penalties_history = {}
        st.session_state.penalties_history[r_num] = round_penalties

        for tr in table_results:
            pA1, pA2 = tr["pair_a"]
            pB1, pB2 = tr["pair_b"]
            sA, sB = tr["score_a"], tr["score_b"]

            st.session_state.history_pairs.append(frozenset({pA1, pA2}))
            st.session_state.history_pairs.append(frozenset({pB1, pB2}))

            for p in [pA1, pA2]:
                st.session_state.players[p]["jj"] += 1
                st.session_state.players[p]["p_plus"] += sA
                st.session_state.players[p]["p_minus"] += sB
            for p in [pB1, pB2]:
                st.session_state.players[p]["jj"] += 1
                st.session_state.players[p]["p_plus"] += sB
                st.session_state.players[p]["p_minus"] += sA

            # Aplicar descuentos personalizados por amonestación
            for p in st.session_state.player_keys:
                if p in round_penalties:
                    st.session_state.players[p]["p_plus"] -= round_penalties[p]

            for p in st.session_state.player_keys:
                st.session_state.players[p]["diff"] = (
                    st.session_state.players[p]["p_plus"] - st.session_state.players[p]["p_minus"]
                )

            a_won_board = sA > sB
            b_won_board = sB > sA

            if a_won_board:
                st.session_state.players[pA1]["jg"] += 1
                st.session_state.players[pA2]["jg"] += 1
                st.session_state.players[pB1]["jp"] += 1
                st.session_state.players[pB2]["jp"] += 1
            elif b_won_board:
                st.session_state.players[pA1]["jp"] += 1
                st.session_state.players[pA2]["jp"] += 1
                st.session_state.players[pB1]["jg"] += 1
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

    if st.button("⬅️ Volver a la Ronda 6 para consultar o modificar datos"):
        st.session_state.round_num = 6
        st.session_state.step = "round_6"
        st.rerun()
