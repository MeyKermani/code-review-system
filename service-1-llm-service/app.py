import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # Import Pydantic for request validation
from openai import OpenAI
from fastapi.responses import JSONResponse

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
                    "content": """Check the following Python function and give 5 to 10 short and useful suggestions
                     ignore indentation and breaking things into multiple line, the suggestions should be specific 
                     strings and the strings should be in quotations and commas between each other and dont number them
                      and dont add any other explanation:\n""" + function_code
                }
            ],
            max_tokens=300
        )
        result = json.loads(response.content)
        output = result["choices"][0]["message"]["content"].replace('\n', '')
        output1 = output.replace('\"', '').strip()
        output2 = output1.split(',')
        print(output2)
        cleaned_suggestions = [s.strip() for s in output2]
        final_suggestions = []
        for suggestion in cleaned_suggestions:
            if not suggestion.__contains__('.') and not suggestion.__contains__(')') and not suggestion.__contains__('(')\
                    and len(suggestion) > 20:
                final_suggestions.append(suggestion)

        # output_dict = {
        #     "suggestions": final_suggestions
        # }
        # print(output_dict)
        # json_output = json.dumps(output_dict, indent=4)
        #response_content = json.dumps({"suggestions": final_suggestions}, indent=4)
      
        return JSONResponse(content={"suggestions": final_suggestions})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
