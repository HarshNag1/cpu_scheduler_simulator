from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import matplotlib.pyplot as plt
from datetime import datetime

class PDFGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def generate_report(self, algorithm, processes, timeline, gantt_chart, metrics):
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"CPU_Schedule_{algorithm}_{timestamp}.pdf")
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph(f"CPU Scheduling Report - {algorithm}", title_style))
        elements.append(Spacer(1, 20))
        
        # Process Table
        process_data = [['Process ID', 'Arrival Time', 'Burst Time', 'Priority',
                        'Start Time', 'Completion Time', 'Waiting Time', 'Turnaround Time']]
                        
        for p in processes:
            process_data.append([
                f'P{p.pid}',
                str(p.arrival_time),
                str(p.burst_time),
                str(p.priority),
                str(p.start_time if p.start_time is not None else '-'),
                str(p.completion_time if p.completion_time is not None else '-'),
                f'{p.waiting_time:.2f}',
                f'{p.turnaround_time:.2f}'
            ])
            
        table = Table(process_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Metrics
        elements.append(Paragraph("Performance Metrics:", styles['Heading2']))
        elements.append(Spacer(1, 10))
        metrics_style = ParagraphStyle(
            'Metrics',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20
        )
        elements.append(Paragraph(metrics, metrics_style))
        elements.append(Spacer(1, 20))
        
        # Save Gantt chart as temporary image
        temp_image = os.path.join(self.output_dir, f"temp_gantt_{timestamp}.png")
        gantt_chart.figure.savefig(temp_image, bbox_inches='tight', dpi=300)
        
        # Add Gantt chart
        elements.append(Paragraph("Gantt Chart:", styles['Heading2']))
        elements.append(Spacer(1, 10))
        elements.append(Image(temp_image, width=9*inch, height=4*inch))
        
        # Build PDF
        doc.build(elements)
        
        # Clean up temporary image
        os.remove(temp_image)
        
        return filename
