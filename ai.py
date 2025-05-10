from openai import AzureOpenAI
import streamlit as st
import sqlite3
import pandas as pd


def get_teams_and_players():
    # function to pull all teams together for the ai bot to have data
    with sqlite3.connect("mlb.db") as conn:
        query = """
            SELECT
                teams.name AS team_name,
                players.name AS player_name
            FROM teams
            LEFT JOIN players ON teams.id = players.team_id
            ORDER BY teams.name, players.name
        """
        df = pd.read_sql_query(query, conn)

    # Convert DataFrame to a readable string
    teams_and_players = ""
    for _, row in df.iterrows():
        teams_and_players += (
            f"Team: {row['team_name']}, Player: {row['player_name']}\n"
        )

    return teams_and_players


def ai_bot(client=None):  # parameter is for testibility
    if client is None:
        client = AzureOpenAI(
            api_key=st.secrets["OPENAI_API_KEY"],
            api_version="2024-10-21",
            azure_endpoint=st.secrets["END_POINT"]
        )

    st.session_state.setdefault("openai_model", "gpt-35-turbo-16k")
    st.session_state.setdefault("messages", [])

    # Display chat history
    for msg in st.session_state.messages:
        role = "👨 Fan" if msg["role"] == "user" else "🧑‍⚖️ Ump"
        with st.chat_message(msg["role"]):
            st.markdown(f"**{role}:** {msg['content']}")

    # Initial greeting
    if not st.session_state.messages:
        greeting = (
            "🧑‍⚖️ *HI! I am a MLB Chat Bot Umpire. "
            "Do you have any baseball questions?*"
        )
        st.session_state.messages.append({"role": "assistant", "content":
                                          greeting})
        with st.chat_message("assistant"):
            st.markdown(f"**🧑‍⚖️ Ump:** {greeting}")

    # Handle user input
    if prompt := st.chat_input("Step up to the plate..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"**👨 Fan:** {prompt}")

        system_message = {
            "role": "system",
            "content": (
                "You are an AI Bot posed as an Umpire to answer a fan's "
                "questions on the MLB and sport of baseball. It's 2025. "
                "Here is the current list of teams and players:\n"
                f"{get_teams_and_players()} USE THIS DATA"
            )
        }

        messages = [system_message] + st.session_state.messages

        response = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages
        )

        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content":
                                          reply})
        with st.chat_message("assistant"):
            st.markdown(f"🧑‍⚖️ Ump: {reply}")
