from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import shutil
import os
import base64
import requests
from pathlib import Path
import re

app = FastAPI()

# Templates
templates = Jinja2Templates(directory="app/templates")

# Static folder for uploaded images
UPLOAD_DIR = "static/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.mount("/static", StaticFiles(directory="static"), name="static")


# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------
def process_image(profile_image: UploadFile) -> Optional[str]:
    """Process uploaded image and return base64 encoded string"""
    if not profile_image or not profile_image.filename:
        return None
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
    if profile_image.content_type not in allowed_types:
        raise HTTPException(400, "Invalid file type. Only JPEG, PNG, and WebP allowed.")
    
    # Read and encode image
    image_bytes = profile_image.file.read()
    
    # Validate file size (max 5MB)
    if len(image_bytes) > 5 * 1024 * 1024:
        raise HTTPException(400, "File too large. Maximum size is 5MB.")
    
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    profile_image.file.seek(0)  # Reset file pointer
    
    return image_base64


def process_form_data(
    name: str,
    title: str,
    summary: str,
    skills: str,
    email: str = "",
    phone: str = "",
    linkedin: str = "",
    github: str = "",
    website: str = "",
    job_title: List[str] = [],
    company: List[str] = [],
    duration: List[str] = [],
    job_description: List[str] = [],
    edu_degree: List[str] = [],
    edu_institution: List[str] = [],
    edu_year: List[str] = [],
    profile_image: UploadFile = None
):
    """Process and validate form data"""
    
    # Validate required fields
    if not name or not title:
        raise HTTPException(400, "Name and title are required")
    
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
    
    # Process education
    education_list = []
    for i in range(len(edu_degree)):
        if edu_degree[i].strip():
            education_list.append({
                "degree": edu_degree[i],
                "institution": edu_institution[i] if i < len(edu_institution) else "",
                "year": edu_year[i] if i < len(edu_year) else ""
            })
    
    # Process contact info
    contact_info = {
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "website": website
    }
    
    # Process image
    image_data = process_image(profile_image) if profile_image else None
    
    return {
        "name": name,
        "title": title,
        "summary": summary,
        "skills": skills_list,
        "experiences": experience_list,
        "education": education_list,
        "contact": contact_info,
        "image_data": image_data
    }


# -----------------------------
# ROUTES
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with explanation and features"""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/builder", response_class=HTMLResponse)
async def builder(request: Request):
    """Portfolio builder interface"""
    return templates.TemplateResponse("builder.html", {"request": request})


@app.post("/generate", response_class=HTMLResponse)
async def generate_portfolio(
    request: Request,
    template: str = Form("executive_dark.html"),
    name: str = Form(...),
    title: str = Form(...),
    summary: str = Form(...),
    skills: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    linkedin: str = Form(""),
    github: str = Form(""),
    website: str = Form(""),
    job_title: List[str] = Form([]),
    company: List[str] = Form([]),
    duration: List[str] = Form([]),
    job_description: List[str] = Form([]),
    edu_degree: List[str] = Form([]),
    edu_institution: List[str] = Form([]),
    edu_year: List[str] = Form([]),
    profile_image: UploadFile = File(None)
):
    """Generate portfolio with all form data"""
    try:
        data = process_form_data(
            name, title, summary, skills, email, phone, linkedin, github, website,
            job_title, company, duration, job_description,
            edu_degree, edu_institution, edu_year,
            profile_image
        )
        
        return templates.TemplateResponse(template, {
            "request": request,
            **data
        })
    
    except HTTPException as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)


@app.post("/preview", response_class=HTMLResponse)
async def preview_portfolio(
    request: Request,
    template: str = Form("executive_dark.html"),
    name: str = Form(""),
    title: str = Form(""),
    summary: str = Form(""),
    skills: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    linkedin: str = Form(""),
    github: str = Form(""),
    website: str = Form(""),
    job_title: List[str] = Form([]),
    company: List[str] = Form([]),
    duration: List[str] = Form([]),
    job_description: List[str] = Form([]),
    edu_degree: List[str] = Form([]),
    edu_institution: List[str] = Form([]),
    edu_year: List[str] = Form([]),
    profile_image: UploadFile = File(None)
):
    """Live preview of portfolio"""
    try:
        # Don't validate required fields for preview
        data = {
            "name": name or "Your Name",
            "title": title or "Your Title",
            "summary": summary or "Your professional summary will appear here...",
            "skills": [s.strip() for s in skills.split(",") if s.strip()] if skills else [],
            "experiences": [],
            "education": [],
            "contact": {
                "email": email,
                "phone": phone,
                "linkedin": linkedin,
                "github": github,
                "website": website
            },
            "image_data": process_image(profile_image) if profile_image else None
        }
        
        # Process experiences
        for i in range(len(job_title)):
            if job_title[i].strip():
                data["experiences"].append({
                    "title": job_title[i],
                    "company": company[i] if i < len(company) else "",
                    "duration": duration[i] if i < len(duration) else "",
                    "description": job_description[i] if i < len(job_description) else ""
                })
        
        # Process education
        for i in range(len(edu_degree)):
            if edu_degree[i].strip():
                data["education"].append({
                    "degree": edu_degree[i],
                    "institution": edu_institution[i] if i < len(edu_institution) else "",
                    "year": edu_year[i] if i < len(edu_year) else ""
                })
        
        return templates.TemplateResponse(template, {
            "request": request,
            **data
        })
    
    except Exception:
        # Return empty preview on error
        return HTMLResponse("<div style='color:white;opacity:0.6;'>Preview loading...</div>")


@app.post("/enhance-summary")
async def enhance_summary(summary: str = Form(...)):
    """AI-powered summary enhancement using Ollama"""
    
    if not summary.strip():
        return JSONResponse({"error": "Summary cannot be empty"}, status_code=400)
    
    prompt = f"""Rewrite this professional summary to be polished, executive-level, clear, confident and concise. 
Keep it under 100 words. Make it impactful:

{summary}

Enhanced summary:"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            enhanced = response.json().get("response", summary)
            return JSONResponse({"enhanced": enhanced})
        else:
            return JSONResponse({"enhanced": summary, "error": "AI service unavailable"})
    
    except Exception as e:
        return JSONResponse({"enhanced": summary, "error": str(e)})


@app.post("/download")
async def download_portfolio(
    request: Request,
    template: str = Form("executive_dark.html"),
    name: str = Form(...),
    title: str = Form(...),
    summary: str = Form(...),
    skills: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    linkedin: str = Form(""),
    github: str = Form(""),
    website: str = Form(""),
    job_title: List[str] = Form([]),
    company: List[str] = Form([]),
    duration: List[str] = Form([]),
    job_description: List[str] = Form([]),
    edu_degree: List[str] = Form([]),
    edu_institution: List[str] = Form([]),
    edu_year: List[str] = Form([]),
    profile_image: UploadFile = File(None)
):
    """Download portfolio as standalone HTML file"""
    try:
        data = process_form_data(
            name, title, summary, skills, email, phone, linkedin, github, website,
            job_title, company, duration, job_description,
            edu_degree, edu_institution, edu_year,
            profile_image
        )
        
        # Render template
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader("app/templates"))
        template_file = env.get_template(template)
        
        html_content = template_file.render(
            request=request,
            **data
        )
        
        # Sanitize filename
        filename = re.sub(r'[^a-zA-Z0-9_-]', '_', name.lower().replace(' ', '_'))
        filename = f"{filename}_portfolio.html"
        
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)