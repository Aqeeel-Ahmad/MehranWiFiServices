import io
from django.utils import timezone
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

def generate_receipt_pdf(payment):
    """
    Generates a professional PDF digital receipt for a HAM 3 NETWORK payment.
    Returns bytes buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#64748B'),
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6,
    )
    normal_text = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
    )
    bold_text = ParagraphStyle(
        'BoldText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#0F172A'),
    )
    status_verified = ParagraphStyle(
        'StatusVerified',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#059669'),
        alignment=2,
    )
    status_pending = ParagraphStyle(
        'StatusPending',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#D97706'),
        alignment=2,
    )

    sub = payment.subscription
    pkg_name = sub.package_name_snapshot if sub else (payment.subscription.package.name if sub and sub.package else "Fiber Package")
    speed_mbps = sub.speed_snapshot if sub else (sub.package.speed_mbps if sub and sub.package else "N/A")
    purchase_date_str = sub.purchase_date.strftime('%B %d, %Y') if sub and sub.purchase_date else payment.payment_date.strftime('%B %d, %Y')
    expiry_date_str = sub.expiry_date.strftime('%B %d, %Y') if sub and sub.expiry_date else "8th of Next Month"

    # Header section
    header_data = [
        [
            Paragraph("<b>HAM 3 NETWORK</b><br/><font size=8 color='#64748B'>High-Speed Fiber Optic Internet Provider<br/>NOC Support: 03452524086 | support@mehranwifi.com</font>", title_style),
            Paragraph(f"<b>RECEIPT / INVOICE</b><br/><font size=9 color='#64748B'>Receipt #: <b>{payment.receipt_number}</b><br/>Date: {payment.payment_date.strftime('%B %d, %Y %H:%M')}</font>", ParagraphStyle('RHeader', parent=styles['Normal'], alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[320, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0284C7'), spaceBefore=4, spaceAfter=12))

    # Customer and Status Row
    status_style = status_verified if payment.verification_status == 'verified' else status_pending
    status_label = "🟢 PACKAGE ACTIVE / PAYMENT VERIFIED" if payment.verification_status == 'verified' else "🟡 PENDING VERIFICATION"
    
    user_profile = getattr(payment.user, 'profile', None)
    customer_phone = user_profile.phone_number if user_profile else "N/A"
    customer_whatsapp = user_profile.whatsapp_number if user_profile and user_profile.whatsapp_number else customer_phone
    customer_address = user_profile.address if user_profile and user_profile.address else "HAM 3 Service Area"

    cust_info = f"""
    <b>Billed To:</b> {payment.user.get_full_name() or payment.user.username}<br/>
    <b>Username:</b> {payment.user.username} &nbsp;|&nbsp; <b>User ID:</b> #{payment.user.id}<br/>
    <b>Phone:</b> {customer_phone} &nbsp;|&nbsp; <b>WhatsApp:</b> {customer_whatsapp}<br/>
    <b>Address:</b> {customer_address}
    """

    status_box = f"""
    <b>Status:</b><br/>
    <font size=11><b>{status_label}</b></font><br/>
    <font size=8 color='#64748B'>Processed via EasyPaisa Gateway</font>
    """

    meta_table = Table([
        [Paragraph(cust_info, normal_text), Paragraph(status_box, status_style)]
    ], colWidths=[330, 190])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#F8FAFC')),
        ('BOX', (1,0), (1,0), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (1,0), (1,0), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 16))

    # Package Details Table
    story.append(Paragraph("Internet Package & Subscription Details", section_heading))
    items_data = [
        [
            Paragraph("<b>Package Description</b>", bold_text),
            Paragraph("<b>Speed</b>", bold_text),
            Paragraph("<b>Purchase Date</b>", bold_text),
            Paragraph("<b>Expiry Date</b>", bold_text),
            Paragraph("<b>Amount (PKR)</b>", ParagraphStyle('AmtH', parent=bold_text, alignment=2)),
        ],
        [
            Paragraph(f"<b>{pkg_name}</b><br/><font size=8 color='#64748B'>Fiber To The Home (FTTH) Dedicated Connection</font>", normal_text),
            Paragraph(f"{speed_mbps} Mbps", normal_text),
            Paragraph(purchase_date_str, normal_text),
            Paragraph(f"<b>{expiry_date_str}</b><br/><font size=7 color='#0284C7'>Auto-calc (8th of month)</font>", normal_text),
            Paragraph(f"Rs. {payment.amount:,.0f}", ParagraphStyle('AmtD', parent=normal_text, alignment=2)),
        ],
        [
            "", "", "",
            Paragraph("<b>Total Amount:</b>", ParagraphStyle('TotalL', parent=bold_text, alignment=2)),
            Paragraph(f"<b>Rs. {payment.amount:,.0f}</b>", ParagraphStyle('TotalV', parent=bold_text, alignment=2)),
        ]
    ]

    items_table = Table(items_data, colWidths=[180, 70, 95, 95, 80])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')),
        ('LINEBELOW', (0,1), (-1,1), 1, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,1), (-1,1), 8),
        ('BOTTOMPADDING', (0,1), (-1,1), 8),
        ('TOPPADDING', (0,2), (-1,2), 8),
        ('BACKGROUND', (3,2), (4,2), colors.HexColor('#EFF6FF')),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 16))

    # EasyPaisa Payment Verification Box
    story.append(Paragraph("EasyPaisa Payment Transaction Verification", section_heading))
    pay_data = [
        [
            Paragraph("<b>Payment Gateway:</b>", bold_text),
            Paragraph("EasyPaisa Mobile Account", normal_text),
            Paragraph("<b>EasyPaisa Receiver No:</b>", bold_text),
            Paragraph(payment.easypaisa_number, normal_text),
        ],
        [
            Paragraph("<b>Transaction ID (TRX):</b>", bold_text),
            Paragraph(f"<b>{payment.transaction_id}</b>", bold_text),
            Paragraph("<b>Sender Account:</b>", bold_text),
            Paragraph(payment.sender_number or "Provided during transfer", normal_text),
        ],
        [
            Paragraph("<b>Verification Status:</b>", bold_text),
            Paragraph(payment.get_verification_status_display(), normal_text),
            Paragraph("<b>Verified By:</b>", bold_text),
            Paragraph(str(payment.verified_by.username) if payment.verified_by else "Admin / Auto Verification", normal_text),
        ]
    ]
    pay_table = Table(pay_data, colWidths=[130, 130, 130, 130])
    pay_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FAFAFA')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(pay_table)
    story.append(Spacer(1, 20))

    # Digital Verification Stamp & Terms
    stamp_text = """
    <b>OFFICIAL DIGITAL RECEIPT - HAM 3 NETWORK</b><br/>
    This digital receipt certifies that the package payment was recorded and processed through the EasyPaisa merchant channel.<br/>
    Internet speeds are subject to optical fiber link state. Billing cycle resets on the 8th of every month.
    """
    story.append(Paragraph(stamp_text, ParagraphStyle('Stamp', parent=normal_text, fontSize=8, textColor=colors.HexColor('#64748B'), alignment=1)))
    story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_history_pdf(user, subscriptions):
    """
    Generates a full package history & billing statement for the user.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()
    story = []

    bold_text = ParagraphStyle('BoldH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#0F172A'))
    normal_text = ParagraphStyle('NormH', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#334155'))

    # Header
    title = Paragraph("<b>HAM 3 NETWORK</b><br/><font size=10 color='#64748B'>Customer Package History & Account Statement</font>", ParagraphStyle('H1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22))
    today_str = timezone.now().strftime('%B %d, %Y')
    
    story.append(title)
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0284C7'), spaceBefore=6, spaceAfter=12))

    # User summary
    profile = getattr(user, 'profile', None)
    total_spent = sum(s.price_snapshot for s in subscriptions)
    user_info = f"""
    <b>Customer:</b> {user.get_full_name() or user.username} &nbsp;|&nbsp; <b>Username:</b> {user.username} &nbsp;|&nbsp; <b>ID:</b> #{user.id}<br/>
    <b>Phone:</b> {profile.phone_number if profile else 'N/A'} &nbsp;|&nbsp; <b>Joined:</b> {user.date_joined.strftime('%B %d, %Y')}<br/>
    <b>Total Packages Subscribed:</b> {subscriptions.count()} &nbsp;|&nbsp; <b>Total Spent:</b> Rs. {total_spent:,.0f}
    """
    story.append(Paragraph(user_info, ParagraphStyle('CustH', parent=styles['Normal'], fontSize=9, leading=14)))
    story.append(Spacer(1, 14))

    # Table
    table_data = [
        [
            Paragraph("<b>#</b>", bold_text),
            Paragraph("<b>Package Name</b>", bold_text),
            Paragraph("<b>Speed</b>", bold_text),
            Paragraph("<b>Price (PKR)</b>", bold_text),
            Paragraph("<b>Purchase Date</b>", bold_text),
            Paragraph("<b>Expiry Date</b>", bold_text),
            Paragraph("<b>Status</b>", bold_text),
        ]
    ]

    for idx, sub in enumerate(subscriptions, start=1):
        status_label = sub.get_status_display()
        p_name = sub.package_name_snapshot or (sub.package.name if sub.package else "Fiber Plan")
        speed = f"{sub.speed_snapshot or (sub.package.speed_mbps if sub.package else '')} Mbps"
        price = f"Rs. {sub.price_snapshot:,.0f}"
        p_date = sub.purchase_date.strftime('%b %d, %Y') if sub.purchase_date else "N/A"
        e_date = sub.expiry_date.strftime('%b %d, %Y') if sub.expiry_date else "N/A"
        table_data.append([
            Paragraph(str(idx), normal_text),
            Paragraph(p_name, normal_text),
            Paragraph(speed, normal_text),
            Paragraph(price, normal_text),
            Paragraph(p_date, normal_text),
            Paragraph(e_date, normal_text),
            Paragraph(status_label, normal_text),
        ])

    tbl = Table(table_data, colWidths=[25, 140, 65, 75, 75, 75, 65])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 16))

    note = "This statement is automatically generated by HAM 3 NETWORK Management System. NOC Hotline: 03452524086"
    story.append(Paragraph(note, ParagraphStyle('Note', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#64748B'), alignment=1)))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
