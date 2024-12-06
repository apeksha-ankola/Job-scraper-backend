from bs4 import BeautifulSoup
import requests

def get_internship_details(internship_link):
    internship_url = 'https://internshala.com' + internship_link
    webpage = requests.get(internship_url)
    soup = BeautifulSoup(webpage.content, 'html.parser')

    internship_data = {
        "role": None, 
        "company": None, 
        "stipend": None, 
        "skills": [], 
        "link_to_apply": None
    }

    # Extracting the role
    role_div = soup.find('div', class_='profile')
    internship_data['role'] = role_div.text.strip() if role_div else None

    # Extracting the company
    company_div = soup.find('div', class_='company_and_premium')
    internship_data['company'] = company_div.find('a').get_text(strip=True) if company_div and company_div.find('a') else None

    # Extracting the stipend
    stipend_span = soup.find('span', class_='stipend')
    internship_data['stipend'] = stipend_span.text if stipend_span else None

    # Extracting the skills
    skill_container = soup.find('div', class_='round_tabs_container')
    if skill_container:
        skills_list = skill_container.find_all('span', class_='round_tabs')
        internship_data['skills'] = [skill.get_text(strip=True) for skill in skills_list]
    else:
        internship_data['skills'] = None

    # Extracting the link to apply
    apply_button = soup.find('button', string=lambda text: text and "Apply now" in text)
    internship_data['link_to_apply'] = 'https://internshala.com' + apply_button.find_parent('a')['href'] if apply_button and apply_button.find_parent('a') else None

    return internship_data

def get_internships(internship_query):
    # Convert the search query into URL format
    query = internship_query.replace(" ", "%20")

    # Get the search results page
    URL = 'https://internshala.com/internships/keywords-' + query
    webpage = requests.get(URL)
    soup = BeautifulSoup(webpage.content, 'html.parser')

    internships = soup.find_all('a', class_='job-title-href')

    internship_links = [internship['href'] for internship in internships]

    # If no internships found, return an empty list with a message "Internship not found"
    if not internship_links:
        return {"message": "Internships not found", "data": []}
    
    total_internships = min(20, len(internship_links))  # Limit the number of internships to 20
    data = []

    for i in range(total_internships):
        data.append(get_internship_details(internship_links[i]))

    return data
