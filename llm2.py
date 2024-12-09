import os
from fpdf import FPDF
from dotenv import load_dotenv
from together import Together
from langchain import PromptTemplate

# Load environment variables
load_dotenv()

# Together.ai API setup
sec_key = os.getenv("TOGETHER_ACCESS_TOKEN")
client = Together(api_key=sec_key)

# PDF Helper
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font("Times", size=12)

    def add_content(self, title, text):
        self.set_font("Times", style="B", size=16)
        self.cell(0, 10, title, ln=True, align="C")
        self.ln(10)
        self.set_font("Times", size=12)
        self.multi_cell(0, 10, text)

def save_to_pdf(content, title, file_name):
    pdf = PDF()
    pdf.add_content(title, content)
    pdf.output(file_name)
    return file_name

# Generate Cover Letter
def generate_cover_letter(name, company_name, job_position):
    prompt = PromptTemplate(
        input_variables=["name", "company_name", "job_position"],
        template=("Write a professional cover letter for {name} applying to a {job_position} "
                  "position at {company_name}. Ensure it's concise and plain text.")
    )
    formatted_prompt = prompt.format(name=name, company_name=company_name, job_position=job_position)
    
    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": formatted_prompt}],
    )
    cover_letter = response.choices[0].message.content

    # Save the cover letter as a PDF and return the file path
    pdf_path = save_to_pdf(cover_letter, "Generated Cover Letter", "cover_letter.pdf")
    return pdf_path

# Generate Resume
def generate_resume(name, job_position):
    resume_prompt = f"""Write a comprehensive resume for {name} applying for a {job_position} position.
    Use specific keywords and formatting that maximize the chances of the resume being shortlisted.
    Include relevant skills, experience, and achievements that showcase the candidate's suitability for the role."""
    
    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": resume_prompt}],
    )
    resume = response.choices[0].message.content

    # Save the resume as a PDF and return the file path
    pdf_path = save_to_pdf(resume, "Generated Resume", "resume.pdf")
    return pdf_path