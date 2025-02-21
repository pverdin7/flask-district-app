from flask import Flask, render_template, request, send_file
import requests
import io
from docx import Document

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Function to fetch school district/university data
def get_district_data(name, location):
    search_query = f"{name} {location} school district site:.gov OR site:.edu"
    search_url = f"https://www.googleapis.com/customsearch/v1?q={search_query}&key=AIzaSyDkW3m1DdVfHbqirYNRa2eSna1ZSG3BY_o&cx=77cbed915d0c641b3"
    response = requests.get(search_url)
    if response.status_code == 200:
        results = response.json().get("items", [])
        if results:
            return results[0]['link']
    return "No data found"

# Function to create Word document
def create_word_doc(data):
    doc = Document()
    doc.add_heading('School District Report', level=1)
    for key, value in data.items():
        doc.add_paragraph(f"{key}: {value}")
    
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        district_name = request.form['district_name']
        location = request.form['location']
        data = {
            "District Name": district_name,
            "Location": location,
            "Website": get_district_data(district_name, location)
        }
        return render_template("index.html", data=data)  # RESTORE TEMPLATE RENDERING
    
    return render_template("index.html")  # RESTORE TEMPLATE RENDERING


@app.route('/export', methods=['POST'])
def export():
    data = {
        "District Name": request.form['district_name'],
        "Location": request.form['location'],
        "Website": request.form['website']
    }
    file_stream = create_word_doc(data)
    return send_file(file_stream, as_attachment=True, download_name="district_report.docx", mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@app.route('/test')
def test():
    return "Flask is running correctly!"

@app.route('/debug-templates')
def debug_templates():
    import os
    template_path = os.path.join(app.template_folder, "index.html")
    return f"Flask is looking for: {template_path}. Exists: {os.path.exists(template_path)}"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10000)
