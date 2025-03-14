import json
import uuid
import os
import re
import http.client
from fastapi import FastAPI, HTTPException, BackgroundTasks
from git import Repo
from pydantic import BaseModel, HttpUrl

app = FastAPI()

jobs = {}
jobs_names = [x[0] for x in os.walk("./repos")]
for job in jobs_names:
    if len(job) > 8:
        job_id = job.replace('./repos/', "").replace("/", "").replace(".", "")[:36]
        jobs[job_id] = {"status": "completed", "repo_path": f"./repos/{job_id}"}


class AnalyzeRequest(BaseModel):
    repo_url: HttpUrl


class AnalyzeFunctionRequest(BaseModel):
    job_id: str
    function_name: str


@app.post("/analyze/start")
async def start_analysis(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    background_tasks.add_task(download_repo, request.repo_url, job_id)
    return {"job_id": job_id}


def download_repo(repo_url: str, job_id: str):
    jobs[job_id] = {"status": "pending", "repo_path": None}
    try:
        repo_path = f"./repos/{job_id}"
        Repo.clone_from(repo_url, repo_path)
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["repo_path"] = repo_path
    except Exception as e:
        print(f"Error cloning repository: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.post("/analyze/function")
async def analyze_function(request: AnalyzeFunctionRequest):
    job_id = request.job_id
    function_name = request.function_name
    try:
        if job_id not in jobs.keys() or jobs[job_id]["status"] != "completed":
            raise HTTPException(status_code=404, detail="Job not found or not completed.")

        repo_path = jobs[job_id]["repo_path"]
        function_code = extract_function_code(repo_path, function_name)

        # Call the LLM service

        conn = http.client.HTTPConnection("service1", 8001)
        payload = json.dumps({
            "function_code": function_code
        })
        headers = {
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/analyze", payload, headers)
        res = conn.getresponse()
        data = res.read()
        response_dict = json.loads(data.decode("utf-8"))  # Decode the response and parse it as JSON
        return {"suggestions": response_dict["suggestions"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def extract_function_code(repo_path: str, function_name: str) -> str:
    """
    Locate and extract the code for a specific function within a repository.

    Args:
        repo_path (str): Path to the repository folder.
        function_name (str): Name of the function to locate.

    Returns:
        str: The extracted code for the function as a string, or '' if not found.
    """
    module_name = function_name.split('.')[0]
    function_name = function_name.split('.')[1]
    # Regex pattern to match the function definition
    function_pattern = re.compile(rf"def\s+{function_name}\s*\(.*\):")

    # Traverse the repository files
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py") and file == f'{module_name}.py':  # Only process the specific Python file
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    # Find the function definition in the file
                    function_code = []
                    inside_function = False
                    for line in lines:
                        if not inside_function and function_pattern.match(line):
                            # Start extracting the function code
                            inside_function = True
                            function_code.append(line)
                        elif inside_function:
                            # Extract the function body
                            function_code.append(line)
                            # Stop when indentation decreases (end of function)
                            if line.strip() == "" or len(line) - len(line.lstrip()) == 0:
                                break

                    if function_code:
                        return "".join(function_code)  # Return the extracted function code

                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

    # Return empty string if the function is not found
    return ''
