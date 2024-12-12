import os
from fpdf import FPDF
from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint

# Load environment variables
load_dotenv()

# HuggingFace setup
sec_key = os.getenv("HUGGINGFACE_TOKEN")
os.environ["huggingface"] = sec_key
print(sec_key)
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
llm = HuggingFaceEndpoint(repo_id=repo_id, max_length=400, temperature=0.5, top_p=0.9, token=sec_key)

# PDF Helper
def save_to_pdf(content, title, file_name):
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
    print("cover letter")
    cover_letter = llm.invoke(formatted_prompt)
    pdf_path = save_to_pdf(cover_letter, "Generated Cover Letter", "cover_letter.pdf")
    return pdf_path

# Generate Resume
def generate_resume(name, job_position):
    resume_prompt = f"""Write a comprehensive resume for {name} applying for a {job_position} position.
    Use specific keywords and formatting that maximize the chances of the resume being shortlisted.
    Include relevant skills, experience, and achievements that showcase the candidate's suitability for the role."""
    print("resume")
    resume = llm.invoke(resume_prompt)
    
    pdf_path = save_to_pdf(resume, "Generated Resume", "resume.pdf")
    return pdf_path

#End
