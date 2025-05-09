# ⚾ Inside the Park – [Click here to open the app!](https://insidethepark.streamlit.app/)

## Overview  
**Inside the Park** is a fun and interactive Streamlit web app for exploring everything Major League Baseball. You can view detailed info about every team and player, visualize league-wide stats, and play trivia games. It also includes a built-in AI umpire powered by OpenAI to answer your baseball questions.

---

## Features  
- 🎯 A trivia game where you answer questions about your selected MLB team  
- 📇 Team explorer with stadium details, addresses, and website links  
- 🧢 Full player rosters with headshots, bios, past teams, and more  
- 🗺️ Interactive map showing all MLB stadiums  
- 🔢 Jersey number insights and search across the league  
- 🤖 Built-in AI "umpire" that answers your baseball questions, rules, and facts  
- ✅ Unit tested and tracked with coverage  

---

## Deployed App  
You can deploy your app to **Streamlit Cloud**:

1. Push the repo to GitHub  
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)  
3. Click “Create App”  
4. Choose `RenaWachsman/InsidethePark`  
5. Set the main file to `Main.py`  
6. Under "Advanced Settings", add your OpenAI API key under **Secrets**  
7. Click **Deploy**

---

## ChatGPT Integration  
This project uses AzureOpenAI's GPT API to:

- Answer fan questions in a chat-style interface  
- Provide fun, informative context about players, teams, and game rules  

**How It Works:**  
In the app, prompts are passed through the `openai` library and displayed inside the Streamlit interface.

---

## Dependencies & Installation  

### Required Python Packages  
This project requires:

- `streamlit` – Web app framework  
- `streamlit-option-menu` – Sidebar menus  
- `openai` – AI chat assistant  
- `beautifulsoup4` – Web scraping  
- `requests` – HTTP requests  
- `pandas` – Data manipulation  
- `geopy` – Geolocation and mapping  
- `pytest`, `coverage` – Testing  
- `ipykernel` – Jupyter/Streamlit support  

### Install Dependencies  
```bash
pip install -r requirements.txt
