from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
def get_jobs_indeed(job_query):
    # Initialize the driver
    driver = webdriver.Chrome()

    # Open the URL (Ensure the URL matches your target search)
    job_query = '+'.join(job_query.split())
    url = f"https://in.indeed.com/jobs?q={job_query}"
    driver.get(url)

    data = []

    # Wait for the job listings to load
    wait = WebDriverWait(driver, 10)
    job_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "job_seen_beacon")))

    # Loop through job listings
    for job_card in job_cards:
        job_data = {
            "Job Title": None, 
            "Company": None,
            "Location": None,
            "Salary": None,  
            "Summary": None,
            "Link_To_Apply": None,
            "Platform":"Internshala",
        }
        try:
            # Job Title
            title = job_card.find_element(By.CSS_SELECTOR, "h2.jobTitle").text
            link = job_card.find_element(By.CSS_SELECTOR, "h2.jobTitle a").get_attribute("href")
            job_data['Job Title'] = title
            job_data['Link_To_Apply'] = link
        except:
            job_data['Job Title'] = None
            job_data['Link_To_Apply'] = None

        try:
            # Company Name
            company = job_card.find_element(By.CSS_SELECTOR, '[data-testid="company-name"]').text
            job_data['Company'] = company
        except:
            job_data['Company'] = None

        try:
            # Job Location
            location = job_card.find_element(By.CSS_SELECTOR, '[data-testid="text-location"]').text
            job_data['Location'] = location
        except:
            job_data['Location'] = None

        try:
            salary = job_card.find_element(By.CLASS_NAME, "salary-snippet").text
            job_data['Salary'] = salary
        except:
            job_data['Salary'] = None

        try:
            # Job Summary
            summary = job_card.find_element(By.CSS_SELECTOR, 'div.underShelfFooter div div').text
            job_data['Summary'] = summary
        except:
            job_data['Summary'] = None
        
        data.append(job_data)

    # Close the browser
    driver.quit()

    return data

def get_jobs_naukri(job_query):
    try:
        # Initialize the Firefox driver
        driver = webdriver.Firefox()

        # Open the Naukri website
        url = 'https://www.naukri.com'
        driver.get(url)
        
        # Wait for the search input field and enter the job query
        wait = WebDriverWait(driver, 5)
        input_search = wait.until(EC.presence_of_element_located((
            By.XPATH, "/html/body/div[1]/div[7]/div/div/div[1]/div/div/div/div[1]/div/input"
        )))
        input_search.send_keys(job_query)

        # Click the search button
        search_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, '/html/body/div[1]/div[7]/div/div/div[6]'
        )))
        search_button.click()

        # Wait for the job listings to load
        # time.sleep(10)  # Adjust this if necessary

        # Locate job listing elements
        job_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "srp-jobtuple-wrapper")))

        data = []

        for job_card in job_cards:
            job_data = {
                "Job Title": None, 
                "Company": None,
                "Location": None,
                "Salary": None,  
                "Summary": None,
                "Link_To_Apply": None,
                "Platform":"Internshala",
            }       
            try:
                # Locate the <a> tag with class "title"
                element = job_card.find_element(By.CLASS_NAME, "title")
                # Extract the href attribute
                title = element.get_attribute("title")
                href = element.get_attribute("href")
                job_data['Job Title'] = title
                job_data['Link_To_Apply'] = href

            except:
                job_data['Job Title'] = None
                job_data['Link_To_Apply'] = None
            
            try:
                # locate Company a tag
                element = job_card.find_element(By.CLASS_NAME, "comp-name")
                # Extract the href attribute
                company = element.get_attribute("title")
                job_data['Company'] = company

            except:
                job_data['Company'] = None
            
            try:
                # Company
                element = job_card.find_element(By.CLASS_NAME, "locWdth")
                location = element.get_attribute("title")
                job_data['Location'] = location
            except:
                job_data['Location'] = None
            
            try:
                # Salary
                parent_span = job_card.find_element(By.CLASS_NAME, "ni-job-tuple-icon-srp-rupee")
                child_span = parent_span.find_element(By.TAG_NAME, "span")
                salary = child_span.get_attribute("title")
                job_data['Salary'] = salary
            except:
                job_data['Salary'] = None
            
            try:
                summary = job_card.find_element(By.CLASS_NAME, "job-desc").text
                job_data['Summary'] = summary
            except:
                job_data['Summary'] = None
            
            data.append(job_data)

        # Close the browser
        driver.quit()

        return data
    
    except Exception as e:
        print(f"An error occurred: {e}")

def get_job_details(job_link):
    job_url = 'https://internshala.com' + job_link
    webpage = requests.get(job_url)
    soup = BeautifulSoup(webpage.content, 'html.parser')

    job_data = {
        "Job Title": None, 
        "Company": None,
        "Location": None,
        "Salary": None,  
        "Summary": None,
        "Link_To_Apply": None,
        "Platform":"Internshala",
    }

    # Extracting the role
    role_div = soup.find('div', class_='profile')
    job_data['Job Title'] = role_div.text.strip() if role_div else None

    # Extracting the company
    company_div = soup.find('div', class_='company_name')
    job_data['Company'] = company_div.find('a').get_text(strip=True) if company_div and company_div.find('a') else None

    location_p_tag = soup.find('p', id='location_names')
    location_span = location_p_tag.find('span') if location_p_tag else None
    job_data['Location'] = location_span.find('a').get_text() if location_span and location_span.find('a') else None
    
    # Extracting the stipend
    stipend_span = soup.find('span', class_='stipend')
    job_data['Salary'] = stipend_span.text if stipend_span else None

    # Extracting the summary
    about = soup.find('h2', class_='about_heading')
    job_data['Summary'] = about.find_next('div').get_text() if about and about.find_next('div') else None

    # Extracting the link to apply
    job_data['Link_To_Apply'] = 'https://internshala.com' + job_link

    return job_data

def get_jobs_internshala (internship_query,job_type):
    # Convert the search query into URL format
    query = internship_query.replace(" ", "%20")

    # Get the search results page
    URL = f"https://internshala.com/{job_type}/keywords-" + query
    webpage = requests.get(URL)
    soup = BeautifulSoup(webpage.content, 'html.parser')

    jobs = soup.find_all('a', class_='job-title-href')

    job_links = [job['href'] for job in jobs]

    # If no internships found, return an empty list with a message
    if not job_links:
        return []
    
    total_jobs = min(20, len(job_links))  # Limit the number of jobs to 20
    data = []

    for i in range(total_jobs):
        data.append(get_job_details(job_links[i]))

    return data
