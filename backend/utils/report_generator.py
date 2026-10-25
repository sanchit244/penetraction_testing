from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from typing import List, Dict, Any
import os


class ReportGenerator:
    """Generate PDF reports for vulnerability scans"""

    def __init__(self, report_path: str):
        self.report_path = report_path
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12
        ))

    def generate_report(
        self,
        scan_id: str,
        target_url: str,
        vulnerabilities: List[Dict[str, Any]],
        summary: Dict[str, Any]
    ) -> str:
        """
        Generate PDF report for scan results

        Returns:
            Path to generated PDF file
        """
        filename = f"scan_report_{scan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.report_path, filename)

        # Ensure report directory exists
        os.makedirs(self.report_path, exist_ok=True)

        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []

        # Title
        title = Paragraph("Vulnerability Scan Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))

        # Scan Information
        story.append(Paragraph("Scan Information", self.styles['SectionHeader']))

        scan_info_data = [
            ['Scan ID:', scan_id],
            ['Target URL:', target_url],
            ['Scan Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Vulnerabilities:', str(summary.get('total_vulnerabilities', 0))]
        ]

        scan_info_table = Table(scan_info_data, colWidths=[2*inch, 4*inch])
        scan_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))

        story.append(scan_info_table)
        story.append(Spacer(1, 0.3 * inch))

        # Severity Summary
        story.append(Paragraph("Severity Summary", self.styles['SectionHeader']))

        severity_data = [
            ['Severity', 'Count', 'Percentage'],
            ['Critical', str(summary.get('critical_count', 0)),
             f"{self._calculate_percentage(summary.get('critical_count', 0), summary.get('total_vulnerabilities', 0))}%"],
            ['High', str(summary.get('high_count', 0)),
             f"{self._calculate_percentage(summary.get('high_count', 0), summary.get('total_vulnerabilities', 0))}%"],
            ['Medium', str(summary.get('medium_count', 0)),
             f"{self._calculate_percentage(summary.get('medium_count', 0), summary.get('total_vulnerabilities', 0))}%"],
            ['Low', str(summary.get('low_count', 0)),
             f"{self._calculate_percentage(summary.get('low_count', 0), summary.get('total_vulnerabilities', 0))}%"],
            ['Info', str(summary.get('info_count', 0)),
             f"{self._calculate_percentage(summary.get('info_count', 0), summary.get('total_vulnerabilities', 0))}%"],
        ]

        severity_table = Table(severity_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        severity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(severity_table)
        story.append(Spacer(1, 0.3 * inch))

        # Vulnerabilities Details
        if vulnerabilities:
            story.append(PageBreak())
            story.append(Paragraph("Vulnerability Details", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.2 * inch))

            for idx, vuln in enumerate(vulnerabilities, 1):
                # Vulnerability header
                vuln_title = f"{idx}. {vuln.get('name', 'Unknown')} [{vuln.get('severity', 'Unknown').upper()}]"
                story.append(Paragraph(vuln_title, self.styles['Heading3']))

                # Vulnerability details
                details = [
                    f"<b>URL:</b> {vuln.get('url', 'N/A')}",
                    f"<b>Severity:</b> {vuln.get('severity', 'N/A').upper()}",
                    f"<b>CVSS Score:</b> {vuln.get('cvss_score', 'N/A')}",
                    f"<b>CWE ID:</b> {vuln.get('cwe_id', 'N/A')}",
                    f"<b>Description:</b> {vuln.get('description', 'N/A')}",
                    f"<b>Remediation:</b> {vuln.get('remediation', 'No remediation provided')}"
                ]

                for detail in details:
                    story.append(Paragraph(detail, self.styles['Normal']))
                    story.append(Spacer(1, 0.05 * inch))

                story.append(Spacer(1, 0.2 * inch))

        # Build PDF
        doc.build(story)

        return filepath

    def _calculate_percentage(self, count: int, total: int) -> float:
        """Calculate percentage"""
        if total == 0:
            return 0.0
        return round((count / total) * 100, 1)
