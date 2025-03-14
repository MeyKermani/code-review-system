import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # Import Pydantic for request validation
from openai import OpenAI

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# Read the environment variable
LLM_PROVIDER = os.getenv("LLM_PROVIDER")


class AnalyzeRequest(BaseModel):
    function_code: str


@app.post("/analyze")
async def analyze_function(request: AnalyzeRequest):
    function_code = request.function_code  # Extract the function code from the request
    # Call OpenAI API
    try:
        with open("secrets", "r") as file:
            api_key = file.read().strip()
        client = OpenAI(base_url="https://api.avalai.ir/v1",
                        api_key=f"{api_key}")
        if LLM_PROVIDER == "openai":
            model = "gpt-4o"
        elif LLM_PROVIDER == "deepseek":
            model = "deepseek-coder"
        else:
            model = "gpt-4o"

        response = client.chat.with_raw_response.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": """Check the following Python function and give a few suggestions
                     ignore indentation and breaking things into multiple line:\n""" + function_code
                }
            ],
            max_tokens=200
        )
        result = json.loads(response.content)
        return {"suggestions": result["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
