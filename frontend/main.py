import streamlit as st
import requests



# TODO: use ENV to decide API URL
API_URL = "http://api:8000"


def create_transcription(url: str):
    """Create a new transcription task"""
    if not url:
        raise ValueError("URL cannot be empty")
    response = requests.post(f"{API_URL}/transcribe", json={"url": url})
    response.raise_for_status()
    return response.json()


def get_all_transcriptions():
    """Get all transcription tasks"""
    response = requests.get(f"{API_URL}/transcriptions")
    response.raise_for_status()
    return response.json()


def delete_transcription(task_id: int):
    """Delete a transcription task"""
    response = requests.delete(f"{API_URL}/transcriptions/{task_id}")
    response.raise_for_status()
    return response.json()

@st.cache_data
def get_model_name():
    """Get the model name"""
    response = requests.get(f"{API_URL}/model")
    response.raise_for_status()
    return response.json().get("model", "Unknown")


def main():
    st.title("Video Transcription Service")

    # Create tabs
    tab1, tab2 = st.tabs(["New Transcription", "Transcription History"])

    with tab1:
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

    with tab2:
        # Add a refresh button
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

                    with st.expander(f"{status_emoji} {display_title} - {task.get('created_at')}", expanded=False):
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

                        # Add buttons
                        col1, col2, col3 = st.columns([1, 1, 2])
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

                        # Show processing message
                        if not task.get('content') and status not in ["failed", "completed"]:
                            st.info("In progress...")
            else:
                st.info("No transcriptions found")
        except Exception as e:
            st.error(f"Falied to fetch transcriptions: {str(e)}")

    # Show configurations # TODO: use ENV to decide model and database
    st.sidebar.markdown("### Configurations")
    st.sidebar.text(f"Database: /app/transcriptions.db")
    model_name = get_model_name()
    st.sidebar.text(f"Model: {model_name}")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Transcribe It!",
        page_icon="🎥"
    )
    main()
