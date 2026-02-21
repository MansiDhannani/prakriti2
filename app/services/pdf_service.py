"""
PDF Policy Report Generator using ReportLab
"""
import io
import base64
from datetime import datetime
from typing import Optional, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY


# ── Colour palette ───────────────────────────────────────────────────────────
FOREST_GREEN   = colors.HexColor("#1a5c3a")
MOSS_GREEN     = colors.HexColor("#2d7a4f")
SAGE_GREEN     = colors.HexColor("#5a9e6f")
LEAF_GREEN     = colors.HexColor("#8cc97e")
LIGHT_GREEN    = colors.HexColor("#e8f5e9")
GOLD           = colors.HexColor("#f9a825")
EARTH          = colors.HexColor("#5c3d1e")
TEXT_DARK      = colors.HexColor("#1a2e1a")
TEXT_MID       = colors.HexColor("#3d5c3d")
LIGHT_GREY     = colors.HexColor("#f5f5f5")
WHITE          = colors.white


def _inr_crore(value: float) -> str:
    cr = value / 1e7
    if abs(cr) >= 1:
        return f"₹{cr:,.2f} Cr"
    lakh = value / 1e5
    return f"₹{lakh:,.2f} L"


def _build_styles():
    styles = getSampleStyleSheet()

    custom = {
        "CoverTitle": ParagraphStyle(
            "CoverTitle", parent=styles["Title"],
            fontSize=26, leading=32, textColor=WHITE,
            alignment=TA_LEFT, spaceAfter=6, fontName="Helvetica-Bold"
        ),
        "CoverSub": ParagraphStyle(
            "CoverSub", parent=styles["Normal"],
            fontSize=12, textColor=colors.HexColor("#c8e6c9"),
            alignment=TA_LEFT, spaceAfter=4, fontName="Helvetica"
        ),
        "SectionHead": ParagraphStyle(
            "SectionHead", parent=styles["Heading1"],
            fontSize=13, leading=16, textColor=FOREST_GREEN,
            fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=14,
            borderPad=0
        ),
        "SubHead": ParagraphStyle(
            "SubHead", parent=styles["Heading2"],
            fontSize=10, textColor=MOSS_GREEN,
            fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=8
        ),
        "Body": ParagraphStyle(
            "Body", parent=styles["Normal"],
            fontSize=9.5, leading=14, textColor=TEXT_DARK,
            alignment=TA_JUSTIFY, fontName="Helvetica"
        ),
        "BodySmall": ParagraphStyle(
            "BodySmall", parent=styles["Normal"],
            fontSize=8.5, leading=12, textColor=TEXT_MID,
            fontName="Helvetica"
        ),
        "MetricLabel": ParagraphStyle(
            "MetricLabel", parent=styles["Normal"],
            fontSize=7.5, textColor=MOSS_GREEN,
            fontName="Helvetica-Bold", spaceAfter=1,
            textTransform="uppercase"
        ),
        "MetricValue": ParagraphStyle(
            "MetricValue", parent=styles["Normal"],
            fontSize=16, leading=18, textColor=FOREST_GREEN,
            fontName="Helvetica-Bold"
        ),
        "Tag": ParagraphStyle(
            "Tag", parent=styles["Normal"],
            fontSize=7.5, textColor=SAGE_GREEN,
            fontName="Helvetica"
        ),
        "TableHeader": ParagraphStyle(
            "TableHeader", parent=styles["Normal"],
            fontSize=8, textColor=WHITE, fontName="Helvetica-Bold",
            alignment=TA_CENTER
        ),
        "TableCell": ParagraphStyle(
            "TableCell", parent=styles["Normal"],
            fontSize=8, textColor=TEXT_DARK, fontName="Helvetica",
            leading=10
        ),
        "TableCellGreen": ParagraphStyle(
            "TableCellGreen", parent=styles["Normal"],
            fontSize=8.5, textColor=FOREST_GREEN,
            fontName="Helvetica-Bold", alignment=TA_RIGHT
        ),
        "FindingBullet": ParagraphStyle(
            "FindingBullet", parent=styles["Normal"],
            fontSize=9, leading=13, textColor=TEXT_DARK,
            fontName="Helvetica", leftIndent=12, spaceAfter=4
        ),
        "Footer": ParagraphStyle(
            "Footer", parent=styles["Normal"],
            fontSize=7.5, textColor=TEXT_MID,
            fontName="Helvetica", alignment=TA_CENTER
        ),
    }
    return custom


def generate_pdf(
    valuation_result: dict,
    scenario_results: Optional[List[dict]] = None,
    narrative: Optional[str] = None,
    location_name: Optional[str] = None,
    prepared_for: Optional[str] = None,
) -> tuple[bytes, str]:
    """Generate PDF report. Returns (pdf_bytes, filename)."""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.5*cm, bottomMargin=2*cm,
        leftMargin=2*cm, rightMargin=2*cm
    )

    styles = _build_styles()
    story  = []

    eco_name   = valuation_result.get("ecosystem_name", "Ecosystem")
    area       = valuation_result.get("area_hectares", 0)
    region     = valuation_result.get("region", "").replace("_", " ").title()
    annual_mid = valuation_result.get("annual_value_mid", 0)
    npv        = valuation_result.get("npv", 0)
    carbon_t   = valuation_result.get("carbon_annual_tonnes", 0)
    bio_idx    = valuation_result.get("biodiversity_index", 0)
    clim_score = valuation_result.get("climate_resilience_score", 0)
    location   = location_name or region
    date_str   = datetime.now().strftime("%d %B %Y")

    # ══════════════════════════════════════════════════════════════════════════
    # COVER BANNER (coloured table used as banner)
    # ══════════════════════════════════════════════════════════════════════════
    banner_data = [[
        Paragraph(
            f'<font size="20"><b>EcoValue India</b></font><br/>'
            f'<font size="11" color="#c8e6c9">Ecosystem Services Valuation Report</font>',
            styles["CoverTitle"]
        )
    ]]
    banner = Table(banner_data, colWidths=[17*cm])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FOREST_GREEN),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
        ("ROUNDEDCORNERS", (0, 0), (-1, -1), [8, 8, 8, 8]),
    ]))
    story.append(banner)
    story.append(Spacer(1, 10))

    # Meta row
    meta_data = [[
        Paragraph(f"<b>Location:</b> {location}", styles["BodySmall"]),
        Paragraph(f"<b>Ecosystem:</b> {eco_name}", styles["BodySmall"]),
        Paragraph(f"<b>Area:</b> {area:,.0f} ha", styles["BodySmall"]),
        Paragraph(f"<b>Date:</b> {date_str}", styles["BodySmall"]),
    ]]
    meta_table = Table(meta_data, colWidths=[4.25*cm]*4)
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_GREEN),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("BOX",           (0, 0), (-1, -1), 0.5, SAGE_GREEN),
    ]))
    story.append(meta_table)
    if prepared_for:
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Prepared for: <b>{prepared_for}</b>", styles["BodySmall"]))
    story.append(Spacer(1, 14))

    # ══════════════════════════════════════════════════════════════════════════
    # KEY METRICS BOXES
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Key Valuation Metrics", styles["SectionHead"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=MOSS_GREEN, spaceAfter=8))

    def metric_cell(label, value, sub=""):
        return [
            Paragraph(label, styles["MetricLabel"]),
            Paragraph(value, styles["MetricValue"]),
            Paragraph(sub, styles["Tag"]),
        ]

    metrics_data = [[
        metric_cell("Annual Eco Value",  _inr_crore(annual_mid), f"₹{annual_mid/area:,.0f}/ha/yr"),
        metric_cell("10-Year NPV (8%)",  _inr_crore(npv), "Net Present Value"),
        metric_cell("Carbon Sequestered",f"{carbon_t:,.0f} tCO₂/yr", f"₹{valuation_result.get('carbon_annual_value_inr',0)/1e5:,.1f}L value"),
        metric_cell("Biodiversity Index",f"{bio_idx}/100", f"Climate Score: {clim_score}/100"),
    ]]
    metrics_table = Table(metrics_data, colWidths=[4.25*cm]*4, rowHeights=[2.2*cm])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_GREEN),
        ("BOX",           (0, 0), (0, -1), 0.5, SAGE_GREEN),
        ("BOX",           (1, 0), (1, -1), 0.5, SAGE_GREEN),
        ("BOX",           (2, 0), (2, -1), 0.5, SAGE_GREEN),
        ("BOX",           (3, 0), (3, -1), 0.5, SAGE_GREEN),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 16))

    # ══════════════════════════════════════════════════════════════════════════
    # SERVICES BREAKDOWN TABLE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Ecosystem Service Valuation Breakdown", styles["SectionHead"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=MOSS_GREEN, spaceAfter=8))

    svc_header = [
        Paragraph("Service", styles["TableHeader"]),
        Paragraph("₹/ha/yr (Min)", styles["TableHeader"]),
        Paragraph("₹/ha/yr (Mid)", styles["TableHeader"]),
        Paragraph("₹/ha/yr (Max)", styles["TableHeader"]),
        Paragraph(f"Total ({area:,.0f} ha)", styles["TableHeader"]),
        Paragraph("Share", styles["TableHeader"]),
        Paragraph("Valuation Method", styles["TableHeader"]),
    ]

    svc_rows = [svc_header]
    for s in valuation_result.get("services", []):
        svc_rows.append([
            Paragraph(s["service_name"], styles["TableCell"]),
            Paragraph(f"₹{s['value_min']:,.0f}", styles["TableCell"]),
            Paragraph(f"₹{s['value_mid']:,.0f}", styles["TableCell"]),
            Paragraph(f"₹{s['value_max']:,.0f}", styles["TableCell"]),
            Paragraph(_inr_crore(s["total_for_area"]), styles["TableCellGreen"]),
            Paragraph(f"{s['contribution_pct']:.1f}%", styles["TableCellGreen"]),
            Paragraph(s["method"][:60], styles["BodySmall"]),
        ])

    svc_table = Table(
        svc_rows,
        colWidths=[3*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.5*cm, 1.5*cm, 3.4*cm]
    )
    svc_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), FOREST_GREEN),
        ("BACKGROUND",    (0, 1), (-1, -1), WHITE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT_GREEN]),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#c8e6c9")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (1, 0), (-1, -1), "RIGHT"),
    ]))
    story.append(svc_table)
    story.append(Spacer(1, 16))

    # ══════════════════════════════════════════════════════════════════════════
    # SCENARIO COMPARISON
    # ══════════════════════════════════════════════════════════════════════════
    if scenario_results:
        story.append(Paragraph("Land Use Scenario Comparison (10-Year NPV)", styles["SectionHead"]))
        story.append(HRFlowable(width="100%", thickness=1.5, color=MOSS_GREEN, spaceAfter=8))

        scn_header = [
            Paragraph("Scenario", styles["TableHeader"]),
            Paragraph("Annual Revenue", styles["TableHeader"]),
            Paragraph("Eco Services NPV", styles["TableHeader"]),
            Paragraph("Revenue NPV", styles["TableHeader"]),
            Paragraph("Combined NPV", styles["TableHeader"]),
            Paragraph("Eco Loss", styles["TableHeader"]),
            Paragraph("Assessment", styles["TableHeader"]),
        ]
        scn_rows = [scn_header]

        for s in sorted(scenario_results, key=lambda x: x["combined_npv"], reverse=True):
            eco_loss = s.get("ecosystem_loss_pct", 0)
            loss_color = TEXT_DARK
            if eco_loss > 70:
                loss_color = colors.red
            elif eco_loss > 40:
                loss_color = colors.HexColor("#e65100")
            else:
                loss_color = FOREST_GREEN

            scn_rows.append([
                Paragraph(f"<b>{s['scenario_name']}</b>", styles["TableCell"]),
                Paragraph(_inr_crore(s["total_revenue_annual"]), styles["TableCell"]),
                Paragraph(_inr_crore(s["ecosystem_npv"]), styles["TableCellGreen"]),
                Paragraph(_inr_crore(s["revenue_npv"]), styles["TableCell"]),
                Paragraph(f"<b>{_inr_crore(s['combined_npv'])}</b>", styles["TableCellGreen"]),
                Paragraph(f"{eco_loss:.0f}%", ParagraphStyle("tmp", parent=styles["TableCell"], textColor=loss_color, fontName="Helvetica-Bold")),
                Paragraph(s["recommendation"][:55], styles["BodySmall"]),
            ])

        scn_table = Table(
            scn_rows,
            colWidths=[3.2*cm, 2.3*cm, 2.5*cm, 2.3*cm, 2.3*cm, 1.4*cm, 3*cm]
        )
        scn_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), MOSS_GREEN),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT_GREEN]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#c8e6c9")),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(scn_table)
        story.append(Spacer(1, 16))

    # ══════════════════════════════════════════════════════════════════════════
    # AI NARRATIVE
    # ══════════════════════════════════════════════════════════════════════════
    if narrative:
        story.append(Paragraph("Policy Analysis & Recommendations", styles["SectionHead"]))
        story.append(HRFlowable(width="100%", thickness=1.5, color=MOSS_GREEN, spaceAfter=8))
        for para in narrative.split("\n\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), styles["Body"]))
                story.append(Spacer(1, 6))
        story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════════
    # SOURCES
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Data Sources & Methodology", styles["SectionHead"]))
    story.append(HRFlowable(width="100%", thickness=1, color=SAGE_GREEN, spaceAfter=6))
    sources = valuation_result.get("sources", [])
    src_text = " • ".join(sources)
    story.append(Paragraph(src_text, styles["BodySmall"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        f"Generated by EcoValue India Valuation Engine | {date_str} | "
        "Values in INR/ha/yr. Sources: TEEB India, FSI ISFR 2023, TERI, MoEFCC, CPCB, ATREE, CPR India.",
        styles["Footer"]
    ))

    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    safe_loc = (location_name or region).replace(" ", "_").lower()
    filename = f"ecovalue_report_{safe_loc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return pdf_bytes, filename


def generate_pdf_b64(
    valuation_result: dict,
    scenario_results=None,
    narrative=None,
    location_name=None,
    prepared_for=None,
) -> dict:
    pdf_bytes, filename = generate_pdf(
        valuation_result, scenario_results, narrative, location_name, prepared_for
    )
    return {
        "pdf_base64": base64.b64encode(pdf_bytes).decode("utf-8"),
        "filename":   filename,
        "size_bytes": len(pdf_bytes),
    }
