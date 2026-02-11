import streamlit as st
from movie_agent import MovieAgent
import requests

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="🎬 Cinematic Movie Agent",
    page_icon="🎬",
    layout="wide"
)

# ==================================================
# CINEMATIC CSS (FIXED + COMPACT)
# ==================================================
st.markdown("""
<style>

/* ---------- APP BACKGROUND ---------- */
.stApp {
    background:#020617;
}

/* ⭐ Cinematic stage overlay (removes empty feeling) */
section.main {
    background: radial-gradient(
        circle at center,
        rgba(15,23,42,0.6) 0%,
        rgba(2,6,23,1) 60%
    );
}
/* ---------- MAIN CONTENT WIDTH ---------- */
section.main > div {
    max-width:1100px;
    margin:auto;
}

/* ---------- ⭐ REAL CHAT HEIGHT FIX ---------- */
/* Prevent Streamlit chat container from filling full screen */
div[data-testid="stAppViewContainer"] > section.main {
    height:auto !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    height:auto !important;
}

/* ---------- SPACING ---------- */
.block-container {
    padding-top:2rem;
}

/* ---------- TITLE ---------- */
.big-title {
    font-size:40px;
    font-weight:700;
    color:white;
}

/* ---------- MOVIE CARD ---------- */
.movie-card {
    background:linear-gradient(135deg,#020617,#0f172a);
    border-radius:16px;
    padding:20px;
    margin-top:14px;
    display:flex;
    gap:18px;
    align-items:center;
    box-shadow:0px 10px 30px rgba(0,0,0,0.5);
    color:white;
}

.poster {
    border-radius:12px;
}
/* ⭐ Anchor chat content to TOP instead of center */
[data-testid="stVerticalBlockBorderWrapper"] {
    display:flex !important;
    flex-direction:column !important;
    justify-content:flex-start !important;
}

/* ⭐ Remove extra stretch from chat message container */
[data-testid="stChatMessageContainer"] {
    align-items:flex-start !important;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# LOAD AGENT
# ==================================================
@st.cache_resource
def load_agent():
    return MovieAgent("data/movies.json")

agent = load_agent()

# ==================================================
# POSTER FETCH FUNCTION (FIXED VERSION)
# ==================================================
def get_poster(title):
    try:
        url = "https://ghibliapi.vercel.app/films"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()

        for film in data:
            if film["title"].lower() == title.lower():
                return film.get("image")

    except Exception:
        return None

    return None

# ==================================================
# HEADER
# ==================================================
st.markdown('<div class="big-title">🎬 Cinematic Movie Agent</div>', unsafe_allow_html=True)
st.caption("Agentic AI • External Tools • Persistent Memory")

st.divider()

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.title("⚙️ Agent Controls")

mode = st.sidebar.radio(
    "Agent Mode",
    ["Chat Mode", "Recommend Mode"]
)

min_rating = st.sidebar.slider(
    "Minimum Rating",
    0.0, 10.0, 8.0
)

# ==================================================
# SESSION CHAT MEMORY
# ==================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==================================================
# CHAT MODE
# ==================================================
if mode == "Chat Mode":

    # ---------- EMPTY STATE (PREVENT BLACK VOID) ----------
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div style="
            background:linear-gradient(135deg,#020617,#0f172a);
            padding:30px;
            border-radius:18px;
            text-align:center;
            color:white;
            margin-top:20px;
            box-shadow:0px 10px 30px rgba(0,0,0,0.5);
        ">
            <h2>🎬 Welcome to Cinematic Movie Agent</h2>
            <p>Ask for any Studio Ghibli movie like:</p>
            <p><b>Spirited Away</b> • <b>Totoro</b> • <b>Howl's Moving Castle</b></p>
        </div>
        """, unsafe_allow_html=True)

    # ---------- SHOW CHAT HISTORY ----------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask the Movie Agent...")

    if user_input:

        # show user message
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        # agent response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Agent thinking..."):
                movie = agent.fetch_movie_details(user_input)

            if movie:

                poster = get_poster(movie["title"])

                card = '<div class="movie-card">'

                if poster:
                    card += f'<img src="{poster}" width="120" class="poster"/>'

                card += f"""
                <div>
                <h3>🎬 {movie['title']}</h3>
                ⭐ {movie['rating']} <br>
                🎭 {movie['genre']} <br>
                📅 {movie['year']}
                </div>
                </div>
                """

                st.markdown(card, unsafe_allow_html=True)

                st.session_state.messages.append(
                    {"role": "assistant", "content": f"Fetched {movie['title']}"}
                )

            else:
                st.error("Movie not found")

# ==================================================
# RECOMMEND MODE
# ==================================================
elif mode == "Recommend Mode":

    if st.button("🎯 Generate Recommendations"):

        movies = agent.recommend_movies(min_rating)

        if movies:
            st.success(f"Agent found {len(movies)} recommendations")

            for m in movies:

                poster = get_poster(m["title"])

                card = '<div class="movie-card">'

                if poster:
                    card += f'<img src="{poster}" width="120" class="poster"/>'

                card += f"""
                <div>
                <h3>🎬 {m['title']}</h3>
                ⭐ {m['rating']} <br>
                🎭 {m['genre']} <br>
                📅 {m['year']}
                </div>
                </div>
                """

                st.markdown(card, unsafe_allow_html=True)

        else:
            st.warning("No recommendations yet. Fetch movies first.")
