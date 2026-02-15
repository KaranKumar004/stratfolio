from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
import shutil
import os
import requests

app = FastAPI()

# Templates
templates = Jinja2Templates(directory="app/templates")

# Static folder for uploaded images
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")


# -----------------------------
# HOME → Redirect to Builder
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def builder(request: Request):
    return templates.TemplateResponse("builder.html", {"request": request})


# -----------------------------
# GENERATE PORTFOLIO
# -----------------------------
@app.post("/generate", response_class=HTMLResponse)
async def generate_portfolio(
    request: Request,

    template: str = Form("executive_dark.html"),
    name: str = Form(...),
    title: str = Form(...),
    summary: str = Form(...),
    skills: str = Form(""),

    job_title: List[str] = Form([]),
    company: List[str] = Form([]),
    duration: List[str] = Form([]),
    job_description: List[str] = Form([]),

    profile_image: UploadFile = File(None)
):

    # Process skills
    skills_list = [s.strip() for s in skills.split(",") if s.strip()]

    # Process experiences
    experience_list = []
    for i in range(len(job_title)):
        if job_title[i].strip():
            experience_list.append({
                "title": job_title[i],
                "company": company[i] if i < len(company) else "",
                "duration": duration[i] if i < len(duration) else "",
                "description": job_description[i] if i < len(job_description) else ""
            })

    # Handle image upload
    image_filename = None
    if profile_image and profile_image.filename:
        image_path = f"static/{profile_image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)
        image_filename = profile_image.filename

    return templates.TemplateResponse(template, {
        "request": request,
        "name": name,
        "title": title,
        "summary": summary,
        "skills": skills_list,
        "experiences": experience_list,
        "profile_image": image_filename
    })


# -----------------------------
# LIVE PREVIEW
# -----------------------------
@app.post("/preview", response_class=HTMLResponse)
async def preview_portfolio(
    request: Request,

    template: str = Form("executive_dark.html"),
    name: str = Form(""),
    title: str = Form(""),
    summary: str = Form(""),
    skills: str = Form(""),

    job_title: List[str] = Form([]),
    company: List[str] = Form([]),
    duration: List[str] = Form([]),
    job_description: List[str] = Form([]),

    profile_image: UploadFile = File(None)
):

    skills_list = [s.strip() for s in skills.split(",") if s.strip()]

    experience_list = []
    for i in range(len(job_title)):
        if job_title[i].strip():
            experience_list.append({
                "title": job_title[i],
                "company": company[i] if i < len(company) else "",
                "duration": duration[i] if i < len(duration) else "",
                "description": job_description[i] if i < len(job_description) else ""
            })

    image_filename = None
    if profile_image and profile_image.filename:
        image_path = f"static/{profile_image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)
        image_filename = profile_image.filename

    return templates.TemplateResponse(template, {
        "request": request,
        "name": name,
        "title": title,
        "summary": summary,
        "skills": skills_list,
        "experiences": experience_list,
        "profile_image": image_filename
    })


# -----------------------------
# AI SUMMARY ENHANCEMENT
# (Using Ollama locally)
# -----------------------------
@app.post("/enhance-summary")
async def enhance_summary(summary: str = Form(...)):

    prompt = f"""
Rewrite this professional summary to sound polished, executive-level,
clear, confident and concise:

{summary}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }
        )

        enhanced = response.json()["response"]

        return JSONResponse({"enhanced": enhanced})

    except:
        return JSONResponse({"enhanced": summary})
from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader

@app.post("/download")
async def download_portfolio(
    request: Request,
    template: str = Form("executive_dark.html"),
    name: str = Form(...),
    title: str = Form(...),
    summary: str = Form(...),
    skills: str = Form(""),

    job_title: List[str] = Form([]),
    company: List[str] = Form([]),
    duration: List[str] = Form([]),
    job_description: List[str] = Form([])
):

    skills_list = [s.strip() for s in skills.split(",") if s.strip()]

    experience_list = []
    for i in range(len(job_title)):
        if job_title[i].strip():
            experience_list.append({
                "title": job_title[i],
                "company": company[i] if i < len(company) else "",
                "duration": duration[i] if i < len(duration) else "",
                "description": job_description[i] if i < len(job_description) else ""
            })

    # Render template manually
    env = Environment(loader=FileSystemLoader("app/templates"))
    template_file = env.get_template(template)

    html_content = template_file.render(
        name=name,
        title=title,
        summary=summary,
        skills=skills_list,
        experiences=experience_list,
        profile_image=None,
        request=request
    )

    filename = f"{name.lower().replace(' ', '_')}_portfolio.html"

    return Response(
        content=html_content,
        media_type="text/html",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
