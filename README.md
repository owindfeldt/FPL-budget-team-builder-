FPL Budget Team Builder


A Generative AI-powered FPL team builder. This Streamlit app uses In-Context Learning (LangChain & GPT-4) and chat memory to suggest teams based on the 2023-24 season data. The user can choose a budget and formation, and the AI will provide team recommendations and explanations.

This guide provides the technical steps to install and run this application locally.


Prerequisites

Before you begin, please ensure you have the following installed:

- Python: Version 3.9 or later.

- Git: Required to clone the repository.

- OpenAI API Key: You must have your own valid OpenAI API key (starting with sk-...).

1. Installation

Follow these steps to set up the project on your local machine.

- Step 1: Clone the Repository
Open your Terminal (or Anaconda Prompt) and run the following command to download the project:

git clone [https://github.com/ditt-anvandarnamn/ditt-repo-namn.git](https://github.com/ditt-anvandarnamn/ditt-repo-namn.git)


(Note: Replace the URL with your actual GitHub repository URL.)


- Step 2: Navigate to the Project Directory
Change into the newly created folder:

cd fpl-budget-team-builder


(Note: This assumes your repo is named fpl-budget-team-builder.)


- Step 3: Install Required Packages
Install all necessary Python libraries using the requirements.txt file:

pip install -r requirements.txt


2. How to Run the Application

Once the installation is complete:

- Ensure you are still in the project's root directory in your Terminal.

- Run the following command to start the Streamlit server:

- streamlit run app.py


The application will automatically open in your web browser.


3. How to Use the App

- Enter API Key: First, go to the sidebar and paste your personal OpenAI API key into the field "Enter your OpenAI API Key (sk-...)".

- Set Team Settings: Use the controls in the sidebar to set your desired Budget (e.g., 100M) and Formation (e.g., 1 GK, 4 DEF, 4 MID, 2 FWD).

- Start Chatting: Type your first prompt in the chat box (e.g., "Can you give me three different team suggestions?").

- Ask Follow-up Questions: Thanks to the app's memory, you can ask follow-up questions (e.g., "In team 1, please swap Saka for a cheaper player from Liverpool.").
