import os
import statistics
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from jinja2 import Environment, FileSystemLoader
import pdfkit


# Load Jinja2 template
TEMPLATES_DIR = "app/templates"
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
template = env.get_template("index.html")

# Directory to save PDFs
PDF_DIR = "output"
os.makedirs(PDF_DIR, exist_ok=True)


def calculate_statistics(data):
    """Calculate statistics for transactions safely."""
    if not data:
        return []
    
    transactions = []
    
    # Dashboard Load Time Statistics
    dashboard_load_times = [user.get('dashboard_load_time', 0) for user in data]
    if dashboard_load_times:
        transactions.append({
            "name": "Dashboard Load Time",
            "minimum": round(min(dashboard_load_times), 3),
            "average": round(statistics.mean(dashboard_load_times), 3),
            "maximum": round(max(dashboard_load_times), 3),
            "std_deviation": round(statistics.stdev(dashboard_load_times), 3) if len(dashboard_load_times) > 1 else 0,
            "percentile_90": round(statistics.quantiles(dashboard_load_times, n=10)[8], 3)
                if len(dashboard_load_times) >= 10 else max(dashboard_load_times)
        })
    
    # Visual Load Times Statistics (expects a dict)
    if 'visual_load_times' in data[0] and isinstance(data[0]['visual_load_times'], dict):
        for key in data[0]['visual_load_times'].keys():
            values = [user.get('visual_load_times', {}).get(key, 0) for user in data]
            transactions.append({
                "name": key,
                "minimum": round(min(values), 3),
                "average": round(statistics.mean(values), 3),
                "maximum": round(max(values), 3),
                "std_deviation": round(statistics.stdev(values), 3) if len(values) > 1 else 0,
                "percentile_90": round(statistics.quantiles(values, n=10)[8], 3)
                    if len(values) >= 10 else max(values)
            })
    
    # Filter Apply Times Statistics:
    # Handle both 'filter_apply_times' (plural) and 'filter_apply_time' (singular)
    if 'filter_apply_time' in data[0]:
        # If it's a dict, iterate over keys
        if isinstance(data[0]['filter_apply_time'], dict):
            for key in data[0]['filter_apply_time'].keys():
                values = [user.get('filter_apply_time', {}).get(key, 0) for user in data]
                transactions.append({
                    "name": key,
                    "minimum": round(min(values), 3),
                    "average": round(statistics.mean(values), 3),
                    "maximum": round(max(values), 3),
                    "std_deviation": round(statistics.stdev(values), 3) if len(values) > 1 else 0,
                    "percentile_90": round(statistics.quantiles(values, n=10)[8], 3)
                        if len(values) >= 10 else max(values)
                })
        else:
            # Otherwise, treat it as a single numeric metric across all objects
            values = [user.get('filter_apply_time', 0) for user in data]
            transactions.append({
                "name": "Filter Apply Time",
                "minimum": round(min(values), 3),
                "average": round(statistics.mean(values), 3),
                "maximum": round(max(values), 3),
                "std_deviation": round(statistics.stdev(values), 3) if len(values) > 1 else 0,
                "percentile_90": round(statistics.quantiles(values, n=10)[8], 3)
                    if len(values) >= 10 else max(values)
            })
    elif 'filter_apply_time' in data[0]:
        # Handle the singular key similarly
        if isinstance(data[0]['filter_apply_time'], dict):
            for key in data[0]['filter_apply_time'].keys():
                values = [user.get('filter_apply_time', {}).get(key, 0) for user in data]
                transactions.append({
                    "name": key,
                    "minimum": round(min(values), 3),
                    "average": round(statistics.mean(values), 3),
                    "maximum": round(max(values), 3),
                    "std_deviation": round(statistics.stdev(values), 3) if len(values) > 1 else 0,
                    "percentile_90": round(statistics.quantiles(values, n=10)[8], 3)
                        if len(values) >= 10 else max(values)
                })
        else:
            values = [user.get('filter_apply_time', 0) for user in data]
            transactions.append({
                "name": "Filter Apply Time",
                "minimum": round(min(values), 3),
                "average": round(statistics.mean(values), 3),
                "maximum": round(max(values), 3),
                "std_deviation": round(statistics.stdev(values), 3) if len(values) > 1 else 0,
                "percentile_90": round(statistics.quantiles(values, n=10)[8], 3)
                    if len(values) >= 10 else max(values)
            })
    
    return transactions




config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

def render_template_to_pdf(template_name, context):
    """Render an HTML template and convert it into a PDF"""

    
    rendered_html = template.render(context)

    # Save the rendered HTML to a file (optional, for debugging)
    html_filename = "transaction_summary.html"
    html_path = os.path.join(PDF_DIR, html_filename)
    with open(html_path, "w") as html_file:
        html_file.write(rendered_html)

    
    pdf_filename = "transaction_summary.pdf"
    pdf_path = os.path.join(PDF_DIR, pdf_filename)
    options = {
        'enable-local-file-access': '', 
    }
    pdfkit.from_file(html_path, pdf_path, configuration=config, options=options)

    return pdf_path