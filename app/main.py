from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
from jinja2 import Environment, FileSystemLoader
import shutil
import os

app = FastAPI()

# Templates directory
templates = Jinja2Templates(directory="app/templates")

# Ensure static folder exists
if not os.path.exists("app/static"):
    os.makedirs("app/static")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


# -----------------------------
# HOME PAGE (Landing)
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# -----------------------------
# BUILDER PAGE
# -----------------------------
@app.get("/builder", response_class=HTMLResponse)
async def builder(request: Request):
    return templates.TemplateResponse("builder.html", {"request": request})


# -----------------------------
# GENERATE PORTFOLIO (View)
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
        image_path = f"app/static/{profile_image.filename}"
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
        image_path = f"app/static/{profile_image.filename}"
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
# DOWNLOAD PORTFOLIO (HTML)
# -----------------------------
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
