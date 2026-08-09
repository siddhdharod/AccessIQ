import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget

def generate_booking_pdf_receipt(booking_dict: dict, user_full_name: str = "") -> bytes:
    """
    Generate a professional downloadable PDF receipt for a Smart Accessibility Booking.
    """
    buffer = io.BytesIO()

    try:
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
            'ReceiptTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#1e1b4b')
        )

        subtitle_style = ParagraphStyle(
            'ReceiptSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#64748b')
        )

        heading_style = ParagraphStyle(
            'Heading2Custom',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#7c3aed'),
            spaceBefore=10,
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

        # 1. Header Banner
        story.append(Paragraph("ACCESSIQ — SMART ACCESSIBILITY RESERVATION RECEIPT", title_style))
        story.append(Paragraph(f"Official Booking Confirmation & Digital Access Pass", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#7c3aed'), spaceAfter=15))

        # 2. Main Booking Specs Table
        b_id = booking_dict.get("booking_id", "N/A")
        loc = booking_dict.get("location_name", "N/A")
        service = booking_dict.get("service_type", "N/A")
        slot = booking_dict.get("slot_id", "N/A")
        b_date = booking_dict.get("booking_date", "N/A")
        s_time = booking_dict.get("start_time", "N/A")
        e_time = booking_dict.get("end_time", "N/A")
        dur = booking_dict.get("duration_str", "N/A")
        amt = booking_dict.get("amount_inr", 0)
        status = booking_dict.get("status", "Active")
        created = booking_dict.get("created_at", "N/A")
        username = booking_dict.get("username", "N/A")
        customer = user_full_name if user_full_name else username

        table_data = [
            [Paragraph("<b>Receipt Parameter</b>", body_style), Paragraph("<b>Details</b>", body_style)],
            [Paragraph("Booking Reference ID", body_style), Paragraph(f"<b>{b_id}</b>", body_style)],
            [Paragraph("Customer Name", body_style), Paragraph(customer, body_style)],
            [Paragraph("Venue / Building Location", body_style), Paragraph(f"<b>{loc}</b>", body_style)],
            [Paragraph("Reserved Accessibility Service", body_style), Paragraph(service, body_style)],
            [Paragraph("Assigned Facility Slot", body_style), Paragraph(f"<font color='#7c3aed'><b>SLOT {slot}</b></font>", body_style)],
            [Paragraph("Reservation Date", body_style), Paragraph(b_date, body_style)],
            [Paragraph("Time Window", body_style), Paragraph(f"{s_time} to {e_time} ({dur})", body_style)],
            [Paragraph("Total Paid Amount", body_style), Paragraph(f"<b>Rs. {amt} INR</b>", body_style)],
            [Paragraph("Booking Status", body_style), Paragraph(f"<font color='#059669'><b>{status.upper()}</b></font>", body_style)],
            [Paragraph("Issued Timestamp", body_style), Paragraph(created, body_style)],
        ]

        t_details = Table(table_data, colWidths=[200, 300])
        t_details.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0,0), (1,0), colors.HexColor('#0f172a')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_details)
        story.append(Spacer(1, 15))

        # 3. Digital Pass QR Code Section
        story.append(Paragraph("Digital Verification Pass & QR Gate Pass", heading_style))
        story.append(Paragraph("Show this digital QR pass at the venue entrance for automated gate access and staff verification.", body_style))
        story.append(Spacer(1, 10))

        qr_text = f"ACCESSIQ:{b_id}:{loc}:{slot}:{b_date}:{s_time}"
        qr_widget = QrCodeWidget(qr_text)
        qr_widget.barWidth = 120
        qr_widget.barHeight = 120
        qr_widget.qrVersion = 1
        d = Drawing(120, 120)
        d.add(qr_widget)
        story.append(d)

        story.append(Spacer(1, 15))

        # 4. Terms & Platform Sign-off
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=15, spaceAfter=10))
        story.append(Paragraph("<b>Terms & Conditions:</b> Reservations are valid strictly during the selected time window. Slots released immediately upon cancellation. Free cancellation available prior to start time.", subtitle_style))
        story.append(Spacer(1, 5))
        story.append(Paragraph("Generated by AccessIQ • AI-Powered Urban Accessibility Platform", subtitle_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        buffer.seek(0)
        fallback_text = f"""
        ====================================================
        ACCESSIQ SMART ACCESSIBILITY BOOKING RECEIPT
        ====================================================
        Booking ID: {booking_dict.get('booking_id', 'N/A')}
        Customer: {user_full_name or booking_dict.get('username', 'N/A')}
        Location: {booking_dict.get('location_name', 'N/A')}
        Service: {booking_dict.get('service_type', 'N/A')}
        Slot: {booking_dict.get('slot_id', 'N/A')}
        Date & Time: {booking_dict.get('booking_date')} ({booking_dict.get('start_time')} - {booking_dict.get('end_time')})
        Duration: {booking_dict.get('duration_str')}
        Amount: Rs. {booking_dict.get('amount_inr')} INR
        Status: {booking_dict.get('status')}
        ====================================================
        """
        return fallback_text.encode('utf-8')
