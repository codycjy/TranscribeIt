# TranscribeIt
This is a self-hosted web application that allows users to transcribe audio files. 
It is built in Streamlit and OpenAI's Whispers.
It is in very early stages of development but you can try it now.

## How to run
1. Clone the repository
2. Install docker and docker-compose
3. (Optional) Install [nvidia-docker](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) if you have a GPU
4. Run `docker-compose up -d` to start the app

## TODO
- [x] Create a basic Streamlit app
- [x] Integrate OpenAi's Whispers
- [x] Use github actions to push to dockerhub
- [ ] Utilize llm to summarize the transcriptions
- [ ] Better docker compose setup
- [ ] Develop a browser extension to easy add videos to the app
- [ ] Add local video support
- [ ] Use other transcription models (Maybe)

Welcome to contribute to this project. 

