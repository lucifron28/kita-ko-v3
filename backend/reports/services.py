"""
PDF Report Generation Services for Kitako MVP

This module handles generation of professional, notarization-ready PDF reports
for proof-of-income using ReportLab.
"""

import os
import io
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional

import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
import logging

from .models import IncomeReport
from transactions.models import Transaction

logger = logging.getLogger('kitako')


class IncomeReportGenerator:
    """
    Service for generating professional income reports
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def generate_ai_insights(self, report: 'IncomeReport') -> str:
        """Generate AI insights for the report"""
        try:
            insights = []
            
            # Income stability analysis
            if report.confidence_score > 85:
                insights.append("✓ High confidence in income data accuracy and consistency")
            elif report.confidence_score > 70:
                insights.append("• Moderate confidence in income data with some variations")
            else:
                insights.append("⚠ Lower confidence score suggests irregular income patterns")
            
            # Income vs expense analysis
            savings_rate = ((report.total_income - report.total_expenses) / report.total_income * 100) if report.total_income > 0 else 0
            if savings_rate > 20:
                insights.append(f"✓ Excellent savings rate of {savings_rate:.1f}% demonstrates strong financial discipline")
            elif savings_rate > 10:
                insights.append(f"✓ Good savings rate of {savings_rate:.1f}% shows healthy financial management")
            elif savings_rate > 0:
                insights.append(f"• Modest savings rate of {savings_rate:.1f}% with room for improvement")
            else:
                insights.append(f"⚠ Negative savings rate of {savings_rate:.1f}% indicates expenses exceed income")
            
            # Income source diversity
            if len(report.income_breakdown) > 3:
                insights.append("✓ Diverse income sources provide good financial stability")
            elif len(report.income_breakdown) == 2:
                insights.append("• Dual income sources offer moderate financial security")
            else:
                insights.append("⚠ Single income source increases financial vulnerability")
            
            # Transaction volume analysis
            avg_daily_transactions = report.transaction_count / ((report.date_to - report.date_from).days) if (report.date_to - report.date_from).days > 0 else 0
            if avg_daily_transactions > 5:
                insights.append("• High transaction frequency indicates active financial management")
            elif avg_daily_transactions > 2:
                insights.append("• Moderate transaction activity shows regular financial activity")
            else:
                insights.append("• Lower transaction frequency may indicate simplified financial habits")
            
            # Data source reliability
            if len(report.data_sources) > 2:
                insights.append("✓ Multiple data sources enhance report reliability and completeness")
            else:
                insights.append("• Limited data sources may affect comprehensive financial overview")
            
            return "\n".join(insights)
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return "AI insights generation encountered an error. Manual review recommended."
    
    def _generate_qr_code_image(self, report: 'IncomeReport') -> Optional[Image]:
        """Generate QR code image for document verification"""
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Add verification URL to QR code
            if report.qr_code_url:
                qr.add_data(report.qr_code_url)
                qr.make(fit=True)
                
                # Create QR code image
                qr_img = qr.make_image(fill_color="black", back_color="white")
                
                # Save to memory buffer
                buffer = io.BytesIO()
                qr_img.save(buffer, format='PNG')
                buffer.seek(0)
                
                # Create ReportLab Image
                qr_image = Image(buffer)
                qr_image.drawWidth = 1.5 * inch
                qr_image.drawHeight = 1.5 * inch
                
                return qr_image
                
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
        
        return None
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50')
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#34495E')
        ))
        
        # Body text with justification
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=14
        ))
        
        # Small text for disclaimers
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=6,
            textColor=colors.HexColor('#7F8C8D')
        ))
    
    def generate_report(self, report: IncomeReport) -> bool:
        """
        Generate PDF report for the given IncomeReport instance
        """
        try:
            # Generate AI insights if not already present
            if not report.ai_insights:
                report.ai_insights = self.generate_ai_insights(report)
                report.save(update_fields=['ai_insights'])
            
            # Create PDF buffer
            buffer = io.BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build content
            story = []
            
            # Header
            story.extend(self._build_header(report))
            
            # Executive Summary
            story.extend(self._build_executive_summary(report))
            
            # Financial Overview
            story.extend(self._build_financial_overview(report))
            
            # Income Analysis
            story.extend(self._build_income_analysis(report))
            
            # Data Sources
            story.extend(self._build_data_sources(report))
            
            # Verification Section
            story.extend(self._build_verification_section(report))
            
            # Notarization Section
            story.extend(self._build_notarization_section(report))
            
            # Footer/Disclaimers
            story.extend(self._build_footer(report))
            
            # Build PDF
            doc.build(story)
            
            # Save to model
            pdf_content = buffer.getvalue()
            buffer.close()
            
            # Create filename
            filename = f"income_report_{report.user.id}_{report.date_from}_{report.date_to}.pdf"
            
            # Save to model
            report.pdf_file.save(
                filename,
                ContentFile(pdf_content),
                save=False
            )
            
            # Update report status
            report.status = 'completed'
            report.completed_at = timezone.now()
            report.file_size = len(pdf_content)
            report.save()
            
            logger.info(f"Generated PDF report for user {report.user.email}")
            return True
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            report.status = 'failed'
            report.generation_error = str(e)
            report.save()
            return False
    
    def _build_header(self, report: IncomeReport) -> List:
        """Build report header"""
        story = []
        
        # Title
        title = Paragraph("PRELIMINARY PROOF OF INCOME REPORT", self.styles['CustomTitle'])
        story.append(title)
        
        # Subtitle with important notice
        subtitle = Paragraph("<b>PRELIMINARY DOCUMENT - REQUIRES NOTARIZATION FOR LEGAL VALIDITY</b>", 
                           self.styles['CustomSubtitle'])
        story.append(subtitle)
        story.append(Spacer(1, 12))
        
        # Report info table
        report_info = [
            ['Report Period:', f"{report.date_from} to {report.date_to}"],
            ['Generated On:', timezone.now().strftime('%B %d, %Y')],
            ['Report ID:', str(report.verification_code)],
            ['Purpose:', report.get_purpose_display()],
            ['Document Status:', 'PRELIMINARY - NOT NOTARIZED'],
        ]
        
        info_table = Table(report_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#BDC3C7')))
        story.append(Spacer(1, 20))
        
        return story
    
    def _build_executive_summary(self, report: IncomeReport) -> List:
        """Build executive summary section"""
        story = []
        
        # Section title
        title = Paragraph("EXECUTIVE SUMMARY", self.styles['CustomSubtitle'])
        story.append(title)
        
        # Summary text
        summary_text = report.summary or self._generate_default_summary(report)
        summary = Paragraph(summary_text, self.styles['CustomBody'])
        story.append(summary)
        story.append(Spacer(1, 20))
        
        return story
    
    def _build_financial_overview(self, report: IncomeReport) -> List:
        """Build financial overview section"""
        story = []
        
        # Section title
        title = Paragraph("FINANCIAL OVERVIEW", self.styles['CustomSubtitle'])
        story.append(title)
        
        # Financial summary table
        financial_data = [
            ['Metric', 'Amount (PHP)', 'Details'],
            ['Total Income', f"₱{report.total_income:,.2f}", f"From {report.transaction_count} transactions"],
            ['Total Expenses', f"₱{report.total_expenses:,.2f}", "Documented expenses"],
            ['Net Income', f"₱{report.net_income:,.2f}", "Income minus expenses"],
            ['Average Monthly Income', f"₱{report.average_monthly_income:,.2f}", "Based on report period"],
        ]
        
        financial_table = Table(financial_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(financial_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _build_income_analysis(self, report: IncomeReport) -> List:
        """Build income analysis section"""
        story = []
        
        # Section title
        title = Paragraph("INCOME BREAKDOWN", self.styles['CustomSubtitle'])
        story.append(title)
        
        # Income breakdown table
        if report.income_breakdown:
            breakdown_data = [['Income Category', 'Amount (PHP)', 'Percentage']]
            
            total_income = float(report.total_income)
            for category, amount in report.income_breakdown.items():
                percentage = (float(amount) / total_income * 100) if total_income > 0 else 0
                breakdown_data.append([
                    category.replace('_', ' ').title(),
                    f"₱{float(amount):,.2f}",
                    f"{percentage:.1f}%"
                ])
            
            breakdown_table = Table(breakdown_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
            breakdown_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(breakdown_table)
        else:
            story.append(Paragraph("Income breakdown data not available.", self.styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        
        return story
    
    def _build_data_sources(self, report: IncomeReport) -> List:
        """Build data sources section"""
        story = []
        
        # Section title
        title = Paragraph("DATA SOURCES", self.styles['CustomSubtitle'])
        story.append(title)
        
        # Data sources text
        if report.data_sources:
            sources_text = "This report is based on financial data from the following sources: " + \
                          ", ".join(report.data_sources) + "."
        else:
            sources_text = "This report is based on uploaded financial documents and transaction records."
        
        sources = Paragraph(sources_text, self.styles['CustomBody'])
        story.append(sources)
        
        # AI analysis note
        if report.ai_insights:
            ai_title = Paragraph("AI ANALYSIS INSIGHTS", self.styles['CustomSubtitle'])
            story.append(ai_title)
            ai_insights = Paragraph(report.ai_insights, self.styles['CustomBody'])
            story.append(ai_insights)
        
        story.append(Spacer(1, 20))
        
        return story
    
    def _build_verification_section(self, report: IncomeReport) -> List:
        """Build verification section"""
        story = []
        
        # Section title
        title = Paragraph("VERIFICATION INFORMATION", self.styles['CustomSubtitle'])
        story.append(title)
        
        # Verification details
        verification_data = [
            ['Verification Code:', report.verification_code],
            ['Document Hash:', report.document_hash[:32] + '...' if report.document_hash else 'Will be generated'],
            ['Confidence Score:', f"{report.confidence_score}%" if report.confidence_score else 'N/A'],
            ['Generated By:', 'Kitako AI Platform'],
        ]
        
        verification_table = Table(verification_data, colWidths=[2*inch, 4*inch])
        verification_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(verification_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _build_notarization_section(self, report: IncomeReport) -> List:
        """Build notarization section with signature placeholders"""
        story = []
        
        # Page break for notarization section
        story.append(PageBreak())
        
        # Important notice
        notice_title = Paragraph("IMPORTANT LEGAL NOTICE", self.styles['CustomSubtitle'])
        story.append(notice_title)
        
        notice_text = """
        <b>FOR LEGAL VALIDITY, THIS DOCUMENT MUST BE NOTARIZED</b><br/><br/>
        This document serves as a preliminary proof of income report generated by Kitako AI Platform. 
        To be considered legally valid for official purposes (loan applications, government submissions, 
        legal proceedings, etc.), this document must be properly notarized by a licensed notary public.
        """
        
        notice = Paragraph(notice_text, self.styles['CustomBody'])
        story.append(notice)
        story.append(Spacer(1, 30))
        
        # Attestation section
        attestation_title = Paragraph("ATTESTATION AND SIGNATURE", self.styles['CustomSubtitle'])
        story.append(attestation_title)
        
        attestation_text = f"""
        I, <b>{report.user.full_name}</b>, hereby attest that the information contained in this income 
        report is true and accurate to the best of my knowledge. I understand that providing false 
        information may result in legal consequences.
        """
        
        attestation = Paragraph(attestation_text, self.styles['CustomBody'])
        story.append(attestation)
        story.append(Spacer(1, 40))
        
        # Signature lines
        signature_data = [
            ['', ''],
            ['_' * 40, '_' * 20],
            ['Signature of Report Holder', 'Date'],
            ['', ''],
            [f'{report.user.full_name}', ''],
            ['Printed Name', ''],
        ]
        
        signature_table = Table(signature_data, colWidths=[4*inch, 2*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 2), (-1, 2), 15),
        ]))
        
        story.append(signature_table)
        story.append(Spacer(1, 50))
        
        # Notary section
        notary_title = Paragraph("FOR NOTARY PUBLIC USE ONLY", self.styles['CustomSubtitle'])
        story.append(notary_title)
        
        notary_text = """
        <b>ACKNOWLEDGMENT</b><br/><br/>
        On this _____ day of _____________, 20___, before me personally appeared 
        <b>""" + report.user.full_name + """</b>, who proved to me on the basis of satisfactory evidence 
        to be the person whose name is subscribed to the within instrument and acknowledged to me that 
        he/she executed the same in his/her authorized capacity, and that by his/her signature on the 
        instrument the person, or the entity upon behalf of which the person acted, executed the instrument.
        <br/><br/>
        I certify under PENALTY OF PERJURY under the laws of the Republic of the Philippines that the 
        foregoing paragraph is true and correct.
        <br/><br/>
        WITNESS my hand and official seal.
        """
        
        notary_paragraph = Paragraph(notary_text, self.styles['CustomBody'])
        story.append(notary_paragraph)
        story.append(Spacer(1, 40))
        
        # Notary signature section
        notary_signature_data = [
            ['', ''],
            ['_' * 40, '_' * 25],
            ['Signature of Notary Public', 'My Commission Expires'],
            ['', ''],
            ['_' * 40, ''],
            ['Printed Name of Notary Public', ''],
            ['', ''],
            ['[NOTARY SEAL]', ''],
        ]
        
        notary_signature_table = Table(notary_signature_data, colWidths=[4*inch, 2.5*inch])
        notary_signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('FONTNAME', (0, 7), (-1, 7), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 2), (-1, 2), 15),
            ('BOX', (0, 7), (0, 7), 1, colors.black),
            ('ALIGN', (0, 7), (0, 7), 'CENTER'),
        ]))
        
        story.append(notary_signature_table)
        story.append(Spacer(1, 40))
        
        # QR Code Verification Section
        verification_title = Paragraph("DOCUMENT VERIFICATION", self.styles['CustomSubtitle'])
        story.append(verification_title)
        
        # Generate QR code
        qr_image = self._generate_qr_code_image(report)
        
        if qr_image:
            verification_text = f"""
            <b>Scan QR Code to Verify Document Authenticity</b><br/><br/>
            This document can be verified online using the QR code below or by visiting:<br/>
            <b>{report.qr_code_url}</b><br/><br/>
            Verification Code: <b>{report.verification_code}</b><br/>
            Document Hash: <font name="Courier">{report.document_hash[:32]}...</font><br/><br/>
            <b>Verification Status:</b> {report.get_signature_verification_status_display()}
            """
            
            verification_paragraph = Paragraph(verification_text, self.styles['CustomBody'])
            
            # Create table with QR code and text
            verification_data = [
                [qr_image, verification_paragraph]
            ]
            
            verification_table = Table(verification_data, colWidths=[2*inch, 4.5*inch])
            verification_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (1, 0), (1, 0), 20),
            ]))
            
            story.append(verification_table)
        else:
            # Fallback if QR code generation fails
            verification_text = f"""
            <b>Document Verification Information</b><br/><br/>
            Verification Code: <b>{report.verification_code}</b><br/>
            Document Hash: <font name="Courier">{report.document_hash[:32]}...</font><br/>
            Verification URL: {report.qr_code_url}<br/><br/>
            <b>Verification Status:</b> {report.get_signature_verification_status_display()}
            """
            
            verification_paragraph = Paragraph(verification_text, self.styles['CustomBody'])
            story.append(verification_paragraph)
        
        story.append(Spacer(1, 20))
        
        return story
    
    def _build_footer(self, report: IncomeReport) -> List:
        """Build footer with disclaimers"""
        story = []
        
        # Legal disclaimer
        legal_disclaimer_text = """
        <b>LEGAL DISCLAIMER AND LIMITATIONS</b><br/><br/>
        
        <b>1. DOCUMENT STATUS:</b> This document is a PRELIMINARY income analysis report generated by 
        automated AI systems. It is NOT a legally binding document and has NO legal validity until 
        properly notarized by a licensed notary public.<br/><br/>
        
        <b>2. DATA ACCURACY:</b> This report is based on financial transaction data provided by the user 
        and processed through AI-powered categorization. While every effort has been made to ensure accuracy, 
        Kitako makes no warranties regarding the completeness or accuracy of the data analysis.<br/><br/>
        
        <b>3. VERIFICATION REQUIRED:</b> All financial institutions, government agencies, and other parties 
        should independently verify the information contained herein. This document should be used only as 
        a preliminary assessment tool.<br/><br/>
        
        <b>4. LIABILITY LIMITATION:</b> Kitako, its employees, and affiliates shall not be liable for any 
        decisions made based on this preliminary report. Users are responsible for ensuring all information 
        is accurate before notarization.<br/><br/>
        
        <b>5. INTENDED USE:</b> This document is intended solely to facilitate the preparation of official 
        income documentation. It must be reviewed, verified, and notarized before submission for any legal, 
        financial, or official purposes.
        """
        
        disclaimer = Paragraph(legal_disclaimer_text, self.styles['SmallText'])
        story.append(disclaimer)
        
        story.append(Spacer(1, 20))
        
        # Contact and verification information
        contact_text = """
        <b>DOCUMENT VERIFICATION:</b> For verification of this preliminary report, contact Kitako Support 
        at support@kitako.ph with verification code: """ + f"<b>{report.verification_code}</b>" + """
        <br/><br/>
        <b>GENERATED:</b> """ + f"{timezone.now().strftime('%B %d, %Y at %I:%M %p %Z')}" + """<br/>
        <b>PLATFORM:</b> Kitako AI Financial Management Platform<br/>
        <b>VERSION:</b> 1.0 (Beta)<br/>
        <b>REPORT ID:</b> """ + f"{report.id}"
        
        contact = Paragraph(contact_text, self.styles['SmallText'])
        story.append(contact)
        
        return story
    
    def _generate_default_summary(self, report: IncomeReport) -> str:
        """Generate a default summary if none provided"""
        period_days = (report.date_to - report.date_from).days
        period_months = period_days / 30.44  # Average days per month
        
        # Calculate some insights
        income_stability = "stable" if report.confidence_score > 80 else "variable"
        financial_status = "positive" if report.net_income > 0 else "negative" if report.net_income < 0 else "balanced"
        
        return f"""
        This report presents a comprehensive analysis of financial activity for the period from 
        {report.date_from} to {report.date_to} ({period_days} days). During this period, 
        total documented income was ₱{report.total_income:,.2f} with total expenses of 
        ₱{report.total_expenses:,.2f}, resulting in a {financial_status} net income of 
        ₱{report.net_income:,.2f}. The average monthly income during this period was 
        ₱{report.average_monthly_income:,.2f}, indicating {income_stability} income patterns. 
        This analysis is based on {report.transaction_count} financial transactions from 
        {len(report.data_sources)} verified data sources, processed through AI-powered 
        categorization and analysis with a confidence score of {report.confidence_score}%.
        """
