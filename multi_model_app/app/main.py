import streamlit as st
from openai_client import OpenAIClient
from utils import load_models_config, load_api_key, Model, get_latest_responses_for_summary

# --- Session State Initialization ---
if "last_summary" not in st.session_state:
    st.session_state.last_summary = None

# --- Configuration Loading ---
CONFIG_LOADED_SUCCESSFULLY = False
try:
    models_config_data = load_models_config()
    if not models_config_data or "models" not in models_config_data:
        st.error("Failed to load/parse models_config.json. Check format/existence.")
        st.stop()
    
    api_keys_loaded = {}
    all_model_configs = models_config_data.get("models", [])
    if "evaluator_model" in models_config_data:
        all_model_configs.append(models_config_data["evaluator_model"])

    for model_conf in all_model_configs:
        if model_conf and "api_key_name" in model_conf:
            key_name = model_conf["api_key_name"]
            if key_name not in api_keys_loaded:
                try:
                    api_key_value = load_api_key(key_name)
                    api_keys_loaded[key_name] = api_key_value
                    if "YOUR_OPENAI_API_KEY_HERE" in api_key_value or not api_key_value.strip():
                        st.warning(f"API key '{key_name}' is placeholder/empty.")
                except (FileNotFoundError, KeyError, ValueError) as e:
                    st.error(f"Failed to load API key '{key_name}': {e}")
                    api_keys_loaded[key_name] = None
    CONFIG_LOADED_SUCCESSFULLY = True
except Exception as e:
    st.error(f"Critical error during configuration loading: {e}")
    st.stop()

# --- Initialize Model Objects and Evaluator ---
if CONFIG_LOADED_SUCCESSFULLY:
    if "model_objects" not in st.session_state:
        st.session_state.model_objects = {}
        valid_models_for_chat = []
        for model_conf in models_config_data.get("models", []):
            model_name = model_conf.get("name")
            api_key_name = model_conf.get("api_key_name")
            api_key = api_keys_loaded.get(api_key_name)
            if not (model_name and api_key_name and api_key and "YOUR_OPENAI_API_KEY_HERE" not in api_key):
                st.warning(f"Skipping chat model '{model_name}' due to missing info or placeholder key.")
                continue
            try:
                client = OpenAIClient(model_name=model_name, api_key=api_key)
                model_instance = Model(name=model_name, api_key_name=api_key_name, context_length=model_conf.get("context_length", 10))
                model_instance.client = client
                st.session_state.model_objects[model_name] = model_instance
                valid_models_for_chat.append(model_name)
            except Exception as e:
                st.error(f"Error initializing client for model '{model_name}': {e}")
        
        if not st.session_state.model_objects:
            st.error("No chat models could be initialized.")
            st.stop()
        st.session_state.selected_model_name = valid_models_for_chat[0] if valid_models_for_chat else None

    if "evaluator_model_obj" not in st.session_state:
        eval_config = models_config_data.get("evaluator_model")
        if eval_config:
            name, key_name = eval_config.get("name"), eval_config.get("api_key_name")
            api_key = api_keys_loaded.get(key_name)
            if name and key_name and api_key and "YOUR_OPENAI_API_KEY_HERE" not in api_key:
                try:
                    client = OpenAIClient(model_name=name, api_key=api_key)
                    instance = Model(name=name, api_key_name=key_name, context_length=eval_config.get("context_length", 2000))
                    instance.client = client
                    st.session_state.evaluator_model_obj = instance
                except Exception as e:
                    st.session_state.evaluator_model_obj = None
                    st.error(f"Error initializing evaluator '{name}': {e}")
            else:
                st.session_state.evaluator_model_obj = None
        else:
            st.session_state.evaluator_model_obj = None

if not st.session_state.get("selected_model_name"):
    if CONFIG_LOADED_SUCCESSFULLY: st.error("No models available for chat.")
    st.stop()

# --- Sidebar ---
st.sidebar.title("Model Controls")

# Evaluator Status
if "evaluator_model_obj" in st.session_state: # Check if processed
    if st.session_state.evaluator_model_obj:
        st.sidebar.info(f"Evaluator: '{st.session_state.evaluator_model_obj.name}' loaded.")
    else: # More detailed error based on config
        eval_conf = models_config_data.get("evaluator_model")
        if not eval_conf: st.sidebar.warning("No evaluator configured. Summarization disabled.")
        elif not eval_conf.get("name") or not eval_conf.get("api_key_name"): st.sidebar.warning("Evaluator config incomplete. Summarization disabled.")
        else: st.sidebar.warning(f"Evaluator '{eval_conf.get('name')}' key missing/placeholder. Summarization disabled.")
st.sidebar.markdown("---")

current_model_obj = st.session_state.model_objects[st.session_state.selected_model_name]
available_model_names = list(st.session_state.model_objects.keys())
selected_idx = available_model_names.index(st.session_state.selected_model_name)

new_selected_model_name = st.sidebar.selectbox("Active Model:", available_model_names, index=selected_idx, key="model_selector")
if new_selected_model_name != st.session_state.selected_model_name:
    st.session_state.selected_model_name = new_selected_model_name
    current_model_obj = st.session_state.model_objects[new_selected_model_name]
    st.rerun()


# Context length
ctx_len_key = f"context_length_input_{current_model_obj.name}"
new_ctx_len = st.sidebar.number_input(f"Context (msgs) for {current_model_obj.name}", min_value=1, max_value=100, value=current_model_obj.conversation.context_length, step=1, key=ctx_len_key)
if new_ctx_len != current_model_obj.conversation.context_length:
    current_model_obj.context_length = new_ctx_len
    current_model_obj.conversation.context_length = new_ctx_len
    current_model_obj.conversation.enforce_context_limit()
    st.rerun()

if st.sidebar.button("Clear Conversation", key=f"clear_conv_{current_model_obj.name}"):
    current_model_obj.conversation.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### Multi-Model Actions")
summarize_all_button = st.sidebar.button("Summarize All Responses")

if summarize_all_button:
    evaluator = st.session_state.get("evaluator_model_obj")
    chat_models = st.session_state.get("model_objects")
    if evaluator and chat_models:
        latest_responses = get_latest_responses_for_summary(chat_models)
        if not latest_responses or all(not r for r in latest_responses.values()):
            st.sidebar.info("No responses from chat models to summarize yet.")
        else:
            prompt_parts = ["You are an expert summarizer and response evaluator.", "Multiple AI models have responded to a user's query. Your task is to synthesize these responses into a single, comprehensive, and accurate summary.", "Please also briefly critique the set of responses if you notice any significant discrepancies, inaccuracies, or areas for improvement.", "\nHere are the responses from the models:\n"] 
            for name, resp in latest_responses.items():
                if resp: prompt_parts.append(f"--- Response from Model {name} ---\n{resp}\n")
            prompt_parts.append("---\nPlease provide your summary and brief evaluation below:")
            summarization_prompt = "\n".join(prompt_parts)
            
            st.sidebar.markdown("---")
            st.sidebar.subheader("Consolidated Summary & Evaluation:")
            summary_placeholder = st.sidebar.empty()
            try:
                with summary_placeholder.container():
                    streamed_summary = evaluator.client.get_chat_completion(messages=[{"role": "user", "content": summarization_prompt}], stream=True)
                    full_summary = st.write_stream(streamed_summary)
                    st.session_state.last_summary = full_summary
                    st.sidebar.success("Summary generated!")
            except Exception as e:
                st.sidebar.error(f"Summarization error: {e}")
                st.session_state.last_summary = None
    elif not evaluator: st.sidebar.error("Evaluator model not available.")
    else: st.sidebar.warning("No chat models loaded.")

# "Use Summary" Checkbox
if st.session_state.get("last_summary"):
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"Context Override for {current_model_obj.name}")
    cb_key = f"use_summary_{current_model_obj.name}"
    if cb_key not in st.session_state: st.session_state[cb_key] = False
    
    st.sidebar.checkbox(f"Use summary as context for next query with {current_model_obj.name}", key=cb_key)
    if st.session_state[cb_key]:
        st.sidebar.caption("Next message will use the summary as primary context.")

# --- Main Chat Area ---
st.title(f"Chat with: {current_model_obj.name}")
for message in current_model_obj.conversation.get_messages():
    with st.chat_message(message["role"]): st.markdown(message["content"])

if prompt := st.chat_input("Ask your question..."):
    current_model_obj.conversation.add_message(role="user", content=prompt)
    with st.chat_message("user"): st.markdown(prompt)

    api_messages = []
    use_summary_key = f"use_summary_{current_model_obj.name}"
    if st.session_state.get(use_summary_key, False) and st.session_state.get("last_summary"):
        st.info(f"Using overall summary as context for {current_model_obj.name} for this turn.")
        api_messages = [
            {"role": "system", "content": f"You are {current_model_obj.name}. Use this summary as primary context: {st.session_state.last_summary}"},
            {"role": "user", "content": prompt}
        ]
        st.session_state[use_summary_key] = False # Reset after use
    else:
        api_messages = current_model_obj.conversation.get_messages()

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_resp = ""
        try:
            stream = current_model_obj.client.get_chat_completion(messages=api_messages, stream=True)
            for chunk in stream:
                if chunk: full_resp += chunk; placeholder.markdown(full_resp + "▌")
            placeholder.markdown(full_resp)
            current_model_obj.conversation.add_message(role="assistant", content=full_resp)
        except Exception as e:
            st.error(f"API Error: {e}")
```
