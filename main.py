from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_response_to_prompt(prompt, model="gpt-4o"):
    return client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}]).choices[0].message.content

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define HTML templates without inline CSS
html_templates = {
    "index": """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Procrast-Assist</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="/static/styles.css">
    </head>
    <body>
        <div class="banana-background">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
        </div>
        <div class="container">
            <div class="logo">Procrast<span class="highlight">Assist</span></div>
            <h1>Procrastination Assistant</h1>
            <p class="subtitle">Enter a task you should be doing and get three great reasons to avoid it!</p>
            
            <form action="/generate" method="post">
                <div class="input-group">
                    <input type="text" name="task" placeholder="Enter your task..." required>
                </div>
                <button type="submit">Find Excuses</button>
            </form>
            
            <div class="footer">Powered by GPT-4o</div>
        </div>
    </body>
    </html>
    """,
    
    "result": """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Your Procrastination Guide</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="/static/styles.css">
    </head>
    <body>
        <div class="banana-background">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
        </div>
        <div class="container">
            <div class="logo">Procrast<span class="highlight">Assist</span></div>
            <h1>Perfect Excuses Found!</h1>
            
            <div class="task-container">
                <div class="task-title">Why you should avoid:</div>
                <div class="task-name">{{ task }}</div>
            </div>
            
            <div class="reasons-container">
                <div class="reasons">{{ reasons }}</div>
            </div>
            
            <a href="/" class="back-button">Find More Excuses</a>
            
            <div class="footer">Powered by GPT-4o</div>
        </div>
    </body>
    </html>
    """
}

@app.get("/", response_class=HTMLResponse)
async def index():
    return html_templates["index"]

@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, task: str = Form(...)):
    # Generate the prompt
    prompt = f"""Give me exactly 3 humorous reasons why someone SHOULD procrastinate on '{task}'. 
    Make each reason witty, absurd and amusing. Format as a list with each reason on a new line, starting with 1., 2., and 3. 
    Don't include any intro or conclusion text - just the 3 numbered reasons."""
    
    # Get response from OpenAI
    reasons = get_response_to_prompt(prompt)
    
    # Format the output for the HTML
    formatted_reasons = ""
    for line in reasons.strip().split('\n'):
        if line.strip():
            # Remove the number and period at the beginning of each line and wrap in div
            reason_text = line.strip()
            if reason_text[0].isdigit() and '. ' in reason_text[:4]:
                reason_text = reason_text[reason_text.find('. ')+2:]
            formatted_reasons += f'<div class="reason-item">{reason_text}</div>\n'
    
    # Return the result template with the task and reasons
    result = html_templates["result"].replace("{{ task }}", task)
    return result.replace("{{ reasons }}", formatted_reasons)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)