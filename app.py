# region Imports
import streamlit as st
import pandas as pd
import sqlite3
from streamlit_option_menu import option_menu

from api import get_player_info, get_player_honors, get_player_teams
from database import get_all_teams, get_team_by_id, get_players_by_team_id
from trivia_game import TriviaGame, new_game
from ai import ai_bot
from data_displays import stadium_map, jersey_distribution, players_by_jersey
# endregion

# region Setup
# Connect to SQLite database
conn = sqlite3.connect('mlb.db')

# Configure Streamlit page settings
st.set_page_config(page_title="Inside the Park", page_icon="⚾",
                   layout="wide")

# Display main title
st.markdown("""
    <h1 style="text-align: left; color: #0033cc;">
        ⚾ Inside the Park ⚾
    </h1>
""", unsafe_allow_html=True)

# Apply custom CSS styling
st.markdown("""
    <style>
        .block-container {
            max-width: 1100px;
            margin: 0 auto;
        }
    </style>
""", unsafe_allow_html=True)
# endregion

# region Sidebar Navigation
with st.sidebar:
    selected_sidebar = option_menu(
        "Main Menu",
        ["Choose a Team", "Team Info", "Get to Know the Players",
            "Team Trivia", "MLB Data", "Ask the Ump"],
        icons=['play', 'trophy', 'person',
               'question-circle', 'clipboard', 'chat'],
        menu_icon="cast",
        default_index=0,
        styles={
            "icon": {
                "color": "#0033cc", "font-size": "30px"
            },
            "nav-link": {
                "font-size": "16px", "text-align": "left",
                "margin": "0px", "--hover-color": "#f0f0f0"
            },
            "nav-link-selected": {
                "background-color": "#ff0000", "color": "white"
            },
            "container": {
                "padding": "0!important", "background-color": "#ffffff"
            },
        }
    )

# Sync menu selection with session state
if 'menu_option' not in st.session_state:
    st.session_state['menu_option'] = selected_sidebar
else:
    st.session_state['menu_option'] = selected_sidebar
# endregion

# region API Calls
def fetch_player_info(player_name):
    """Fetch basic player info."""
    return get_player_info(player_name)


def fetch_player_honors(player_id):
    """Fetch player honors."""
    return get_player_honors(player_id)


def fetch_player_teams(player_id):
    """Fetch player's former teams."""
    return get_player_teams(player_id)


# endregion

# region Team Selection


def get_selected_team():
    """Returns the selected team from session state or \
        prompt the user to choose."""
    if 'selected_team' not in st.session_state:
        choosing_team()
    return st.session_state.get('selected_team')


def choosing_team():
    """Prompt user to select a team and update session state."""
    teams_df = get_all_teams()
    team_name_to_id = {row['name']: row['id']
                       for _, row in teams_df.iterrows()}
    team_names = ["-- Please select a team.--"] + \
        list(team_name_to_id.keys())

    selected_team_name = st.selectbox(
        "Select a team", team_names, key="selected_team_name")

    if selected_team_name != "-- Please select a team.--":
        st.session_state['selected_team'] = team_name_to_id[selected_team_name]
        st.rerun()
# endregion

# region Choose a Team Page
if st.session_state['menu_option'] == "Choose a Team":
    new_game()  # reset in case a games in progress
    st.subheader("MLB Teams")
    st.write("Select your Favorite Team to Interact with!")

    df_teams = pd.read_sql_query("SELECT * FROM teams", conn)

    cols_per_row = 2
    cols = st.columns(cols_per_row)

    for idx, row in df_teams.iterrows():
        col = cols[idx % cols_per_row]
        with col:
            with st.container():
                inner_cols = st.columns([0.4, 2.6])
                with inner_cols[0]:
                    st.image(row['logo_url'], width=45)
                with inner_cols[1]:
                    if st.button(
                        row['name'], key=row['name'],
                        help=f"Select {row['name']}"
                    ):
                        st.session_state['selected_team'] = row['id']
# endregion

# region Team Info Page
elif st.session_state['menu_option'] == "Team Info":
    st.subheader("Get to Know the Team")
    st.write("Learn more about the Team!")
    selected_team = get_selected_team()
    if selected_team is None:
        st.stop()
    else:
        team = get_team_by_id(int(selected_team))
        st.markdown(f"#### {team['name']} Info:")
        st.markdown(f"**🏟️ Stadium:** {team['stadium']}")
        st.markdown(f"**📍 Stadium Address:** {team['stadium_addr']}")
        st.markdown(f"**📞 Phone:** {team['phone']}")
        st.markdown(
            f"**🔗 Team Page:** [Link](https://www.mlb.com/{team['team_ext']})")
# endregion

# region Player Info Page
elif st.session_state['menu_option'] == "Get to Know the Players":
    st.subheader("Get to Know the Players")
    st.write("Learn more about the players and their stats!")
    if 'player_details_shown' not in st.session_state:
        st.session_state.player_details_shown = {}

    selected_team = get_selected_team()
    if selected_team is None:
        st.stop()
    else:
        team = get_team_by_id(int(selected_team))

    st.subheader(f"{team['name']} Roster")
    players_df = get_players_by_team_id(int(get_selected_team()))

    for _, row in players_df.iterrows():
        with st.expander(
            f"**# {row['jersey_number']} - {row['name']}**",
            expanded=False
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(row['headshot_url'], width=100)
            with col2:
                st.markdown(f"**Name**: {row['name']}")
                st.markdown(f"**Jersey Number**: {row['jersey_number']}")
            with col3:
                if st.button(f"Find Out More about {row['name']}",
                             key=f"find_out_more_{row['jersey_number']}"):
                    st.session_state.player_details_shown[row
                                                          ['jersey_number']
                                                          ] = True

            if st.session_state.player_details_shown.get(row['jersey_number'],
                                                         False):
                st.markdown(
                    f"#### **Additional Information about {row['name']}**")
                player_info = fetch_player_info(row['name'])
                if player_info:
                    external_player_id = player_info.get('idPlayer', 0)
                    st.write(
                        f"**🎂 Birthday:** "
                        f"{player_info.get('dateBorn', 'Not available')}"
                    )

                    st.write(
                        f"**🌍 Nationality:** "
                        f"{player_info.get('strNationality', 'Not available')}"
                    )

                    st.write(
                        f"**📍 Position:** "
                        f"{player_info.get('strPosition', 'Not available')}"
                    )

                    try:
                        player_honors = fetch_player_honors(external_player_id)
                    except Exception as e:
                        player_honors = None
                        st.error(f"Error retrieving honors: {e}")

                    if player_honors:
                        st.write("**Honors:**")
                        for honor in player_honors:
                            st.markdown(
                                f"- 🏆 **{honor['honour']}** with ** \
                                {honor['team_name']} \
                                ** in **{honor['year']}**"
                            )
                    else:
                        st.write("No honors found.")

                    try:
                        former_teams = fetch_player_teams(external_player_id)
                    except Exception as e:
                        former_teams = None
                        st.error(f"Error retrieving former teams: {e}")

                    if former_teams:
                        st.write("**Former Teams:**")
                        for team in former_teams:
                            st.markdown(
                                f"- 🏟️ **{team['former_team']}** \
                                ({team.get('joined', 'N/A')} to \
                                {team.get('departed', 'N/A')}) \
                            >>Type: *{team['move_type']}*")
                    else:
                        st.write("No former teams found.")
                else:
                    st.warning("No additional information found.")
# endregion

# region Team Trivia Page
elif st.session_state['menu_option'] == "Team Trivia":
    st.subheader("The Grand Slam Quiz")
    st.write("Test your baseball knowledge with team-based trivia.")

    if 'selected_team' not in st.session_state:
        choosing_team()
    else:
        with st.expander("📖 The Playbook"):
            st.markdown("""
                1. **Team Selection**: Pick your favorite baseball team.
                2. **Answer Questions**: You'll be asked 5 trivia questions
                        based on your selected team and its players.
                3. **Scoring**:
                    - Correct answer = **Base**
                    - Wrong answer = **Strike**
                4. **Game Rules**:
                    - **3 strikes** and you're out.
                    - You get **5 pitches** (questions) max.
                    - Game ends after 5 questions or 3 strikes.
                5. **Performance Grades**:
                    - **1 Correct**: "Single!"
                    - **2 Correct**: "Double!"
                    - **3 Correct**: "Triple!"
                    - **4 Correct**: "Home Run!"
                    - **5 Correct**: "Grand Slam!"
                """)
        team_id = int(st.session_state["selected_team"])
        game = TriviaGame(team_id)  # start a trivia game
        trivia_q = game.get_question()

        col1, col2 = st.columns([1, 1])
        with col1:
            team = get_team_by_id(team_id)
            st.markdown(f"## Play Ball!\n##### Your team: {team['name']}")

            if trivia_q:
                if trivia_q.image_url:
                    st.image(trivia_q.image_url, width=150)

                user_answer = st.radio(trivia_q.question, trivia_q.choices,
                                       key=f"answer_{team_id}")

                if not st.session_state[game.submit_key]:
                    if st.button("Submit"):
                        st.session_state[game.submit_key] = True
                        game.submit_answer(user_answer)  # check user's answer

                if st.session_state[game.submit_key]:
                    if not game.is_game_over():  # check if game is over
                        if st.button("Next Pitch"):  # if not new question
                            game.next_pitch()
                    else:
                        game.finalize_status()
                        st.markdown(f"#### GAME OVER! \
                                    {st.session_state['status']}")
                        if st.button("🔁 Start New Game"):
                            new_game()  # clear for a new game
                            st.rerun()  # start a new game
        with col2:
            st.markdown("## Scoreboard ")
            st.markdown("####")
            st.markdown(f"""
                <div style='background-color: #f5f5f5; padding: 1rem;
                    border-radius: 10px; box-shadow: 2px 2px
                        5px rgba(0,0,0,0.1);'>
                    <p style='font-size: 18px;'>⚾ <strong>Pitches:</strong>
                        {st.session_state.pitches}</p>
                    <p style='font-size: 18px;'>🧮 <strong>Pitches Remaining: \
                        </strong>
                        {5 - st.session_state.pitches}</p>
                    <p style='font-size: 18px;'>❌ <strong>Strikes:</strong>
                        {st.session_state.strikes}</p>
                    <p style='font-size: 18px;'>✅ <strong>Correct:</strong>
                        {st.session_state.bases}</p>
                    <p style='font-size: 18px;'>🏅 <strong>Status:</strong>
                        {st.session_state.status}</
                </div>
                """, unsafe_allow_html=True)
# endregion

# region MLB Data Page
elif st.session_state['menu_option'] == "MLB Data":
    st.subheader("Explore MLB Data")

    option = st.radio("Choose a view:", [
                      "📍 MLB Stadium Map", "👕 Jersey Number Distribution",
                      "🔢 Browse Players by Jersey Number"
                      ])

    if option == "📍 MLB Stadium Map":
        stadium_map(conn)
    elif option == "👕 Jersey Number Distribution":
        jersey_distribution(conn)
    elif option == "🔢 Browse Players by Jersey Number":
        players_by_jersey(conn)
# endregion

# region Ask the Ump Page
elif st.session_state['menu_option'] == "Ask the Ump":
    st.subheader("Ask the Ump")
    ai_bot()
# endregion
