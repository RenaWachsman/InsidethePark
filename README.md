# ⚾ Inside the Park - [Click Here!](https://insidethepark.streamlit.app)

**Inside the Park** is a fun and interactive Streamlit web app for exploring everything Major League Baseball. You can view detailed info about every team and player, visualize league-wide stats, and play trivia games. It also includes a built-in AI umpire powered by OpenAI to answer your baseball questions.

![Tests](https://github.com/RenaWachsman/InsidethePark/actions/workflows/tests.yml/badge.svg)   ![coverage](coverage.svg)

---
## 📦 Features

- Scrapes MLB ballpark data from a public website
- Retrieves player details and summaries from APIs
- Stores data in a local SQLite3 database
- Provides interactive visualizations and data manipulation
- Integrates OpenAI ChatGPT for intelligent responses
- Fully deployable on Streamlit Cloud

- 🎯 A trivia game where you answer questions about your selected MLB team
- 🏟️ Team explorer with stadium details, addresses, and website links
- 🧢 Full player rosters with headshots, honors, past teams, and more
- 🗺️ Interactive map showing all MLB stadiums
- 🔢 Jersey number insights and search across the league
- 🤖 Built-in AI "umpire" that answers your baseball questions, rules, and facts
- ✅ Unit tested and tracked with coverage

---

## 🛠️ Installation & Local Setup

To run the app locally:

### 1. Clone the repository

```bash
git clone https://github.com/RenaWachsman/InsidethePark.git
cd inside-the-park
```

### 2. Create a virtual environment and activate it

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `secrets.toml` in `.streamlit/`:

```
# .streamlit/secrets.toml
OPENAI_API_KEY=your-openai-api-key
END_POINT=your-maps-api-key
```

### 5. Run the app

```bash
streamlit run app.py
```

---

## 🤖 ChatGPT Integration

The app uses the OpenAI API to provide natural language summaries and insights about Major League Baseball, it's players, rules and history,

---

## ✅ Testing

This project includes tests for:

- Web scraping and API functions (mocked)
- Database interactions (CRUD)
- Core logic
- Streamlit interface behavior

To run tests and check coverage:

```bash
python -m pytest --cov
```
