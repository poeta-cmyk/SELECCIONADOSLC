# --- PANTALLA 2: REGISTRO DE 20 JUGADORES Y OPCIÓN MANUAL ---
elif st.session_state.step == "register":
  st.title("Selección de la Liga de Campeones - Registro y Configuración Inicial")
  st.write("Ingrese los nombres de los 20 participantes:")

  col1, col2 = st.columns(2)
  player_names = {}

  with col1:
    st.subheader("Columna 1 (J1 - J10)")
    for i in range(1, 11):
      player_names[f"J{i}"] = st.text_input(
          f"J{i}", value=f"Jugador {i}", key=f"name_J{i}"
      )

  with col2:
    st.subheader("Columna 2 (J11 - J20)")
    for i in range(11, 21):
      player_names[f"J{i}"] = st.text_input(
          f"J{i}", value=f"Jugador {i}", key=f"name_J{i}"
      )

  st.divider()
  st.subheader("Modo de inicio de la Primera Ronda")

  # Creamos dos botones para dar la opción de elección
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
      # Generar mesas aleatorias de 1
      random.shuffle(names_list)
      st.session_state["tables_r1"] = [
          [names_list[i], names_list[i + 1], names_list[i + 2], names_list[i + 3]]
          for i in range(0, 20, 4)
      ]
      st.session_state.round_num = 1
      st.session_state.step = "round_1"
      st.rerun()

  with b_col2:
    # Opción de activar el generador manual
    if st.button("🛠️ Generar ronda manualmente"):
      st.session_state.modo_manual = True
      st.rerun()

  # Si el usuario eligió configurar manualmente las mesas de la primera ronda
  if st.session_state.get("modo_manual", False):
    st.info(
        "Asigne los jugadores manualmente para cada una de las 5 mesas de la"
        " primera ronda:"
    )
    all_names = list(player_names.values())
    manual_tables = []

    for m in range(5):
      st.markdown(f"**Mesa {m + 1}**")
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
      # Validar que no se repitan jugadores en la selección manual
      flat_manual = [p for mesa in manual_tables for p in mesa]
      if len(set(flat_manual)) < 20:
        st.error(
            "Error: Hay jugadores repetidos en las mesas. Cada uno debe ser"
            " único."
        )
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
