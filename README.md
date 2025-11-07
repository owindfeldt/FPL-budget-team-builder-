# FPL-budget-team-builder-
A Generative AI-powered FPL team builder. This Streamlit app uses In-Context Learning (LangChain &amp; GPT-4) and chat memory to suggest teams based on 2023-24 data. The user can choose budget and formation, chat with the AI  and It will give recommendations regarding players and teambuilder.

This is a short technical guide for installing and running the "FPL Budget Team Builder" application.


1. Prerequisites
Before you begin, please ensure you have the following installed:

- Python: Version 3.9 or later (the project was developed using Anaconda and Python 3.13).
- OpenAI API Key: You must have your own valid OpenAI API key (one that starts with sk-...) for the AI model to function.


2. Installation
Follow these steps to install the required packages:

  - Download and unzip the project folder (fpl_projekt).
  - Open your Terminal (or Anaconda Prompt).
  - Navigate to the project folder. Example (replace with your path):  cd /Users/yourname/Desktop/fpl_projekt
  - Install all necessary Python libraries by running the following command:  pip install streamlit pandas langchain-openai langchain-core

(Note: numpy is typically installed automatically with pandas.)


3. How to Run the Application
Once the installation is complete, follow these steps:

  - Ensure you are still in the project folder (fpl_projekt) in your Terminal.
  - Run the following command to start the Streamlit server:  streamlit run app.py

The application should now automatically open in your web browser at a local address (e.g., http://localhost:8501).


4. How to Use the App

Once the app is running in your browser:

  - Enter API Key: First, go to the sidebar and paste your personal OpenAI API key into the field "Ange din OpenAI API-nyckel (sk-...)". This is mandatory for the app to work.
  - Set Team Settings: Use the controls in the sidebar to set your desired Budget (e.g., 100M) and Formation (e.g., 1 GK, 4 DEF, 4 MID, 2 FWD).
  - Start Chatting: Type your first prompt in the chat box at the bottom, for example: "Can you give me three different team suggestions?"
  - Ask Follow-up Questions: Thanks to the app's memory, you can now ask follow-up questions, such as: "In team 1, please swap Saka for a cheaper player from Liverpool."
