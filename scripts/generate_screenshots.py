#!/usr/bin/env python3
"""
Generate UI Screenshots for Repository
Creates high-resolution visual previews of the 6 core UI modules in screenshots/ folder.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS_DIR = ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def create_ui_header(draw, title: str, active_tab: str, width: int = 1200):
    # Top Navbar
    draw.rectangle([0, 0, width, 60], fill=(15, 23, 42)) # Slate 900
    draw.text((20, 18), "🛡️ INDUSTRIAL SAFETY INTELLIGENCE OS", fill=(56, 189, 248)) # Sky 400
    
    # Subheader / Tabs
    draw.rectangle([0, 60, width, 100], fill=(30, 41, 59)) # Slate 800
    tabs = ["Surveillance Wall", "CV Incident Studio", "Predictive Maintenance", "RAG Compliance", "Knowledge Graph", "RBAC Matrix"]
    tx = 20
    for tab in tabs:
        is_active = (tab.lower() in active_tab.lower())
        bg = (56, 189, 248) if is_active else (51, 65, 85)
        fg = (15, 23, 42) if is_active else (226, 232, 240)
        tw = len(tab) * 9 + 20
        draw.rectangle([tx, 68, tx + tw, 92], fill=bg)
        draw.text((tx + 10, 72), tab, fill=fg)
        tx += tw + 12
        
    # Title Banner
    draw.rectangle([0, 100, width, 140], fill=(2, 6, 23))
    draw.text((20, 112), f"SECTION: {title.upper()}", fill=(248, 250, 252))
    draw.text((width - 240, 112), "● LIVE SYSTEM ACTIVE", fill=(34, 197, 94))

def generate_surveillance_wall_screenshot():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    create_ui_header(draw, "4-Channel Continuous CCTV Live Surveillance Wall", "Surveillance Wall")
    
    # 4 Video Grid Cards
    cards = [
        ("📹 Camera #1 - Solvent Tank Farm", 30, 160, "● LIVE", (16, 185, 129)),
        ("📹 Camera #2 - Reactor Hall Train A", 610, 160, "● LIVE", (16, 185, 129)),
        ("📹 Camera #3 - Logistics Receiving Bay", 30, 470, "● LIVE", (16, 185, 129)),
        ("📹 Camera #4 - Utilities & Boiler Island", 610, 470, "● LIVE", (16, 185, 129)),
    ]
    
    for title, x, y, status, st_color in cards:
        draw.rectangle([x, y, x + 560, y + 290], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
        draw.rectangle([x, y, x + 560, y + 36], fill=(51, 65, 85))
        draw.text((x + 12, y + 10), title, fill=(248, 250, 252))
        draw.text((x + 480, y + 10), status, fill=st_color)
        
        # Screen Video Area Mock
        draw.rectangle([x + 10, y + 46, x + 550, y + 280], fill=(2, 6, 23), outline=(71, 85, 105))
        draw.text((x + 180, y + 150), "[ CCTV MP4 Stream Auto-Looping ]", fill=(148, 163, 184))
        
    img.save(SCREENSHOTS_DIR / "01_cctv_live_surveillance_wall.png")

def generate_cv_studio_screenshot():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    create_ui_header(draw, "Computer Vision Incident Analysis Studio", "CV Incident Studio")
    
    # Left Panel: Upload & Controls
    draw.rectangle([30, 160, 420, 760], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    draw.text((45, 180), "📷 Frame Snapshot Upload", fill=(248, 250, 252))
    draw.rectangle([45, 210, 405, 320], fill=(15, 23, 42), outline=(56, 189, 248), width=1)
    draw.text((80, 250), "Drag & Drop CCTV Image Frame", fill=(148, 163, 184))
    
    draw.text((45, 340), "Select Detection Task:", fill=(248, 250, 252))
    tasks = ["1. Workers & PPE Compliance", "2. Man-Down Posture Fall Detection", "3. Vehicle-Pedestrian Hazard", "4. Fire & Smoke Optical Detection"]
    ty = 370
    for task in tasks:
        draw.rectangle([45, ty, 405, ty + 30], fill=(51, 65, 85))
        draw.text((55, ty + 7), task, fill=(226, 232, 240))
        ty += 40
        
    # Right Panel: Image Display & Bounding Boxes
    draw.rectangle([440, 160, 1170, 760], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    draw.text((460, 180), "🔍 Real-Time YOLOv8 Annotated Bounding Box Inspection", fill=(248, 250, 252))
    
    draw.rectangle([460, 210, 1150, 580], fill=(2, 6, 23), outline=(56, 189, 248), width=2)
    # Mock Bounding Boxes
    draw.rectangle([520, 260, 680, 500], outline=(239, 68, 68), width=3) # Red box - NO HARDHAT
    draw.rectangle([520, 240, 680, 260], fill=(239, 68, 68))
    draw.text((525, 243), "NO_HARDHAT (89%)", fill=(255, 255, 255))
    
    draw.rectangle([760, 280, 940, 520], outline=(34, 197, 94), width=3) # Green box - PPE OK
    draw.rectangle([760, 260, 940, 280], fill=(34, 197, 94))
    draw.text((765, 263), "WORKER_PPE_OK (94%)", fill=(15, 23, 42))
    
    # Bottom Audit Metrics
    draw.rectangle([460, 600, 1150, 740], fill=(15, 23, 42), outline=(71, 85, 105))
    draw.text((480, 620), "STATUS: HIGH RISK PPE VIOLATION DETECTED", fill=(239, 68, 68))
    draw.text((480, 650), "• Risk Score: 78.4/100 | Severity: HIGH | Recommendation: Dispatch EHS Inspector", fill=(226, 232, 240))
    draw.text((480, 680), "• Model: YOLOv8 Pretrained (yolov8s.pt) | Inference Time: 42.1ms", fill=(148, 163, 184))
    
    img.save(SCREENSHOTS_DIR / "02_computer_vision_incident_studio.png")

def generate_predictive_maint_screenshot():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    create_ui_header(draw, "Predictive Maintenance & Equipment RUL Analytics", "Predictive Maintenance")
    
    # 3 Stat Cards
    draw.rectangle([30, 160, 390, 260], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    draw.text((45, 175), "AVERAGE EQUIPMENT HEALTH", fill=(148, 163, 184))
    draw.text((45, 205), "84.2%", fill=(34, 197, 94))
    
    draw.rectangle([415, 160, 785, 260], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    draw.text((430, 175), "HIGH RISK ANOMALIES", fill=(148, 163, 184))
    draw.text((430, 205), "3 Assets Alerting", fill=(239, 68, 68))
    
    draw.rectangle([810, 160, 1170, 260], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    draw.text((825, 175), "RUL PREDICTION MODEL", fill=(148, 163, 184))
    draw.text((825, 205), "NASA C-MAPSS v1", fill=(56, 189, 248))
    
    # Equipment Table Mock
    draw.rectangle([30, 280, 1170, 760], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    draw.text((50, 300), "⚙️ Plant Machinery Remaining Useful Life (RUL) & Failure Risk Table", fill=(248, 250, 252))
    
    headers = ["Asset Name", "Plant Zone", "Health Score", "Estimated RUL", "Priority", "Action"]
    hx = [50, 300, 520, 680, 840, 1000]
    draw.rectangle([30, 330, 1170, 365], fill=(51, 65, 85))
    for i, h_text in enumerate(headers):
        draw.text((hx[i], 340), h_text, fill=(248, 250, 252))
        
    rows = [
        ("Reactor Feed Pump 01", "zone_reactor", "48.2%", "14 Cycles", "HIGH RISK", (239, 68, 68)),
        ("Solvent Transfer Skid 02", "zone_tank_farm", "62.1%", "42 Cycles", "MEDIUM", (245, 158, 11)),
        ("Main Agitator Drive 01", "zone_process", "91.8%", "180 Cycles", "NORMAL", (34, 197, 94)),
        ("Boiler Feed Compressor", "zone_utilities", "88.4%", "154 Cycles", "NORMAL", (34, 197, 94)),
    ]
    ry = 380
    for r_name, r_zone, r_health, r_rul, r_prio, r_color in rows:
        draw.rectangle([30, ry, 1170, ry + 45], fill=(15, 23, 42) if (ry//45)%2==0 else (30, 41, 59))
        draw.text((hx[0], ry + 12), r_name, fill=(248, 250, 252))
        draw.text((hx[1], ry + 12), r_zone, fill=(148, 163, 184))
        draw.text((hx[2], ry + 12), r_health, fill=(226, 232, 240))
        draw.text((hx[3], ry + 12), r_rul, fill=(226, 232, 240))
        draw.text((hx[4], ry + 12), r_prio, fill=r_color)
        draw.rectangle([hx[5], ry + 8, hx[5] + 120, ry + 36], fill=(56, 189, 248))
        draw.text((hx[5] + 15, ry + 14), "Schedule Work Order", fill=(15, 23, 42))
        ry += 55
        
    img.save(SCREENSHOTS_DIR / "03_predictive_maintenance_analytics.png")

def generate_rag_screenshot():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    create_ui_header(draw, "Regulatory Safety RAG Search Engine", "RAG Compliance")
    
    # Search Bar
    draw.rectangle([30, 160, 1170, 230], fill=(30, 41, 59), outline=(56, 189, 248), width=2)
    draw.text((50, 185), "🔍 Search OSHA Regulations & NIST ICS Security Guidelines:", fill=(148, 163, 184))
    draw.text((505, 185), "Lockout Tagout requirements for solvent pump maintenance", fill=(248, 250, 252))
    
    # Results Container
    draw.rectangle([30, 250, 1170, 760], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    draw.text((50, 270), "📚 Grounded Regulatory Search Results & Verified Citations", fill=(248, 250, 252))
    
    # Citation Box 1
    draw.rectangle([50, 310, 1150, 500], fill=(15, 23, 42), outline=(56, 189, 248), width=1)
    draw.text((70, 330), "OSHA Standard 1910.147 - Control of Hazardous Energy (Lockout/Tagout)", fill=(56, 189, 248))
    draw.text((70, 360), "Score: 96.4% Relevance | Source: osha_1910_147.html", fill=(34, 197, 94))
    draw.text((70, 390), "• Requirement: Specific energy control procedures must be documented and utilized for hazardous energy isolation.", fill=(226, 232, 240))
    draw.text((70, 415), "• Key Directive: Lockout devices must hold energy isolating devices in a neutral or 'safe' position during service.", fill=(226, 232, 240))
    draw.text((70, 440), "• Action Checklist: De-energize pump motor, relieve hydraulic pressure, and apply standardized padlock.", fill=(148, 163, 184))
    
    # Citation Box 2
    draw.rectangle([50, 520, 1150, 710], fill=(15, 23, 42), outline=(51, 65, 85), width=1)
    draw.text((70, 540), "NIST SP 800-82r3 - Guide to Industrial Control Systems (ICS) Security", fill=(56, 189, 248))
    draw.text((70, 570), "Score: 88.1% Relevance | Source: NIST_SP_800_82r3_ICS_Security.pdf", fill=(34, 197, 94))
    draw.text((70, 600), "• Guideline: Ensure emergency shutdown interlocks remain operational independently of primary PLC network.", fill=(226, 232, 240))
    
    img.save(SCREENSHOTS_DIR / "04_rag_regulatory_compliance.png")

def generate_kg_screenshot():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    create_ui_header(draw, "Plant Equipment & Hazard Knowledge Graph Network", "Knowledge Graph")
    
    # Main Graph Canvas
    draw.rectangle([30, 160, 1170, 760], fill=(2, 6, 23), outline=(51, 65, 85), width=2)
    draw.text((50, 180), "🕸️ Knowledge Graph Network (1,072 Nodes | 1,492 Relationship Edges)", fill=(248, 250, 252))
    
    # Draw Nodes and Lines
    center = (600, 450)
    nodes = [
        ("Solvent Tank Farm", 350, 300, (56, 189, 248)),
        ("Reactor Feed Pump", 850, 300, (245, 158, 11)),
        ("Chemical Spill Risk", 350, 600, (239, 68, 68)),
        ("OSHA 1910.119 PSM", 850, 600, (34, 197, 94)),
        ("PPE Hardhat Required", 600, 250, (168, 85, 247)),
    ]
    
    for _, nx, ny, _ in nodes:
        draw.line([center, (nx, ny)], fill=(71, 85, 105), width=2)
        
    draw.ellipse([center[0]-45, center[1]-45, center[0]+45, center[1]+45], fill=(56, 189, 248), outline=(255, 255, 255), width=2)
    draw.text((center[0]-35, center[1]-8), "Apex Plant 01", fill=(15, 23, 42))
    
    for ntext, nx, ny, ncolor in nodes:
        draw.ellipse([nx-40, ny-40, nx+40, ny+40], fill=ncolor, outline=(255, 255, 255), width=2)
        draw.text((nx-35, ny-8), ntext.split()[0], fill=(255, 255, 255))
        draw.text((nx-35, ny+45), ntext, fill=(226, 232, 240))
        
    img.save(SCREENSHOTS_DIR / "05_equipment_hazard_knowledge_graph.png")

def generate_rbac_screenshot():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    create_ui_header(draw, "Role-Based Access Control (RBAC) & Security Audit Matrix", "RBAC Matrix")
    
    # Table Box
    draw.rectangle([30, 160, 1170, 760], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    draw.text((50, 180), "🔐 Role Permissions & Access Authorization Control Matrix", fill=(248, 250, 252))
    
    roles = ["Administrator", "EHS Manager", "Operations Supervisor", "Maintenance Lead", "Process Operator", "Field Worker"]
    features = ["CCTV Live Streams", "CV Incident Studio", "Predictive Analytics", "RAG Compliance Search", "System Audit Logs", "User Administration"]
    
    # Table Header
    draw.rectangle([50, 220, 1150, 260], fill=(51, 65, 85))
    draw.text((70, 232), "Role / Module", fill=(248, 250, 252))
    cx = 280
    for feat in features:
        draw.text((cx, 232), feat[:12], fill=(248, 250, 252))
        cx += 145
        
    ry = 270
    for r_idx, role in enumerate(roles):
        draw.rectangle([50, ry, 1150, ry + 40], fill=(15, 23, 42) if r_idx%2==0 else (30, 41, 59))
        draw.text((70, ry + 12), role, fill=(56, 189, 248) if r_idx==0 else (226, 232, 240))
        cx = 280
        for f_idx in range(len(features)):
            has_access = (r_idx == 0) or (r_idx == 1 and f_idx < 5) or (r_idx == 2 and f_idx in [0,1,2,3]) or (r_idx == 3 and f_idx in [0,2,3]) or (f_idx == 0)
            badge_text = "✔ ALLOW" if has_access else "✖ DENY"
            badge_color = (34, 197, 94) if has_access else (239, 68, 68)
            draw.text((cx + 10, ry + 12), badge_text, fill=badge_color)
            cx += 145
        ry += 48
        
    img.save(SCREENSHOTS_DIR / "06_rbac_security_matrix.png")

def main():
    print("[Screenshot Generator] Rendering UI preview screenshots...")
    generate_surveillance_wall_screenshot()
    generate_cv_studio_screenshot()
    generate_predictive_maint_screenshot()
    generate_rag_screenshot()
    generate_kg_screenshot()
    generate_rbac_screenshot()
    print(f"[Screenshot Generator] 6 UI screenshots created in {SCREENSHOTS_DIR}")

if __name__ == "__main__":
    main()
