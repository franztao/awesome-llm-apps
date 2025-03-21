# Import the required libraries
from embedchain.pipeline import Pipeline as App
from embedchain.loaders.github import GithubLoader
import streamlit as st
import os

loader = GithubLoader(
    config={
        "token":"Your GitHub Token",
        }
    )

# Create Streamlit app
st.title("Chat with GitHub Repository 💬")
st.caption("This app allows you to chat with a GitHub Repo using OpenAI API")

# Get LLM API Key from user
openai_access_token = st.text_input("LLM API Key", type="password")

# If LLM API Key is provided, create an instance of App
if openai_access_token:
    os.environ["OPENAI_API_KEY"] = openai_access_token
    # Create an instance of Embedchain App
    app = App()
    # Get the GitHub repo from the user
    git_repo = st.text_input("Enter the GitHub Repo", type="default")
    if git_repo:
        # Add the repo to the knowledge base
        app.add("repo:" + git_repo + " " + "type:repo", data_type="github", loader=loader)
        st.success(f"Added {git_repo} to knowledge base!")
        # Ask a question about the Github Repo
        prompt = st.text_input("Ask any question about the GitHub Repo")
        # Chat with the GitHub Repo
        if prompt:
            answer = app.chat(prompt)
            st.write(answer)