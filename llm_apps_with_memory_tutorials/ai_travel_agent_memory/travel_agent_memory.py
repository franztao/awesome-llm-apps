import streamlit as st
from openai import OpenAI
from mem0 import Memory

# Set up the Streamlit App
st.title("AI Travel Agent with Memory 🧳")
st.caption("Chat with a travel assistant who remembers your preferences and past interactions.")

# Set the LLM API Key
openai_api_key = st.text_input("Enter LLM API Key", type="password")

if openai_api_key:
    # Initialize OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Initialize Mem0 with Qdrant
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "host": "localhost",
                "port": 6333,
            }
        },
    }
    memory = Memory.from_config(config)

    # Sidebar for username and memory view
    st.sidebar.title("Enter your username:")
    previous_user_id = st.session_state.get("previous_user_id", None)
    user_id = st.sidebar.text_input("Enter your Username")

    if user_id != previous_user_id:
        st.session_state.messages = []
        st.session_state.previous_user_id = user_id

    # Sidebar option to show memory
    st.sidebar.title("Memory Info")
    if st.button("View My Memory"):
        memories = memory.get_all(user_id=user_id)
        if memories and "results" in memories:
            st.write(f"Memory history for **{user_id}**:")
            for mem in memories["results"]:
                if "memory" in mem:
                    st.write(f"- {mem['memory']}")
        else:
            st.sidebar.info("No learning history found for this user ID.")
    else:
        st.sidebar.error("Please enter a username to view memory info.")

    # Initialize the chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    prompt = st.chat_input("Where would you like to travel?")

    if prompt and user_id:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Retrieve relevant memories
        relevant_memories = memory.search(query=prompt, user_id=user_id)
        context = "Relevant past information:\n"
        if relevant_memories and "results" in relevant_memories:
            for memory in relevant_memories["results"]:
                if "memory" in memory:
                    context += f"- {memory['memory']}\n"

        # Prepare the full prompt
        full_prompt = f"{context}\nHuman: {prompt}\nAI:"

        # Generate response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a travel assistant with access to past conversations."},
                {"role": "user", "content": full_prompt}
            ]
        )
        answer = response.choices[0].message.content

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

        # Store the user query and AI response in memory
        memory.add(prompt, user_id=user_id, metadata={"role": "user"})
        memory.add(answer, user_id=user_id, metadata={"role": "assistant"})
    elif not user_id:
        st.error("Please enter a username to start the chat.")
