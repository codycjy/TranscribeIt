from fastapi import FastAPI
from api.routes import models,summary,transcription


app = FastAPI()
app.include_router(models.router)
app.include_router(summary.router)
app.include_router(transcription.router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
