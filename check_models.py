from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("CODYSSEY_API_KEY"),
    base_url=os.getenv("CODYSSEY_BASE_URL")
)

models = client.models.list()

for model in models.data:
    print(model.id)