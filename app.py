
import streamlit as st
import pandas as pd
import numpy as np

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

#  STEP 1 & 2: DATAPREPROCESSING (WITH Caching)
@st.cache_data
def load_and_prepare_data():
    st.info("Laddar och förbereder FPL-rådata (säsong 23/24)... (detta görs bara en gång)")
    
    try:
        url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2023-24/gws/merged_gw.csv"
        df_raw = pd.read_csv(url)
    except Exception as e:
        st.error(f"Kunde inte ladda data från GitHub: {e}")
        return None

    # Cleaning
    df_raw['price'] = df_raw['value'] / 10.0
    cols_to_fill = ['total_points', 'minutes', 'goals_scored', 'assists', 'bonus', 'clean_sheets']
    for col in cols_to_fill:
        if col in df_raw.columns:
            df_raw[col] = df_raw[col].fillna(0)

    # Aggregation
    aggregation_functions = {
        'total_points': 'sum', 'minutes': 'sum', 'goals_scored': 'sum',
        'assists': 'sum', 'bonus': 'sum', 'clean_sheets': 'sum', 'price': 'last'
    }
    cols_to_agg = {k: v for k, v in aggregation_functions.items() if k in df_raw.columns}
    df_agg = df_raw.groupby(['name', 'position', 'team']).agg(cols_to_agg).reset_index()

    df_agg.rename(columns={
        'total_points': 'total_points_season', 'minutes': 'total_minutes_season',
        'goals_scored': 'total_goals_season', 'assists': 'total_assists_season',
        'price': 'current_price'
    }, inplace=True)
    
    # Step 2: Format the data as as text
    df_filtered = df_agg[df_agg['total_minutes_season'] > 500].copy()
    df_sorted = df_filtered.sort_values(by='total_points_season', ascending=False)
    
    output_text = "FPL Player Data (Price in £M, Points for season 2023-24):\n\n"
    for index, row in df_sorted.iterrows():
        player_string = (
            f"Player: {row['name']} "
            f"({row['position']}, {row['team']}), "
            f"Price: {row['current_price']:.1f}, "
            f"Points: {row['total_points_season']}\n"
        )
        output_text += player_string
    
    st.success("Datainläsning klar!")
    return output_text

# STEG 3: AI-LOGIK 

def get_ai_chain(api_key, player_data_text):
    
    # 1. Systemprompten sätter reglerna och ger datan
    system_prompt = f"""
    Du är en expert på Fantasy Premier League (FPL).
    Ditt mål är att hjälpa användaren bygga ett lag.
    Du måste basera alla dina val och beräkningar på följande spelardata (från säsongen 2023-24).

    PLAYERRDATA:
    ---
    {player_data_text}
    ---

    Regler för konversation:
    - Svara alltid på samma språk som användarens senaste meddelande.
    - Var artig och hjälpsam.
    - Du måste komma ihåg tidigare meddelanden i konversationen.
    - Användaren kommer att ge dig sina "Aktuella Inställningar" (Budget och Formation)
      i varje meddelande. Du måste följa dessa inställningar.
    """
    
    # 2. Load the model
    llm = ChatOpenAI(
        openai_api_key=api_key,
        model_name="gpt-4o-mini",
        temperature=0.7
    )
    
    # 3. Skapa den nya prompt-mallen create the new prompt template
    # It now gathers 4 variables: budget, formation, chat_history, input
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{chat_history}"), 
        ("user", """
        Mina aktuella inställningar:
        - Budget: {budget} miljoner
        - Formation: {formation}
        
        Min fråga: {input}
        """)
    ])
    
    # 4. Create an easy chain
    chain = prompt | llm | StrOutputParser()
    
    return chain

# --- STEG 4: STREAMLIT INTERFACE	

st.set_page_config(layout="wide")
st.title("FPL Budget Team Builder")
st.markdown("Använd sidomenyn för att ställa in din budget och formation. Ställ sedan frågor i chatten!")

# LOAD THE DATA	
player_data = load_and_prepare_data()

# Sidebar) 
st.sidebar.header("Konfiguration")
user_api_key = st.sidebar.text_input(
    "Ange din OpenAI API-nyckel (sk-...)",
    type="password",
    help="Din nyckel sparas inte, den används bara för denna session."
)

st.sidebar.divider()
st.sidebar.header("Dina Laginställningar")

# 1. Budget-slider 
user_budget = st.sidebar.slider(
    "Välj din budget (i miljoner):",
    min_value=80.0,
    max_value=120.0,
    value=100.0, # Standardvärde
    step=0.5
)

# 2. Choose formation of the team
col1, col2 = st.sidebar.columns(2)
gk_count = col1.number_input("Målvakter (GK):", min_value=1, max_value=1, value=1)
def_count = col2.number_input("Försvarare (DEF):", min_value=3, max_value=5, value=4)
mid_count = col1.number_input("Mittfältare (MID):", min_value=2, max_value=5, value=4)
fwd_count = col2.number_input("Anfallare (FWD):", min_value=1, max_value=3, value=2)

user_formation = f"{gk_count} GK, {def_count} DEF, {mid_count} MID, {fwd_count} FWD"
total_players = gk_count + def_count + mid_count + fwd_count

if total_players != 11:
    st.sidebar.error(f"Ditt lag måste ha 11 spelare, du har {total_players}.")
else:
    st.sidebar.success(f"Du har valt {total_players} spelare.")


# CHATT-LOGIK 
if player_data:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "ai_chain" not in st.session_state:
        st.session_state.ai_chain = None

    # Visa alla gamla meddelanden
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Waiting for new input from user
    if prompt := st.chat_input("Din fråga... (t.ex. 'Ge mig 3 lagförslag')"):
        
        #  Control if API-key exists
        if not user_api_key:
            st.error("Du måste ange din OpenAI API-nyckel i sidomenyn först.")
        #  Control if formation is 11 players
        elif total_players != 11:
             st.error("Justera din formation i sidomenyn. Du måste ha exakt 11 spelare.")
        else:
            # Initiate the chain if not already exists 
            if st.session_state.ai_chain is None:
                st.session_state.ai_chain = get_ai_chain(user_api_key, player_data)
            
            # a. Add users message in history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # b.  Formate the history for the AI
            formatted_history = []
            for msg in st.session_state.messages[:-1]:
                if msg["role"] == "user":
                    formatted_history.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    formatted_history.append(AIMessage(content=msg["content"]))
            
            # c.  Generate AI answear
            with st.chat_message("assistant"):
                with st.spinner("AI:n tänker..."):
                    # Använd kedjan, och skicka med ALLA variabler
                    response = st.session_state.ai_chain.invoke({
                        "budget": user_budget,           # Från slidern
                        "formation": user_formation,     # Från nummer-input
                        "chat_history": formatted_history, # Från session state
                        "input": prompt                  # Från chatt-rutan
                    })
                    
                    st.markdown(response)
            
            # d. Lägg till AI:ns svar i historiken Add the AI answer to the history
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.error("Kunde inte ladda spelardata. Appen kan inte starta.")