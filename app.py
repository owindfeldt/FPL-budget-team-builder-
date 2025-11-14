
import streamlit as st
import pandas as pd
import numpy as np

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

#  DATA PREPARATION 
# This function is identical, it just loads our data
@st.cache_data
def load_and_prepare_data():
    st.info("Loading and preparing 23/24 FPL data")
    
    try:
        url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2023-24/gws/merged_gw.csv"
        df_raw = pd.read_csv(url)
    except Exception as e:
        st.error(f"Could not load data from GitHub: {e}")
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
    
    # Step 2: Format the data as text
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
    
    st.success("Data loading complete!")
    return output_text

# AI LOGIC  

def get_ai_chain(api_key, player_data_text):
    
    # 1. The System Prompt sets the rules and provides the data
    # THIS IS THE BLOCK YOU ASKED TO CHANGE:
    system_prompt = f"""
    You are an expert on Fantasy Premier League (FPL).
    Your goal is to help the user build a team.
    You must base all your choices and calculations on the following player data (from the 2023-24 season).

    PLAYER DATA:
    ---
    {player_data_text}
    ---

    Conversation Rules:
    - Always respond in the SAME language as the user's last message.
    - Be polite and helpful.
    - You must remember previous messages in the conversation.
    - The user will provide you with their "Current Settings" (Budget and Formation)
      in each message. You must follow these settings.
    """
    
    # 2. Load the model
    llm = ChatOpenAI(
        openai_api_key=api_key,
        model_name="gpt-4o-mini",
        temperature=0.7
    )
    
    # 3. Create the new prompt template
    # It now takes 4 variables: budget, formation, chat_history, input
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{chat_history}"), 
        ("user", """
        My Current Settings:
        - Budget: {budget} million
        - Formation: {formation}
        
        My Question: {input}
        """)
    ])
    
    # 4. Create a simple chain
    chain = prompt | llm | StrOutputParser()
    
    return chain

#  STREAMLIT INTERFACE 

st.set_page_config(layout="wide")
st.title("FPL Budget Team Builder")
st.markdown("Use the sidebar to set your budget and formation. Then, ask questions in the chat!")

# Load our data
player_data = load_and_prepare_data()

# --- SIDEBAR ---
st.sidebar.header("Configuration")
user_api_key = st.sidebar.text_input(
    "Enter your OpenAI API Key (sk-...)",
    type="password",
    help="Your key is not stored, it is only used for this session."
)

st.sidebar.divider()
st.sidebar.header("Your Team Settings")

# 1. Budget Slider 
user_budget = st.sidebar.slider(
    "Select your budget (in millions):",
    min_value=80.0,
    max_value=120.0,
    value=100.0, # Default value
    step=0.5
)

# 2. Formation Selector 
col1, col2 = st.sidebar.columns(2)
gk_count = col1.number_input("Goalkeepers (GK):", min_value=1, max_value=1, value=1)
def_count = col2.number_input("Defenders (DEF):", min_value=3, max_value=5, value=4)
mid_count = col1.number_input("Midfielders (MID):", min_value=2, max_value=5, value=4)
fwd_count = col2.number_input("Forwards (FWD):", min_value=1, max_value=3, value=2)

user_formation = f"{gk_count} GK, {def_count} DEF, {mid_count} MID, {fwd_count} FWD"
total_players = gk_count + def_count + mid_count + fwd_count

if total_players != 11:
    st.sidebar.error(f"Your team must have 11 players. You have {total_players}.")
else:
    st.sidebar.success(f"You have selected {total_players} players.")


#  CHAT LOGIC 
if player_data:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "ai_chain" not in st.session_state:
        st.session_state.ai_chain = None

    # Display all old messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Wait for new user input
    if prompt := st.chat_input("Your question... (e.g., 'Give me 3 team suggestions')"):
        
        # Check if API key is present
        if not user_api_key:
            st.error("Please enter your OpenAI API key in the sidebar to begin.")
        # Check if formation is 11 players
        elif total_players != 11:
             st.error("Please adjust your formation in the sidebar. You must have exactly 11 players.")
        else:
            # Initialize the chain if it doesn't exist
            if st.session_state.ai_chain is None:
                st.session_state.ai_chain = get_ai_chain(user_api_key, player_data)
            
            # a. Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # b. Format the history for the AI
            formatted_history = []
            for msg in st.session_state.messages[:-1]:
                if msg["role"] == "user":
                    formatted_history.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    formatted_history.append(AIMessage(content=msg["content"]))
            
            # c. Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("The AI is thinking..."):
                    # Invoke the chain, passing ALL variables
                    response = st.session_state.ai_chain.invoke({
                        "budget": user_budget,           # From the slider
                        "formation": user_formation,     # From the number inputs
                        "chat_history": formatted_history, # From session state
                        "input": prompt                  # From the chat box
                    })
                    
                    st.markdown(response)
            
            # d. Add AI response to history
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.error("Could not load player data. The app cannot start.")

