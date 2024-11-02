import random
import string
import requests
import streamlit as st
from config import API_URL


# USE ENDPONIT TO combine BASE URL and ENDPOINT
def random_key_prefix():
    return ''.join(random.choices(string.ascii_lowercase, k=4))


def create_transcription(url: str):
    """Create a new transcription task"""
    if not url:
        raise ValueError("URL cannot be empty")
    response = requests.post(
        f"{API_URL}/transcriptions", json={"url": url}, timeout=10)
    response.raise_for_status()
    return response.json()


def get_all_transcriptions():
    """Get all transcription tasks"""
    response = requests.get(f"{API_URL}/transcriptions", timeout=10)
    response.raise_for_status()
    return response.json()


def delete_transcription(task_id: int):
    """Delete a transcription task"""
    response = requests.delete(
        f"{API_URL}/transcriptions/{task_id}", timeout=10)
    response.raise_for_status()
    return response.json()


def summary_transcription(task_id: int, model: dict, provider: str, max_tokens: int = 300):
    """Get a transcription task"""
    model = {
        "provider": provider,
        "model": model,
        "max_tokens": max_tokens
    }
    response = requests.post(
        f"{API_URL}/summaries/{task_id}", json=model, timeout=10)
    if response.status_code != 200:
        raise ValueError(response.json()['detail'])
    return response.json()


@st.cache_data
def get_summarize_provider():
    """Get all summarize provider"""
    response = requests.get(f"{API_URL}/model/available_providers", timeout=10)
    response.raise_for_status()
    return response.json()


@st.cache_data
def get_summarize_model(provider: str):
    """Get all summarize model"""
    response = requests.post(
        f"{API_URL}/model/available_models", json={"provider": provider}, timeout=10)
    response.raise_for_status()
    return response.json()


@st.cache_data
def get_model_name():
    """Get the model name"""
    response = requests.get(f"{API_URL}/model/transcribe", timeout=10)
    response.raise_for_status()
    return response.json().get("model", "Unknown")


def transcript_tab():
    url = st.text_input("Input of video url")

    if st.button("Start Transcription"):
        if url:
            with st.spinner("Submitting job..."):
                try:
                    task = create_transcription(url)
                    st.success(f"Job submitted, task ID: {task.get('id')}")
                except Exception as e:
                    st.error(f"Falied to submit job: {str(e)}")
        else:
            st.warning("Please input a valid Video URL")


def item_unit(task):
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    with col1:
        if st.button("Delete", key=f"delete_{task.get('id')}"):
            try:
                delete_transcription(task.get('id'))
                st.success(
                    f"Task {task.get('id')} deleted")
                st.rerun()
            except Exception as e:
                st.error(
                    f"Falied to delete task: {str(e)}")
    with col2:
        if st.button("Retry", key=f"retry_{task.get('id')}"):
            try:
                new_task = create_transcription(
                    task.get('youtube_url'))
                st.success(
                    f"Retrying task, new task ID: {new_task.get('id')}")
                st.rerun()
            except Exception as e:
                st.error(f"Falied to retry task: {str(e)}")
    with col3:
        if task.get('content'):
            st.download_button(
                label="Download Transcript",
                data=task.get('content'),
                file_name=f"{task.get('title', 'transcript')}.txt",
                mime="text/plain",
                key=f"download_{task.get('id')}"
            )
        else:
            st.write("")

    with col4:
        if st.session_state.get('model') is None or st.session_state.get('provider') is None:
            st.warning("Please select a model")
        else:
            model = st.session_state.get('model')
            provider = st.session_state.get('provider')
            max_tokens = st.session_state.get('max_tokens')
            if st.button("Summary", key=f"summary_{task.get('id')}"):
                try:
                    summary_transcription(task.get(
                        'id'), model=model, provider=provider, max_tokens=max_tokens)  # type: ignore
                    st.success(
                        f"Task {task.get('id')} summarizing")
                except Exception as e:
                    st.error(
                        f"Falied to summary task: {str(e)}")


def history_tab():

    if st.button("Refresh"):
        st.rerun()

    # Show transcriptions
    try:
        transcriptions = get_all_transcriptions()

        if transcriptions:
            for task in transcriptions:
                # Build the display title
                display_title = f"{task.get('title', 'In Progress...')}"
                status = task.get('status', '')
                status_emoji = {
                    "pending": "⏳",
                    "downloading": "📥",
                    "transcribing": "🔄",
                    "completed": "✅",
                    "failed": "❌"
                }.get(status, "")

                with st.expander(
                    f"{status_emoji} {display_title} - {task.get('created_at')}", expanded=False
                ):
                    st.markdown(f"**URL:** {task.get('youtube_url')}")
                    st.markdown(f"**Status:** {task.get('status')}")

                    if task.get('error_message'):
                        st.error(f"Error: {task.get('error_message')}")

                    if task.get('content'):
                        st.text_area(
                            "Transcript",
                            value=task.get('content'),
                            height=200,
                            key=f"content_{task.get('id')}"
                        )
                    if task.get('summary'):
                        st.text_area(
                            "Summary",
                            value=task.get('summary'),
                            height=200,
                            key=f"summary_{task.get('id')}+{random_key_prefix()}"
                        )

                    # Add buttons
                    item_unit(task)
                    # Show processing message
                    if not task.get('content') and status not in ["failed", "completed"]:
                        st.info("In progress...")
        else:
            st.info("No transcriptions found")
    except Exception as e:
        st.error(f"Falied to fetch transcriptions: {str(e)}")


def main():
    st.title("Video Transcription Service")

    # Show configurations # TODO: use ENV to decide model and database
    st.sidebar.markdown("### Configurations")
    model_name = get_model_name()
    st.sidebar.text(f"Transcribe Model: {model_name}")
    st.sidebar.text("Database: /app/transcriptions.db")
    available_provider = get_summarize_provider()['provider']
    provider = st.sidebar.selectbox("Summarize Provider", available_provider)
    available_model = get_summarize_model(provider)['available_models']
    summarize_model = st.sidebar.selectbox("Summarize Model", available_model)
    max_tokens = st.sidebar.slider('Max Token', 0, 1000, 300)  # min max default
    st.session_state.model = summarize_model
    st.session_state.provider = provider
    st.session_state.max_tokens = max_tokens

    # Create tabs
    tab1, tab2 = st.tabs(["New Transcription", "Transcription History"])

    with tab1:
        transcript_tab()

    with tab2:
        history_tab()


if __name__ == "__main__":
    st.set_page_config(
        page_title="Transcribe It!",
        page_icon="🎥"
    )
    main()
