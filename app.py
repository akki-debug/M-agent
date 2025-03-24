import streamlit as st
import asyncio
from autogen import AssistantAgent, UserProxyAgent
from openai import AuthenticationError

st.set_page_config(page_title="AutoGen Chat", layout="wide")
st.write("""# AutoGen Chat Agents""")

class TrackableAssistantAgent(AssistantAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name, avatar="🤖"):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)

class TrackableUserProxyAgent(UserProxyAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name, avatar="👤"):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)

# Initialize session state for messages and agents
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agents_initialized" not in st.session_state:
    st.session_state.agents_initialized = False

# Sidebar configuration
with st.sidebar:
    st.header("OpenAI Configuration")
    selected_model = st.selectbox("Model", ['gpt-3.5-turbo', 'gpt-4'], index=1)
    selected_key = st.text_input("API Key", type="password")
    
    # Add reset conversation button
    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.session_state.agents_initialized = False
        st.rerun()

# Display chat messages
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Chat input and processing
user_input = st.chat_input("Type something...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    if not selected_key or not selected_model:
        st.warning('Please provide valid OpenAI API key and select a model', icon="⚠️")
        st.stop()

    # Initialize agents if not exists
    if not st.session_state.agents_initialized:
        llm_config = {
            "request_timeout": 600,
            "config_list": [{"model": selected_model, "api_key": selected_key}]
        }
        
        try:
            st.session_state.assistant = TrackableAssistantAgent(
                name="assistant",
                llm_config=llm_config,
                system_message="You are a helpful AI assistant."
            )
            
            st.session_state.user_proxy = TrackableUserProxyAgent(
                name="user",
                human_input_mode="NEVER",
                llm_config=llm_config,
                code_execution_config={"work_dir": "coding", "use_docker": False},
                default_auto_reply="Continue"
            )
            
            st.session_state.agents_initialized = True
        except Exception as e:
            st.error(f"Error initializing agents: {str(e)}")
            st.stop()

    # Process message with existing agents
    try:
        with st.spinner("Thinking..."):
            # Create async event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def chat_task():
                await st.session_state.user_proxy.a_initiate_chat(
                    st.session_state.assistant,
                    message=user_input,
                    clear_history=not st.session_state.agents_initialized
                )
                # Store assistant's response
                if st.session_state.assistant.last_message():
                    response = st.session_state.assistant.last_message()["content"]
                    st.session_state.messages.append({"role": "assistant", "content": response})

            loop.run_until_complete(chat_task())
            
    except AuthenticationError:
        st.error("Authentication failed. Please check your API key.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
