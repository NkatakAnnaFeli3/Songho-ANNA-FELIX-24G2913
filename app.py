import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Songo Pro - Anna", layout="centered")

# --- 1. LOGIQUE ET ÉTAT DU JEU PYTHON ---
if "board" not in st.session_state:
    st.session_state.board = [7] * 14
    st.session_state.scores = [0, 0]
    st.session_state.tour = 0  # 0 = Joueur 1 (bas), 1 = Joueur 2 (haut)
    st.session_state.message = "Le Joueur 1 commence !"

# Réception sécurisée du coup via les paramètres d'URL (très stable)
query_params = st.query_params
if "pit" in query_params:
    pit = int(query_params["pit"])
    board = st.session_state.board
    tour = st.session_state.tour
    
    # Règles de validation du Songo
    if (tour == 0 and pit > 6) or (tour == 1 and pit < 7):
        st.session_state.message = "❌ Ce n'est pas votre camp !"
    elif board[pit] == 0:
        st.session_state.message = "❌ Cette case est vide !"
    else:
        seeds = board[pit]
        board[pit] = 0
        current = pit
        while seeds > 0:
            current = (current + 1) % 14
            if current == pit:
                current = (current + 1) % 14
            board[current] += 1
            seeds -= 1
            
        captured = 0
        while True:
            in_adversary_camp = (tour == 0 and 7 <= current <= 13) or (tour == 1 and 0 <= current <= 6)
            if in_adversary_camp and (board[current] in [2, 3, 4]):
                captured += board[current]
                board[current] = 0
                current = (current - 1 + 14) % 14
            else:
                break
                
        st.session_state.scores[tour] += captured
        st.session_state.tour = 1 - tour
        st.session_state.message = f"Au tour du Joueur {st.session_state.tour + 1}"
        
    st.query_params.clear()
    st.rerun()

if "action" in query_params and query_params["action"] == "reset":
    st.session_state.board = [7] * 14
    st.session_state.scores = [0, 0]
    st.session_state.tour = 0
    st.session_state.message = "Partie réinitialisée. Joueur 1 commence !"
    st.query_params.clear()
    st.rerun()

# --- 2. PRÉPARATION DE L'INTERFACE GRAPHIQUE ---
board_json = st.session_state.board
s0, s1 = st.session_state.scores[0], st.session_state.scores[1]
active_0 = "active" if st.session_state.tour == 0 else ""
active_1 = "active" if st.session_state.tour == 1 else ""

# Génération des trous du Haut (13 à 7) avec leurs clics directs intégrés
p2_html = ""
for i in range(13, 6, -1):
    disabled = "disabled" if st.session_state.tour == 0 else ""
    p2_html += f'<div class="pit {disabled}" onclick="sendMove({i})"><span class="seeds">{board_json[i]}</span></div>'

# Génération des trous du Bas (0 à 6) avec leurs clics directs intégrés
p1_html = ""
for i in range(0, 7):
    disabled = "disabled" if st.session_state.tour == 1 else ""
    p1_html += f'<div class="pit {disabled}" onclick="sendMove({i})"><span class="seeds">{board_json[i]}</span></div>'

# --- 3. LE CODE HTML/CSS 100% VERT UNIQUE AVEC TOUCHES INTÉGRÉES ---
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Fond d'écran 100% Vert Dégradé Lumineux */
        body {{ 
            background: linear-gradient(135deg, #064e3b 0%, #022c22 50%, #065f46 100%); 
            font-family: 'Segoe UI', Arial, sans-serif; 
            color: #fff; margin: 0; padding: 10px; display: flex; justify-content: center;
            min-height: 100vh;
        }}
        .game-container {{ text-align: center; background: rgba(0, 0, 0, 0.5); padding: 20px; border-radius: 20px; width: 100%; max-width: 620px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); border: 1px solid rgba(255,255,255,0.1); }}
        .header-area {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }}
        h1 {{ color: #f1f5f9; margin: 0; font-size: 1.8rem; letter-spacing: 1px; }}
        
        /* Chronomètre vert clair style radar */
        .timer {{ background: #022c22; padding: 6px 12px; border-radius: 20px; color: #34d399; font-weight: bold; font-family: monospace; font-size: 1.1rem; border: 1px solid #059669; }}
        
        .scoreboard {{ display: flex; justify-content: space-between; margin-bottom: 15px; }}
        .score {{ background: #022c22; padding: 10px 18px; border-radius: 8px; border: 2px solid transparent; font-size: 0.95rem; }}
        .score.active {{ border-color: #34d399; box-shadow: 0 0 15px rgba(52, 211, 153, 0.4); }}
        .score span {{ font-weight: bold; color: #fbbf24; font-size: 1.2rem; }}
        .status {{ font-size: 1.1rem; color: #e2e8f0; margin-bottom: 15px; font-weight: bold; min-height: 27px; }}
        
        /* Plateau en bois traditionnel */
        .board {{ background: #5c3a21; border: 10px solid #362213; border-radius: 25px; padding: 20px; display: flex; flex-direction: column; gap: 20px; box-shadow: inset 0 0 25px rgba(0,0,0,0.9); }}
        .row {{ display: flex; justify-content: center; gap: 12px; }}
        
        /* Trous réactifs directement au clic */
        .pit {{ width: 62px; height: 62px; background: #231408; border-radius: 50%; display: flex; justify-content: center; align-items: center; cursor: pointer; box-shadow: inset 0 6px 10px rgba(0,0,0,0.9); transition: all 0.2s; }}
        .pit:hover:not(.disabled) {{ background: #3a220f; transform: scale(1.08); box-shadow: inset 0 4px 8px rgba(0,0,0,0.8), 0 0 12px #34d399; }}
        .pit.disabled {{ cursor: not-allowed; opacity: 0.35; pointer-events: none; }}
        .seeds {{ color: #fbbf24; font-size: 1.4rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.9); }}
        
        .footer-credit {{ margin-top: 20px; font-size: 0.85rem; color: #cbd5e1; font-style: italic; }}
        .footer-credit span {{ color: #34d399; font-weight: bold; font-style: normal; }}
    </style>
</head>
<body>
    <div class="game-container">
        <div class="header-area">
            <h1>🎴 Songo Master</h1>
            <div class="timer">⏱️ <span id="time-display">00:00</span></div>
        </div>
        <div class="scoreboard">
            <div class="score {active_1}">Joueur 2 (Haut) : <span>{s1}</span></div>
            <div class="score {active_0}">Joueur 1 (Bas) : <span>{s0}</span></div>
        </div>
        <div class="status">{st.session_state.message}</div>
        <div class="board">
            <div class="row">{p2_html}</div>
            <div class="row">{p1_html}</div>
        </div>
        <div class="footer-credit">Développé avec passion par <span>Anna</span></div>
    </div>

    <script>
        // Script du chrono
        if (!window.parent.songoStartTime) window.parent.songoStartTime = Date.now();
        setInterval(() => {{
            const elapsed = Math.floor((Date.now() - window.parent.songoStartTime) / 1000);
            document.getElementById('time-display').innerText = String(Math.floor(elapsed / 60)).padStart(2,'0') + ':' + String(elapsed % 60).padStart(2,'0');
        }}, 1000);

        # Envoi direct du coup à l'application sans passer par des boutons externes
        function sendMove(pitIndex) {{
            const url = new URL(window.parent.location.href);
            url.searchParams.set('pit', pitIndex);
            window.parent.location.href = url.href;
        }}
    </script>
</body>
</html>
"""

# Injection propre du jeu en bois vert dans la page Streamlit
components.html(html_template, height=480, scrolling=False)

# Bouton Réinitialiser natif en bas, centré proprement
st.markdown("<br>", unsafe_allow_html=True)
col_reset = st.columns([1,2,1])
with col_reset[1]:
    if st.button("🔄 Réinitialiser la partie", use_container_width=True):
        st.query_params.from_dict({"action": "reset"})
        st.markdown("<script>window.parent.songoStartTime = Date.now();</script>", unsafe_allow_html=True)
        st.rerun()