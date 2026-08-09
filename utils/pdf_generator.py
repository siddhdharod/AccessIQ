import io
import os
import pandas as pd

def generate_accessibility_pdf_report(
    location_name: str,
    score: float,
    category: str,
    priority: str,
    city: str,
    features_dict: dict,
    ai_suggestions: str = None,
    weather_info: str = None
) -> bytes:
    """Generate a high-quality PDF report using ReportLab with fallback."""
    buffer = io.BytesIO()

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1e1b4b')
        )

        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#64748b')
        )

        heading2_style = ParagraphStyle(
            'Heading2Custom',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#4f46e5'),
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'BodyCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#1e293b')
        )

        story = []

        # Title Banner
        story.append(Paragraph("URBAN ACCESSIBILITY & INFRASTRUCTURE AUDIT REPORT", title_style))
        story.append(Paragraph(f"Official AI Evaluation for <b>{location_name}</b> ({city})", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#6366f1'), spaceAfter=15))

        # Core Metrics Summary Table
        metrics_data = [
            [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Audit Value</b>", body_style)],
            [Paragraph("Location Name", body_style), Paragraph(str(location_name), body_style)],
            [Paragraph("City / Region", body_style), Paragraph(str(city), body_style)],
            [Paragraph("Accessibility Score", body_style), Paragraph(f"<b>{score:.1f} / 100</b>", body_style)],
            [Paragraph("Accessibility Category", body_style), Paragraph(f"<b>{category}</b>", body_style)],
            [Paragraph("Improvement Priority", body_style), Paragraph(f"<b>{priority}</b>", body_style)]
        ]

        t_metrics = Table(metrics_data, colWidths=[200, 300])
        t_metrics.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0,0), (1,0), colors.HexColor('#0f172a')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_metrics)
        story.append(Spacer(1, 15))

        # Infrastructure Audit Breakdown
        story.append(Paragraph("1. Infrastructure Checklist & Compliance", heading2_style))
        
        infra_items = [
            ("Wheelchair Ramp Available", features_dict.get("Ramp_Available", 0)),
            ("Elevator Access Available", features_dict.get("Elevator_Available", 0)),
            ("Wheelchair Accessible Entrance", features_dict.get("Wheelchair_Entrance", 0)),
            ("Braille Signage & Tactile Maps", features_dict.get("Braille_Signage", 0)),
            ("Audio Assistance System", features_dict.get("Audio_Announcements", 0)),
            ("Accessible Washroom Facilities", features_dict.get("Accessible_Washroom", 0)),
            ("Tactile Paving Path", features_dict.get("Tactile_Path", 0)),
            ("Reserved Accessible Parking", features_dict.get("Reserved_Parking", 0)),
        ]

        infra_table_data = [[Paragraph("<b>Feature Parameter</b>", body_style), Paragraph("<b>Status</b>", body_style)]]
        for name, val in infra_items:
            status_text = "<font color='#059669'><b>AVAILABLE (YES)</b></font>" if val == 1 else "<font color='#e11d48'>NOT DETECTED (NO)</font>"
            infra_table_data.append([Paragraph(name, body_style), Paragraph(status_text, body_style)])

        t_infra = Table(infra_table_data, colWidths=[300, 200])
        t_infra.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_infra)
        story.append(Spacer(1, 15))

        # AI Recommendations Section
        story.append(Paragraph("2. AI-Generated Accessibility Suggestions", heading2_style))
        ai_text = ai_suggestions if ai_suggestions else (
            "Prioritize installing ramp facilities at main entry steps, ensure all tactile paths remain unobstructed, "
            "and upgrade audio announcement speakers for hearing and visually impaired visitors."
        )
        story.append(Paragraph(ai_text.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 15))

        # Weather Notice if present
        if weather_info:
            story.append(Paragraph("3. Real-Time Environmental & Weather Notice", heading2_style))
            story.append(Paragraph(weather_info, body_style))
            story.append(Spacer(1, 15))

        # Footer Signoff
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=20, spaceAfter=10))
        story.append(Paragraph("Generated by AccessIQ • Intelligent Urban Accessibility Platform", subtitle_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        # Emergency text fallback if reportlab is not available
        buffer.seek(0)
        content = f"""
        =====================================================
        URBAN ACCESSIBILITY AUDIT REPORT
        Location: {location_name} ({city})
        =====================================================
        Score: {score:.1f} / 100
        Category: {category}
        Priority: {priority}

        AI Suggestions:
        {ai_suggestions or 'Standard accessibility improvements recommended.'}
        =====================================================
        (Report PDF fallback generated)
        """
        return content.encode('utf-8')
