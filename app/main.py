from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, Response, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import shutil
import os
import base64
import requests
from pathlib import Path
import re
import urllib.parse

from sqlalchemy.orm import Session
from app.database import engine, get_db
import app.models as models
from app.auth import verify_password, get_password_hash, create_access_token, decode_access_token

models.Base.metadata.create_all(bind=engine)

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
# AUTH & USER CONTEXT
# -----------------------------
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    
    username = decode_access_token(token)
    if not username:
        return None
        
    user = db.query(models.User).filter(models.User.username == username).first()
    return user


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/api/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if db.query(models.User).filter(models.User.username == username).first():
        return RedirectResponse(url=f"/register?error={urllib.parse.quote('Username already registered')}", status_code=302)
    if db.query(models.User).filter(models.User.email == email).first():
        return RedirectResponse(url=f"/register?error={urllib.parse.quote('Email already registered')}", status_code=302)
        
    hashed_password = get_password_hash(password)
    db_user = models.User(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return RedirectResponse(url="/login", status_code=302)


@app.post("/api/login")
async def login(
    username: str = Form(...), 
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse(url=f"/login?error={urllib.parse.quote('Incorrect username or password')}", status_code=302)
        
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/builder", status_code=302)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response


# -----------------------------
# ROUTES
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page with explanation and features"""
    user = get_current_user(request, db)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})


@app.get("/builder", response_class=HTMLResponse)
async def builder(request: Request, db: Session = Depends(get_db)):
    """Portfolio builder interface"""
    user = get_current_user(request, db)
    return templates.TemplateResponse("builder.html", {"request": request, "user": user})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """User dashboard to manage saved portfolios"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
        
    portfolios = db.query(models.Portfolio).filter(models.Portfolio.user_id == user.id).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": user, 
        "portfolios": portfolios
    })

@app.get("/view/{portfolio_id}", response_class=HTMLResponse)
async def view_portfolio(request: Request, portfolio_id: int, db: Session = Depends(get_db)):
    """View a saved portfolio"""
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
        
    import json
    data = {
        "name": portfolio.name,
        "title": portfolio.title,
        "summary": portfolio.summary,
        "skills": json.loads(portfolio.skills) if portfolio.skills else [],
        "experiences": json.loads(portfolio.experiences_json),
        "education": json.loads(portfolio.education_json),
        "contact": json.loads(portfolio.contact_json),
        "image_data": portfolio.profile_image_url
    }
    
    return templates.TemplateResponse(portfolio.template_name, {
        "request": request,
        **data
    })
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
    profile_image: UploadFile = File(None),
    action: str = Form("download"),
    db: Session = Depends(get_db)
):
    """Generate portfolio with all form data and either preview, download, or save it"""
    try:
        user = get_current_user(request, db)
        
        data = process_form_data(
            name, title, summary, skills, email, phone, linkedin, github, website,
            job_title, company, duration, job_description,
            edu_degree, edu_institution, edu_year,
            profile_image
        )
        
        if action == "save":
            if not user:
                return RedirectResponse(url=f"/login?error=Please login to save portfolios", status_code=302)
                
            import json
            new_portfolio = models.Portfolio(
                user_id=user.id,
                name=data["name"],
                template_name=template,
                title=data["title"],
                summary=data["summary"],
                skills=json.dumps(data["skills"]),
                experiences_json=json.dumps(data["experiences"]),
                education_json=json.dumps(data["education"]),
                contact_json=json.dumps(data["contact"]),
                profile_image_url=data["image_data"]
            )
            db.add(new_portfolio)
            db.commit()
            return RedirectResponse(url="/dashboard", status_code=302)
            
        elif action == "preview":
            return templates.TemplateResponse(template, {
                "request": request,
                **data
            })
            
        else: # download
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader("app/templates"))
            template_file = env.get_template(template)
            
            html_content = template_file.render(
                request=request,
                **data
            )
            
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

@app.post("/api/portfolios/{portfolio_id}/delete")
async def delete_portfolio(portfolio_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id, models.Portfolio.user_id == user.id).first()
    if portfolio:
        db.delete(portfolio)
        db.commit()
        
    return RedirectResponse(url="/dashboard", status_code=302)


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
    """AI-powered summary enhancement using Groq API"""
    
    if not summary.strip():
        return JSONResponse({"error": "Summary cannot be empty"}, status_code=400)
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        # Fallback to a polite message if no API key is set
        return JSONResponse({
            "enhanced": summary, 
            "error": "AI enhancements are temporarily disabled. Please configure GROQ_API_KEY on the server."
        })

    prompt = f"""Rewrite this professional summary to be polished, executive-level, clear, confident and concise. 
Keep it under 100 words. Make it impactful:

{summary}

Enhanced summary:"""

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json={
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are an expert career coach and resume writer. Return ONLY the enhanced summary, without any conversational filler or introductions."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            enhanced = result["choices"][0]["message"]["content"].strip()
            # Clean up potential quotes returned by the model
            if enhanced.startswith('"') and enhanced.endswith('"'):
                enhanced = enhanced[1:-1]
            return JSONResponse({"enhanced": enhanced})
        else:
            return JSONResponse({
                "enhanced": summary, 
                "error": f"AI service error: {response.text[:100]}"
            })
    
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