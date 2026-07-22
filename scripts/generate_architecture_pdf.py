#!/usr/bin/env python3
"""
Generate System Architecture Diagram PDF
Creates a high-resolution PDF report containing the overall System Architecture Diagram.
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


def draw_architecture_diagram_image() -> Image.Image:
    """Renders high-resolution graphic architecture diagram image (1600x1100)."""
    w, h = 1600, 1100
    img = Image.new("RGB", (w, h), (15, 23, 42))  # Dark slate theme
    draw = ImageDraw.Draw(img, "RGBA")

    # Title Header Banner
    draw.rectangle([0, 0, w, 80], fill=(30, 41, 59, 255))
    draw.text((30, 22), "INDUSTRIAL SAFETY INTELLIGENCE PLATFORM", fill=(248, 250, 252))
    draw.text((820, 26), "OVERALL SYSTEM ARCHITECTURE DIAGRAM", fill=(56, 189, 248))

    # Layer Containers
    layers = [
        ("1. FRONTEND WEB OS (CLIENT LAYER)", 110, (30, 58, 138, 180), (147, 197, 253)),
        ("2. FASTAPI CORE BACKEND ENGINE (API LAYER)", 330, (15, 118, 110, 180), (153, 246, 228)),
        ("3. AI & ANALYTICS CORE ENGINES", 550, (120, 53, 15, 180), (253, 230, 138)),
        ("4. DATA & MEDIA STORAGE LAYER", 770, (67, 56, 202, 180), (199, 210, 254)),
    ]

    for title, y, fill_color, border_color in layers:
        # Layer Container Box
        draw.rectangle([40, y, w - 40, y + 170], fill=fill_color, outline=border_color, width=2)
        draw.rectangle([40, y, 480, y + 34], fill=border_color)
        draw.text((50, y + 8), title, fill=(15, 23, 42))

    # Nodes inside Layer 1: Frontend
    l1_nodes = [
        ("Vanilla JS / HTML5 UI", 60, 160),
        ("CCTV Surveillance Wall\n(4 Live MP4 Feeds)", 420, 160),
        ("CCTV Incident Studio\n(Frame Upload & BBoxes)", 780, 160),
        ("RBAC Admin Matrix\n& Audit Log UI", 1140, 160),
    ]
    for text, nx, ny in l1_nodes:
        draw.rectangle([nx, ny, nx + 320, ny + 90], fill=(255, 255, 255, 240), outline=(56, 189, 248), width=2)
        draw.text((nx + 15, ny + 22), text, fill=(15, 23, 42))

    # Nodes inside Layer 2: API
    l2_nodes = [
        ("Auth & Security Router\n(PBKDF2 + Bearer Tokens)", 60, 380),
        ("CCTV Vision Router\n(/api/computer-vision/*)", 420, 380),
        ("RAG Compliance Router\n(/api/compliance)", 780, 380),
        ("Knowledge Graph Router\n(/api/knowledge-graph)", 1140, 380),
    ]
    for text, nx, ny in l2_nodes:
        draw.rectangle([nx, ny, nx + 320, ny + 90], fill=(241, 245, 249, 240), outline=(45, 212, 191), width=2)
        draw.text((nx + 15, ny + 22), text, fill=(15, 23, 42))

    # Nodes inside Layer 3: AI Engines
    l3_nodes = [
        ("CV Detection Engine\n(cv_engine.py)", 60, 600),
        ("YOLOv8 Pretrained Models\n(yolov8n.pt / yolov8s.pt)", 420, 600),
        ("RAG Citation Search\n(TF-IDF Vector Index)", 780, 600),
        ("Knowledge Graph Builder\n(1072 Nodes / 1492 Edges)", 1140, 600),
    ]
    for text, nx, ny in l3_nodes:
        draw.rectangle([nx, ny, nx + 320, ny + 90], fill=(254, 243, 199, 240), outline=(251, 191, 36), width=2)
        draw.text((nx + 15, ny + 22), text, fill=(15, 23, 42))

    # Nodes inside Layer 4: Storage
    l4_nodes = [
        ("SQLite3 Database\n(safety_platform.db WAL)", 60, 820),
        ("CCTV Stream Videos\n(frontend/media/ 4 MP4s)", 420, 820),
        ("RAG Index JSON\n(rag/index.json)", 780, 820),
        ("Knowledge Graph JSON\n(knowledge_graph/graph.json)", 1140, 820),
    ]
    for text, nx, ny in l4_nodes:
        draw.rectangle([nx, ny, nx + 320, ny + 90], fill=(238, 242, 255, 240), outline=(129, 140, 248), width=2)
        draw.text((nx + 15, ny + 22), text, fill=(15, 23, 42))

    # Inter-layer Connection Arrows (Vertical Lines & Flow Arrows)
    arrow_color = (56, 189, 248, 220)
    for col_x in [220, 580, 940, 1300]:
        # L1 -> L2
        draw.line([(col_x, 250), (col_x, 380)], fill=arrow_color, width=4)
        draw.polygon([(col_x - 6, 374), (col_x + 6, 374), (col_x, 382)], fill=arrow_color)

        # L2 -> L3
        draw.line([(col_x, 470), (col_x, 600)], fill=arrow_color, width=4)
        draw.polygon([(col_x - 6, 594), (col_x + 6, 594), (col_x, 602)], fill=arrow_color)

        # L3 -> L4
        draw.line([(col_x, 690), (col_x, 820)], fill=arrow_color, width=4)
        draw.polygon([(col_x - 6, 814), (col_x + 6, 814), (col_x, 822)], fill=arrow_color)

    # Footer Metadata
    draw.rectangle([0, h - 60, w, h], fill=(30, 41, 59))
    draw.text((40, h - 40), "Industrial Safety AI Platform Architecture | Grounded RAG + YOLOv8 Vision Guardrail", fill=(148, 163, 184))
    draw.text((w - 320, h - 40), "Version 2.0.0 | Enterprise Edition", fill=(56, 189, 248))

    return img


def build_pdf_document() -> None:
    """Generates landscape PDF report containing the diagram and system specs."""
    print("[PDF Generator] Rendering architecture diagram image...")
    diagram_img = draw_architecture_diagram_image()

    buf = io.BytesIO()
    diagram_img.save(buf, format="PNG")
    buf.seek(0)

    # Setup Landscape PDF Page
    pdf_path = PDF_OUTPUT_PATH
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=landscape(letter),
        leftMargin=0.4 * inch,
        rightMargin=0.4 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "PDFTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6
    )
    sub_style = ParagraphStyle(
        "PDFSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10
    )

    story = []
    story.append(Paragraph("Industrial Safety Intelligence Platform", title_style))
    story.append(Paragraph("Overall Multi-Layer System Architecture Diagram", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

    # Add Diagram Graphic Image (Fit to Page: 10.2 x 5.8 inches)
    rl_img = RLImage(buf, width=10.2 * inch, height=5.5 * inch)
    story.append(rl_img)
    story.append(Spacer(1, 10))

    # Summary Architecture Specs Table
    data = [
        ["Layer Component", "Technology Stack", "Primary Function / Capability"],
        ["Client Interface", "Vanilla HTML5 / CSS3 / ES6 JS", "4-Channel CCTV Continuous Live Feed Wall & Incident Studio"],
        ["API Backend", "FastAPI + Uvicorn (Python 3.13)", "Async REST APIs, Authentication, RBAC Matrix, Audit Logging"],
        ["AI & CV Engine", "YOLOv8 (yolov8n.pt / yolov8s.pt) + PyTorch", "PPE Violation, Fallen Worker (Man Down), Vehicle Proximity, Fire/Smoke"],
        ["RAG & Knowledge Graph", "Vector Index + NetworkX Graph", "Grounded OSHA/NIST Regulatory Citations & 1072-Node Risk Graph"],
        ["Data & Storage", "SQLite3 (WAL Mode) + Media Store", "Relational Database, Models Registry, CCTV Streams, Snapshots"],
    ]

    t = Table(data, colWidths=[2.0 * inch, 2.8 * inch, 5.4 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t)

    doc.build(story)
    print(f"[PDF Generator] Architecture PDF generated: {pdf_path} ({pdf_path.stat().st_size / 1024:.1f} KB)")

    # Copy to documentation folder
    DOCS_PDF_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_PDF_OUTPUT_PATH.write_bytes(pdf_path.read_bytes())
    print(f"[PDF Generator] Copied to documentation folder: {DOCS_PDF_OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf_document()
