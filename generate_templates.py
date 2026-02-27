import os
import re

TEMPLATE_DIR = "app/templates"
IMAGE_DIR = "static/images/templates"

# 15 Templates inspired by top companies/fields
# Structure: { id, name, category, desc, colors: { bg, text, primary, secondary, accent }, font }
TEMPLATES = [
    {
        "id": "theme_google", "name": "Google Minimal", "category": "Big Tech",
        "desc": "Clean white background with classic primary color accents (Red, Blue, Yellow, Green).",
        "colors": {"bg": "#ffffff", "text": "#202124", "primary": "#4285f4", "secondary": "#34a853", "accent": "#ea4335"},
        "font": "'Roboto', 'Open Sans', sans-serif"
    },
    {
        "id": "theme_apple", "name": "Apple Sleek", "category": "Big Tech",
        "desc": "Ultra-minimalist, lots of whitespace, stark contrasts, and elegant typography.",
        "colors": {"bg": "#f5f5f7", "text": "#1d1d1f", "primary": "#0066cc", "secondary": "#86868b", "accent": "#1d1d1f"},
        "font": "-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif"
    },
    {
        "id": "theme_microsoft", "name": "Microsoft Fluent", "category": "Big Tech",
        "desc": "Blocky, structured, professional design with familiar blue accents.",
        "colors": {"bg": "#f3f2f1", "text": "#323130", "primary": "#0078d4", "secondary": "#605e5c", "accent": "#107c10"},
        "font": "'Segoe UI', 'Helvetica Neue', sans-serif"
    },
    {
        "id": "theme_amazon", "name": "Amazon Retail", "category": "Big Tech",
        "desc": "Dark top bar, orange accents, highly functional and data-dense layout.",
        "colors": {"bg": "#ffffff", "text": "#0f1111", "primary": "#ff9900", "secondary": "#232f3e", "accent": "#007185"},
        "font": "'Amazon Ember', Arial, sans-serif"
    },
    {
        "id": "theme_meta", "name": "Meta Connect", "category": "Big Tech",
        "desc": "Modern blue gradients, rounded corners, and a social-media feed feel.",
        "colors": {"bg": "#ffffff", "text": "#1c1e21", "primary": "#0668E1", "secondary": "#8D949E", "accent": "#E4E6EB"},
        "font": "'Helvetica Neue', Helvetica, Arial, sans-serif"
    },
    {
        "id": "theme_netflix", "name": "Netflix Cinematic", "category": "Entertainment",
        "desc": "Deep black background, striking red accents, large immersive visuals.",
        "colors": {"bg": "#141414", "text": "#ffffff", "primary": "#e50914", "secondary": "#333333", "accent": "#b3b3b3"},
        "font": "'Netflix Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
    },
    {
        "id": "theme_spotify", "name": "Spotify Audio", "category": "Entertainment",
        "desc": "Dark mode with vibrant, punchy green accents and bold typography.",
        "colors": {"bg": "#121212", "text": "#ffffff", "primary": "#1ed760", "secondary": "#b3b3b3", "accent": "#535353"},
        "font": "'Circular', 'Helvetica Neue', Helvetica, Arial, sans-serif"
    },
    {
        "id": "theme_stripe", "name": "Stripe FinTech", "category": "Finance",
        "desc": "Sleek gradients, crisp typography, and high-contrast blurple accents.",
        "colors": {"bg": "#f6f9fc", "text": "#424770", "primary": "#635bff", "secondary": "#0a2540", "accent": "#00d4ff"},
        "font": "'Inter', '-apple-system', sans-serif"
    },
    {
        "id": "theme_bloomberg", "name": "Bloomberg Terminal", "category": "Finance",
        "desc": "Intense dark mode, amber/orange text, data-heavy layout.",
        "colors": {"bg": "#000000", "text": "#ff9900", "primary": "#ff9900", "secondary": "#333333", "accent": "#ffffff"},
        "font": "'Courier New', monospace"
    },
    {
        "id": "theme_airbnb", "name": "Airbnb Travel", "category": "Lifestyle",
        "desc": "Warm, inviting design with soft peach/coral accents and friendly rounded fonts.",
        "colors": {"bg": "#ffffff", "text": "#222222", "primary": "#ff385c", "secondary": "#717171", "accent": "#b0b0b0"},
        "font": "'Circular', -apple-system, BlinkMacSystemFont, Roboto, sans-serif"
    },
    {
        "id": "theme_uber", "name": "Uber Motion", "category": "Lifestyle",
        "desc": "Stark contrast, exclusively black and white, highly utilitarian.",
        "colors": {"bg": "#ffffff", "text": "#000000", "primary": "#000000", "secondary": "#eeeeee", "accent": "#545454"},
        "font": "'Uber Move Text', system-ui, sans-serif"
    },
    {
        "id": "theme_github", "name": "GitHub Dev", "category": "Developer Tools",
        "desc": "Classic developer styling, gray backgrounds, blue links, monospace code blocks.",
        "colors": {"bg": "#0d1117", "text": "#c9d1d9", "primary": "#58a6ff", "secondary": "#30363d", "accent": "#8b949e"},
        "font": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
    },
    {
        "id": "theme_vercel", "name": "Vercel Edge", "category": "Developer Tools",
        "desc": "Ultra modern, stark black/white with subtle gradients and perfect typography.",
        "colors": {"bg": "#000000", "text": "#ededed", "primary": "#ffffff", "secondary": "#111111", "accent": "#333333"},
        "font": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    },
    {
        "id": "theme_discord", "name": "Discord Gaming", "category": "Social",
        "desc": "Dark grayish-blue backgrounds with bright 'blurple' and green accents.",
        "colors": {"bg": "#36393f", "text": "#dcddde", "primary": "#5865F2", "secondary": "#2f3136", "accent": "#3ba55c"},
        "font": "'gg sans', 'Noto Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
    },
    {
        "id": "theme_notion", "name": "Notion Document", "category": "Productivity",
        "desc": "Looks like a beautiful document, minimal CSS, serif typography options.",
        "colors": {"bg": "#ffffff", "text": "#37352f", "primary": "#0f0f0f", "secondary": "#f1f1ef", "accent": "#9b9a97"},
        "font": "ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, sans-serif"
    }
]

BASE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ name }} - {{ title }}</title>
    <!-- Template: {template_name} -->
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@300;400;500;700&display=swap');
        
        :root {{
            --bg: {bg};
            --text: {text};
            --primary: {primary};
            --secondary: {secondary};
            --accent: {accent};
            --font: {font};
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: var(--font); background: var(--bg); color: var(--text); line-height: 1.6; padding: 40px 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        
        header {{ 
            display: flex; gap: 40px; align-items: center; margin-bottom: 60px; 
            padding-bottom: 40px; border-bottom: 2px solid var(--secondary);
        }}
        
        .profile-img {{
            width: 150px; height: 150px; border-radius: 50%; object-fit: cover;
            border: 4px solid var(--bg); box-shadow: 0 0 0 3px var(--primary);
        }}
        
        h1 {{ font-size: 3rem; font-weight: 700; margin-bottom: 8px; color: var(--primary); }}
        h2 {{ font-size: 1.5rem; font-weight: 400; margin-bottom: 16px; opacity: 0.9; }}
        .summary {{ font-size: 1.1rem; max-width: 600px; line-height: 1.8; color: var(--text); opacity: 0.8; }}
        
        .contact-links {{ display: flex; gap: 15px; margin-top: 20px; flex-wrap: wrap; }}
        .contact-links a {{ 
            display: inline-block; padding: 8px 16px; border-radius: 20px;
            background: var(--secondary); color: var(--text); text-decoration: none;
            font-size: 0.9rem; font-weight: 500; transition: 0.2s;
        }}
        .contact-links a:hover {{ background: var(--primary); color: var(--bg); }}

        section {{ margin-bottom: 50px; }}
        h3 {{ font-size: 1.8rem; margin-bottom: 25px; color: var(--primary); border-left: 4px solid var(--accent); padding-left: 15px; }}

        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
        
        .card {{ 
            background: var(--secondary); padding: 25px; border-radius: 12px;
            border: 1px solid var(--accent);
        }}
        
        .card-title {{ font-size: 1.2rem; font-weight: 600; margin-bottom: 5px; color: var(--text); }}
        .card-subtitle {{ color: var(--primary); font-weight: 500; font-size: 1rem; margin-bottom: 10px; }}
        .card-date {{ font-size: 0.85rem; opacity: 0.7; margin-bottom: 15px; display: inline-block; background: var(--bg); padding: 3px 8px; border-radius: 4px; }}
        
        .skills {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .skill-tag {{ 
            background: var(--bg); border: 1px solid var(--accent); color: var(--text);
            padding: 6px 14px; border-radius: 6px; font-size: 0.9rem; font-weight: 500;
        }}

        @media (max-width: 768px) {{
            header {{ flex-direction: column; text-align: center; }}
            .grid-2 {{ grid-template-columns: 1fr; }}
            .contact-links {{ justify-content: center; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            {{% if image_data %}}
            <img src="data:image/jpeg;base64,{{{{ image_data }}}}" alt="{{{{ name }}}}" class="profile-img">
            {{% endif %}}
            <div>
                <h1>{{{{ name }}}}</h1>
                <h2>{{{{ title }}}}</h2>
                <p class="summary">{{{{ summary }}}}</p>
                <div class="contact-links">
                    {{% if contact.email %}}<a href="mailto:{{{{ contact.email }}}}">Email</a>{{% endif %}}
                    {{% if contact.phone %}}<a href="tel:{{{{ contact.phone }}}}">Phone</a>{{% endif %}}
                    {{% if contact.linkedin %}}<a href="{{{{ contact.linkedin }}}}" target="_blank">LinkedIn</a>{{% endif %}}
                    {{% if contact.website %}}<a href="{{{{ contact.website }}}}" target="_blank">Portfolio</a>{{% endif %}}
                    {{% if contact.github %}}<a href="{{{{ contact.github }}}}" target="_blank">GitHub</a>{{% endif %}}
                </div>
            </div>
        </header>

        {{% if skills %}}
        <section>
            <h3>Core Skills</h3>
            <div class="skills">
                {{% for skill in skills %}}
                <span class="skill-tag">{{{{ skill }}}}</span>
                {{% endfor %}}
            </div>
        </section>
        {{% endif %}}

        {{% if experiences %}}
        <section>
            <h3>Experience</h3>
            <div class="grid-2">
                {{% for exp in experiences %}}
                <div class="card">
                    <div class="card-title">{{{{ exp.title }}}}</div>
                    <div class="card-subtitle">{{{{ exp.company }}}}</div>
                    {{% if exp.duration %}}<div class="card-date">{{{{ exp.duration }}}}</div>{{% endif %}}
                    <p>{{{{ exp.description }}}}</p>
                </div>
                {{% endfor %}}
            </div>
        </section>
        {{% endif %}}

        {{% if education %}}
        <section>
            <h3>Education</h3>
            <div class="grid-2">
                {{% for edu in education %}}
                <div class="card">
                    <div class="card-title">{{{{ edu.institution }}}}</div>
                    <div class="card-subtitle">{{{{ edu.degree }}}}</div>
                    {{% if edu.year %}}<div class="card-date">{{{{ edu.year }}}}</div>{{% endif %}}
                </div>
                {{% endfor %}}
            </div>
        </section>
        {{% endif %}}
    </div>
</body>
</html>"""

def generate_template_files():
    for t in TEMPLATES:
        filename = f"{t['id']}.html"
        filepath = os.path.join(TEMPLATE_DIR, filename)
        
        html_content = BASE_HTML.format(
            template_name=t['name'],
            bg=t['colors']['bg'],
            text=t['colors']['text'],
            primary=t['colors']['primary'],
            secondary=t['colors']['secondary'],
            accent=t['colors']['accent'],
            font=t['font']
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Created template: {filename}")

def generate_placeholders():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    # create a simple 1x1 base64 png script to serve as solid color placeholders
    # In real life we'd use PIL but for brevity we'll just leave a text file or 1x1 pngs
    pass # we'll generate actual colored blocks in CSS for cards or small PNGs via bash later

def update_builder_html():
    builder_path = os.path.join(TEMPLATE_DIR, "builder.html")
    with open(builder_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create new optgroups based on generated templates
    groups = {}
    for t in TEMPLATES:
        cat = t['category']
        if cat not in groups:
            groups[cat] = []
        groups[cat].append(t)
        
    new_options = ""
    for cat, items in groups.items():
        new_options += f'                    <optgroup label="{cat}">\n'
        for item in items:
            new_options += f'                        <option value="{item["id"]}.html">🏢 {item["name"]}</option>\n'
        new_options += f'                    </optgroup>\n'

    # Inject into select
    pattern = r'(<select name="template" id="templateSelect">)(.*?)(</select>)'
    
    # We will PREPEND our new optgroups to the existing ones
    def replacer(match):
        return match.group(1) + "\n" + new_options + match.group(2) + match.group(3)
        
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    with open(builder_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Updated builder.html")

def update_home_html():
    home_path = os.path.join(TEMPLATE_DIR, "home.html")
    with open(home_path, 'r', encoding='utf-8') as f:
        content = f.read()

    cards_html = "<!-- Auto-generated templates -->\n"
    for t in TEMPLATES:
        cards_html += f"""
                <div class="template-card">
                    <div class="template-preview" style="background: {t['colors']['bg']}; padding: 0;">
                        <!-- We use CSS blocks to represent the theme colors instead of actual images -->
                        <div style="width: 100%; height: 100%; display: flex; flex-direction: column;">
                            <div style="height: 30%; background: {t['colors']['primary']};"></div>
                            <div style="height: 70%; background: {t['colors']['secondary']}; position: relative;">
                                <div style="position: absolute; top: -20px; left: 20px; width: 40px; height: 40px; border-radius: 50%; background: {t['colors']['accent']};"></div>
                                <div style="margin: 30px 20px 0; height: 10px; width: 60%; background: {t['colors']['text']}; opacity: 0.2; border-radius: 5px;"></div>
                                <div style="margin: 10px 20px 0; height: 8px; width: 40%; background: {t['colors']['text']}; opacity: 0.2; border-radius: 4px;"></div>
                            </div>
                        </div>
                    </div>
                    <div class="template-info">
                        <h3 class="template-name">{t['name']}</h3>
                        <p class="template-desc">{t['desc']}</p>
                    </div>
                </div>
"""

    pattern = r'(<!-- New Templates -->)(.*?)(</div>\s*</div>\s*</section>)'
    
    def replacer(match):
        return match.group(1) + match.group(2) + cards_html + match.group(3)
        
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)

    with open(home_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Updated home.html")

if __name__ == "__main__":
    print("Generating 15 templates...")
    generate_template_files()
    update_builder_html()
    update_home_html()
    print("Done!")
