"""StartupOS AI — Report Compiler Agent

Aggregates all 7 agent outputs into a structured report.
Generates PDF using ReportLab.
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ReportCompiler:
    """Compiles all agent outputs into a downloadable report."""

    def compile_json(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compile all agent outputs into a structured JSON report."""
        report = {
            "title": "StartupOS AI — Business Plan Report",
            "generated_by": "StartupOS AI Multi-Agent System",
            "sections": []
        }

        section_map = {
            "ceo_output": {"title": "1. Executive Summary", "icon": "🎯"},
            "research_output": {"title": "2. Market Research Report", "icon": "🔍"},
            "marketing_output": {"title": "3. Marketing Strategy", "icon": "📣"},
            "developer_output": {"title": "4. Technical Roadmap", "icon": "💻"},
            "finance_output": {"title": "5. Financial Projections", "icon": "💰"},
            "analytics_output": {"title": "6. KPI Framework", "icon": "📊"},
            "operations_output": {"title": "7. Operations Checklist", "icon": "⚙️"},
        }

        for key, meta in section_map.items():
            if key in context and context[key]:
                report["sections"].append({
                    "title": meta["title"],
                    "icon": meta["icon"],
                    "content": context[key],
                })

        return report

    def generate_pdf(self, report: Dict[str, Any], output_path: str) -> str:
        """Generate a PDF from the compiled report using ReportLab."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.colors import HexColor
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                    topMargin=0.75*inch, bottomMargin=0.75*inch)

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle', parent=styles['Title'],
                fontSize=24, spaceAfter=30,
                textColor=HexColor('#1a1a2e')
            )
            heading_style = ParagraphStyle(
                'CustomHeading', parent=styles['Heading1'],
                fontSize=16, spaceAfter=12, spaceBefore=20,
                textColor=HexColor('#16213e')
            )
            body_style = ParagraphStyle(
                'CustomBody', parent=styles['Normal'],
                fontSize=11, spaceAfter=8, leading=16,
            )

            elements = []

            # Title
            elements.append(Paragraph(report.get("title", "Business Plan"), title_style))
            elements.append(Spacer(1, 20))

            # Sections
            for section in report.get("sections", []):
                elements.append(Paragraph(
                    f"{section['icon']} {section['title']}", heading_style
                ))

                content = section.get("content", {})
                if isinstance(content, dict):
                    for key, value in content.items():
                        label = key.replace("_", " ").title()
                        if isinstance(value, str):
                            elements.append(Paragraph(
                                f"<b>{label}:</b> {value}", body_style
                            ))
                        elif isinstance(value, list):
                            elements.append(Paragraph(f"<b>{label}:</b>", body_style))
                            for item in value:
                                if isinstance(item, str):
                                    elements.append(Paragraph(f"  • {item}", body_style))
                                elif isinstance(item, dict):
                                    summary = ", ".join(f"{k}: {v}" for k, v in item.items() if isinstance(v, str))
                                    elements.append(Paragraph(f"  • {summary}", body_style))
                        elif isinstance(value, dict):
                            elements.append(Paragraph(f"<b>{label}:</b>", body_style))
                            for k, v in value.items():
                                elements.append(Paragraph(
                                    f"  {k.replace('_', ' ').title()}: {v}", body_style
                                ))

                elements.append(Spacer(1, 15))

            doc.build(elements)
            logger.info(f"PDF generated: {output_path}")
            return output_path

        except ImportError:
            logger.warning("ReportLab not installed, saving as JSON instead")
            json_path = output_path.replace(".pdf", ".json")
            with open(json_path, "w") as f:
                json.dump(report, f, indent=2)
            return json_path
