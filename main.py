from fastapi import FastAPI
from requests import Session
from pydantic import BaseSettings, Field, BaseConfig
from fastapi.responses import HTMLResponse

html = """
<style>
body {display: flex;flex-direction: column;align-items: center;justify-content: center;height: 100vh;background-image: url(https://wallpaperaccess.com/full/17520.jpg);background-size: cover;background-position: center;background-repeat: no-repeat;background-attachment: fixed;
}
#prompt, #result {width: 100%;outline: none;padding: 10px;font-size: 1.2rem;font-family: monospace;margin-bottom: 10px;
}</style>
<main><textarea id="result" rows="12" cols="50" disabled placeholder="Chatbot response will appear here..."></textarea><hr/>
<textarea id="prompt" rows="6" cols="50" placeholder="Prompt chatbot here..."></textarea>
<script>const prompt = document.getElementById("prompt");
const result = document.getElementById("result");
const getResponse = async()=>{
    const res = await fetch("/complete/"+prompt.value, {method: "POST",headers: {"Content-Type": "application/json"},});
    const data = await res.json();
    result.value = data.result;}
prompt.addEventListener("keyup", async(e)=>{if(e.key === "Enter"){await getResponse()}})</script>
"""
class Settings(BaseSettings):
    class Config(BaseConfig):
        env_file = ".env"
    api_key: str = Field(env="API_KEY")
    api_url: str = Field(env="API_URL")
    
settings = Settings()

class ApiClient:
    def __init__(self, api_key: str, api_url: str):
        self.session = Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        self.api_url = api_url

    def complete(self, prompt:str, temperature:float)->str:
        response = self.session.post(self.api_url, json={"model":"text-davinci-003", "prompt":prompt, "max_tokens":512, "temperature":temperature})
        return response.json()["choices"][0]["text"]

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(html)

@app.post("/complete/{prompt}")
def complete(prompt: str, temperature: float = 1):
    api_client = ApiClient(settings.api_key, settings.api_url)
    result = api_client.complete(prompt, temperature)
    return  {"result": result}