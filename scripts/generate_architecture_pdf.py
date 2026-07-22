#!/usr/bin/env python3
"""
Generate High-Contrast Black & White Architecture Diagram PDF
Creates a clean, monochrome (B&W), publication-ready PDF diagram of the System Architecture.
"""

from __future__ import annotations

import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, HRFlowable

ROOT = Path(__file__).resolve().parents[1]
PDF_OUTPUT_PATH = ROOT / "architecture_diagram.pdf"
DOCS_PDF_OUTPUT_PATH = ROOT / "documentation" / "architecture_diagram.pdf"


def draw_bw_architecture_diagram_image() -> Image.Image:
    """Renders crisp, high-contrast 100% Black & White architecture diagram graphic (1800x1200)."""
    w, h = 1800, 1200
    img = Image.new("RGB", (w, h), (255, 255, 255))  # Pure white background
    draw = ImageDraw.Draw(img, "RGBA")

    # Outer Document Border
    draw.rectangle([10, 10, w - 10, h - 10], outline=(0, 0, 0), width=3)

    # Title Header Banner (Monochrome High Contrast)
    draw.rectangle([20, 20, w - 20, 100], fill=(255, 255, 255), outline=(0, 0, 0), width=3)
    draw.text((40, 36), "INDUSTRIAL SAFETY INTELLIGENCE PLATFORM", fill=(0, 0, 0))
    draw.text((40, 68), "SYSTEM ARCHITECTURE DIAGRAM — MONOCHROME COMPONENT SPECIFICATION", fill=(0, 0, 0))
    draw.text((w - 380, 52), "[ BLACK & WHITE EDITION ]", fill=(0, 0, 0))

    # 4 Layer Containers (B&W Boxes with Double Borders)
    layers = [
        ("LAYER 1: FRONTEND WEB OPERATING SYSTEM (CLIENT LAYER)", 130),
        ("LAYER 2: FASTAPI CORE BACKEND ENGINE (API & CONTROL LAYER)", 390),
        ("LAYER 3: AI & ANALYTICS ENGINES (VISION, RAG, GRAPH, ML)", 650),
        ("LAYER 4: DATA & MEDIA STORAGE LAYER (SQLITE, MODELS, STREAMS)", 910),
    ]

    for title, y in layers:
        # Outer Layer Box
        draw.rectangle([30, y, w - 30, y + 230], fill=(255, 255, 255), outline=(0, 0, 0), width=3)
        # Header Badge Inside Layer
        draw.rectangle([30, y, 780, y + 38], fill=(0, 0, 0))
        draw.text((45, y + 10), title, fill=(255, 255, 255))

    # Nodes inside Layer 1: Frontend
    l1_nodes = [
        ("Vanilla JS / HTML5 UI\nEnterprise Single-Page OS", 60, 185),
        ("CCTV Surveillance Wall\n4 Continuous Video Streams", 490, 185),
        ("CCTV Incident Studio\nFrame Upload & Detection", 920, 185),
        ("RBAC Admin Matrix\nUser Management & Audit Logs", 1350, 185),
    ]
    for text, nx, ny in l1_nodes:
        draw.rectangle([nx, ny, nx + 390, ny + 155], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        draw.text((nx + 20, ny + 35), text, fill=(0, 0, 0))

    # Nodes inside Layer 2: API Engine
    l2_nodes = [
        ("Auth & Security Module\nPBKDF2 + Bearer Tokens", 60, 445),
        ("CCTV Vision Router\n/api/computer-vision/*", 490, 445),
        ("RAG Compliance Router\n/api/compliance", 920, 445),
        ("Knowledge Graph Router\n/api/knowledge-graph", 1350, 445),
    ]
    for text, nx, ny in l2_nodes:
        draw.rectangle([nx, ny, nx + 390, ny + 155], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        draw.text((nx + 20, ny + 35), text, fill=(0, 0, 0))

    # Nodes inside Layer 3: AI Core
    l3_nodes = [
        ("CV Detection Engine\ncv_engine.py Analytics", 60, 705),
        ("YOLOv8 Pretrained Models\nyolov8n.pt / yolov8s.pt", 490, 705),
        ("RAG Citation Search\nTF-IDF Vector Index", 920, 705),
        ("Knowledge Graph Engine\n1072 Nodes / 1492 Edges", 1350, 705),
    ]
    for text, nx, ny in l3_nodes:
        draw.rectangle([nx, ny, nx + 390, ny + 155], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        draw.text((nx + 20, ny + 35), text, fill=(0, 0, 0))

    # Nodes inside Layer 4: Storage
    l4_nodes = [
        ("SQLite3 Database\nsafety_platform.db (WAL)", 60, 965),
        ("CCTV MP4 Streams\nfrontend/media/ Video Files", 490, 965),
        ("RAG Index JSON\nrag/index.json Storage", 920, 965),
        ("Knowledge Graph Store\nknowledge_graph/graph.json", 1350, 965),
    ]
    for text, nx, ny in l4_nodes:
        draw.rectangle([nx, ny, nx + 390, ny + 155], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        draw.text((nx + 20, ny + 35), text, fill=(0, 0, 0))

    # Vertical Solid Black Connecting Arrows
    for col_x in [255, 685, 1115, 1545]:
        # L1 -> L2
        draw.line([(col_x, 340), (col_x, 445)], fill=(0, 0, 0), width=3)
        draw.polygon([(col_x - 8, 437), (col_x + 8, 437), (col_x, 447)], fill=(0, 0, 0))

        # L2 -> L3
        draw.line([(col_x, 600), (col_x, 705)], fill=(0, 0, 0), width=3)
        draw.polygon([(col_x - 8, 697), (col_x + 8, 697), (col_x, 707)], fill=(0, 0, 0))

        # L3 -> L4
        draw.line([(col_x, 860), (col_x, 965)], fill=(0, 0, 0), width=3)
        draw.polygon([(col_x - 8, 957), (col_x + 8, 957), (col_x, 967)], fill=(0, 0, 0))

    # Footer Metadata
    draw.rectangle([20, h - 45, w - 20, h - 15], fill=(0, 0, 0))
    draw.text((30, h - 35), "Industrial Safety AI Platform Architecture | Black & White Specification Document", fill=(255, 255, 255))
    draw.text((w - 280, h - 35), "Monochrome Format | Ver 2.0", fill=(255, 255, 255))

    return img


def build_bw_pdf_document() -> None:
    """Generates landscape PDF report in crisp 100% Black & White."""
    print("[PDF Generator] Rendering B&W architecture diagram image...")
    diagram_img = draw_bw_architecture_diagram_image()

    buf = io.BytesIO()
    diagram_img.save(buf, format="PNG")
    buf.seek(0)

    # Setup Landscape PDF Document
    pdf_path = PDF_OUTPUT_PATH
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=landscape(letter),
        leftMargin=0.3 * inch,
        rightMargin=0.3 * inch,
        topMargin=0.3 * inch,
        bottomMargin=0.3 * inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "PDFTitleBW",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.black,
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        "PDFSubBW",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.black,
        spaceAfter=8
    )

    story = []
    story.append(Paragraph("Industrial Safety Intelligence Platform — System Architecture", title_style))
    story.append(Paragraph("Monochrome Specification & Multi-Layer System Diagram (Black & White Edition)", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=8))

    # Diagram Image (Fit to Page: 10.4 x 5.7 inches)
    rl_img = RLImage(buf, width=10.4 * inch, height=5.6 * inch)
    story.append(rl_img)
    story.append(Spacer(1, 8))

    # B&W Summary Table
    data = [
        ["Layer Component", "Technology Stack", "Architecture Description / Specification"],
        ["Client Interface", "Vanilla HTML5 / CSS3 / ES6 JS", "4-Channel CCTV Continuous Live Feed Wall & Incident Studio"],
        ["API Backend Engine", "FastAPI + Uvicorn (Python 3.13)", "Async REST APIs, Authentication, RBAC Matrix, Audit Logging"],
        ["AI & CV Core", "YOLOv8 (yolov8n.pt / yolov8s.pt) + PyTorch", "PPE Violation, Fallen Worker (Man Down), Vehicle Proximity, Fire/Smoke"],
        ["RAG & Knowledge Graph", "Vector Index + NetworkX Graph", "Grounded OSHA/NIST Regulatory Citations & 1072-Node Risk Graph"],
        ["Data & Storage", "SQLite3 (WAL Mode) + Media Store", "Relational Database, Models Registry, CCTV Streams, Snapshots"],
    ]

    t = Table(data, colWidths=[2.0 * inch, 2.8 * inch, 5.6 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 1.0, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t)

    doc.build(story)
    print(f"[PDF Generator] Black & White Architecture PDF generated: {pdf_path} ({pdf_path.stat().st_size / 1024:.1f} KB)")

    # Copy to documentation folder
    DOCS_PDF_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_PDF_OUTPUT_PATH.write_bytes(pdf_path.read_bytes())
    print(f"[PDF Generator] Copied to documentation folder: {DOCS_PDF_OUTPUT_PATH}")


if __name__ == "__main__":
    build_bw_pdf_document()
