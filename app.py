import streamlit as st
import pickle
import pandas as pd

st.set_page_config(page_title="IPL Win Predictor", page_icon="🏆", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0e1117; }
[data-testid="stHeader"] { background-color: #0e1117; }
[data-testid="stSidebar"] { background-color: #0e1117; }

/* Subheadings like "Select Teams", "Match Venue" */
h1, h2, h3 { color: #ffffff !important; }

/* Labels above each input box e.g. "Batting Team", "City" */
[data-testid="stWidgetLabel"] p { color: #cccccc !important; }

/* Metric cards - label and value */
[data-testid="stMetricLabel"] p { color: #cccccc !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ── TEAM LOGOS ───────────────────────────────────────────────────────────────
team_logos = {
    'Mumbai Indians':              'https://documents.iplt20.com/ipl/MI/Logos/Logooutline/MIoutline.png',
    'Chennai Super Kings':         'https://documents.iplt20.com/ipl/CSK/logos/Logooutline/CSKoutline.png',
    'Royal Challengers Bangalore': 'https://documents.iplt20.com/ipl/RCB/Logos/Logooutline/RCBoutline.png',
    'Kolkata Knight Riders':       'https://documents.iplt20.com/ipl/KKR/Logos/Logooutline/KKRoutline.png',
    'Sunrisers Hyderabad':         'https://documents.iplt20.com/ipl/SRH/Logos/Logooutline/SRHoutline.png',
    'Delhi Capitals':              'https://documents.iplt20.com/ipl/DC/Logos/LogoOutline/DCoutline.png',
    'Rajasthan Royals':            'https://documents.iplt20.com/ipl/RR/Logos/Logooutline/RRoutline.png',
    'Kings XI Punjab':             'https://documents.iplt20.com/ipl/PBKS/Logos/Logooutline/PBKSoutline.png',
}

# ── DATA ─────────────────────────────────────────────────────────────────────
teams = sorted([
    'Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore',
    'Kolkata Knight Riders', 'Kings XI Punjab', 'Chennai Super Kings',
    'Rajasthan Royals', 'Delhi Capitals'
])

cities = sorted([
    'Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
    'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
    'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
    'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
    'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
    'Sharjah', 'Mohali', 'Bengaluru'
])

# ── LOAD MODEL ───────────────────────────────────────────────────────────────
pipe = pickle.load(open('pipe.pkl', 'rb'))

# ════════════════════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<h1 style='text-align:center;'>🏆 IPL Win Predictor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray; font-size:15px;'>⚡ Real-time match probability engine</p>", unsafe_allow_html=True)
#st.divider()
st.markdown("""
<hr style="
height:1px;
border:none;
background:#00ffcc;
box-shadow:0px 0px 6px #00ffcc;
">
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
#  FORM INPUTS
# ════════════════════════════════════════════════════════════════════════════
st.subheader("Select Teams")
col1, col2 = st.columns(2)
with col1:
    batting_team = st.selectbox("Batting Team", ["-- Select --"] + teams, key="bat")
with col2:
    bowling_team = st.selectbox("Bowling Team", ["-- Select --"] + teams, key="bowl")

st.subheader("Match Venue")
selected_city = st.selectbox("City", ["-- Select --"] + cities, key="city")

st.subheader("Live Match Situation")
c1, c2, c3, c4 = st.columns(4)
with c1:
    target  = st.number_input("Target Score",    min_value=0, max_value=300, value=0, step=1)
with c2:
    score   = st.number_input("Current Score",   min_value=0, max_value=300, value=0, step=1)
with c3:
    overs   = st.number_input("Overs Completed", min_value=0.0, max_value=20.0, value=0.0, step=0.1, format="%.1f")
with c4:
    wickets = st.number_input("Wickets Out",     min_value=0, max_value=10, value=0, step=1)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
#  PREDICT BUTTON
# ════════════════════════════════════════════════════════════════════════════
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    predict_clicked = st.button("⚡ Predict Winning Probability", use_container_width=True, type="primary")

# ════════════════════════════════════════════════════════════════════════════
#  RESULT
# ════════════════════════════════════════════════════════════════════════════
if predict_clicked:

    # Validation
    errors = []
    if batting_team == "-- Select --":
        errors.append("Please select a batting team.")
    if bowling_team == "-- Select --":
        errors.append("Please select a bowling team.")
    if selected_city == "-- Select --":
        errors.append("Please select a match city.")
    if batting_team != "-- Select --" and bowling_team != "-- Select --" and batting_team == bowling_team:
        errors.append("Batting and bowling teams must be different.")
    if target < 1:
        errors.append("Target score must be at least 1.")
    if target > 0 and score >= target:
        errors.append("Current score must be less than the target.")
    if overs <= 0:
        errors.append("Overs completed must be greater than 0.")

    if errors:
        for e in errors:
            st.error(e)

    else:
        # Feature engineering
        runs_left         = target - score
        balls_left        = 120 - int(overs * 6)
        wickets_remaining = 10 - wickets
        crr               = round(score / overs, 2)
        rrr               = round((runs_left * 6) / balls_left, 2) if balls_left > 0 else 0.0

        input_df = pd.DataFrame({
            'batting_team': [batting_team],
            'bowling_team': [bowling_team],
            'city':         [selected_city],
            'runs_left':    [runs_left],
            'balls_left':   [balls_left],
            'wickets':      [wickets_remaining],
            'total_runs_x': [target],
            'crr':          [crr],
            'rrr':          [rrr],
        })

        result = pipe.predict_proba(input_df)
        loss   = round(result[0][0] * 100, 1)
        win    = round(result[0][1] * 100, 1)

        # ── Winner label ──
        if win >= 60:
            st.success(f"🏆  {batting_team} is the FAVOURITE  ({win}% win probability)")
        elif loss >= 60:
            st.error(f"🏆  {bowling_team} is the FAVOURITE  ({loss}% win probability)")
        else:
            st.warning(f"⚖️  It's a CLOSE CONTEST  —  {batting_team} {win}%  vs  {bowling_team} {loss}%")

        st.divider()

        # ── Team columns ──
        left, mid, right = st.columns([2, 1, 2])

        with left:
            logo = team_logos.get(batting_team, '')
            st.image(logo, width=80)
            st.markdown(f"**{batting_team}**")
            st.markdown(f"### 🟢 {win}%")
            st.caption("Win probability")

        with mid:
            st.markdown("## VS")

        with right:
            logo = team_logos.get(bowling_team, '')
            st.image(logo, width=80)
            st.markdown(f"**{bowling_team}**")
            st.markdown(f"### 🔴 {loss}%")
            st.caption("Win probability")

        st.write("")

        # ── Progress bar ──
        st.write(f"**{batting_team}** win chance")
        st.progress(int(win))

        st.divider()

        # ── Stats ──
        st.subheader("Match Stats")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Runs Needed", int(runs_left))
        with m2:
            st.metric("Balls Left", int(balls_left))
        with m3:
            st.metric("Current RR", crr)
        with m4:
            st.metric("Required RR", rrr)
