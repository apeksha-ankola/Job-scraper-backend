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
def generate_cover_letter(name, job_position, company_name, email, linkedin, github, phone):
    cover_letter_prompt = f"""Write a concise and professional cover letter for {name} applying to a {job_position} position at {company_name}. 
    Include their email: {email}, phone: {phone}, LinkedIn: {linkedin}, and GitHub: {github}. 
    Keep it in plain text."""
    
    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": cover_letter_prompt}],
    )
    cover_letter = response.choices[0].message.content

    # Save the cover letter as a PDF and return the file path
    pdf_path = save_to_pdf(cover_letter, "Generated Cover Letter", "cover_letter.pdf")
    return pdf_path

# Generate Resume
def generate_resume(name, job_position, github, email, linkedin, phone):
    resume_prompt = f"""Write a resume for {name} applying for a {job_position} position. Include their email: {email}, Github: {github},Phone: {phone} and LinkedIn: {linkedin}. 
    Highlight relevant skills, experience, and achievements for the job."""
    
    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": resume_prompt}],
    )
    resume = response.choices[0].message.content

    # Save the resume as a PDF and return the file path
    pdf_path = save_to_pdf(resume, "Generated Resume", "resume.pdf")
    return pdf_path
