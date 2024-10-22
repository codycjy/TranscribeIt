# TranscribeIt
This is a self-hosted web application that allows users to transcribe audio files. 
It is built in Streamlit and OpenAi's Whispers.
It is in very early stages of development but you can try it now.

## How to run
1. Clone the repository
2. Install docker and docker-compose
3. (Optional) Install nvidia-docker if you have a GPU
4. Run `docker-compose up --build` (I feel sorry but that's the only way for now)

## TODO
- [x] Create a basic Streamlit app
- [x] Integrate OpenAi's Whispers
- [ ] Use github actions to push to dockerhub
- [ ] Utilize llm to summarize the transcriptions
- [ ] Better docker compose setup

Welcome to contribute to this project. 

