from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def get_jobs_indeed(job_query):
    # Initialize the driver
    driver = webdriver.Chrome()

    # Open the URL (Ensure the URL matches your target search)
    job_query = '+'.join(job_query.split())
    url = f"https://in.indeed.com/jobs?q={job_query}"
    driver.get(url)

    # Extract job listing elements
    job_titles = []
    link_to_apply=[]
    companies = []
    locations = []
    salaries = []
    summaries = []

    # Wait for the job listings to load
    wait = WebDriverWait(driver, 10)
    job_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "job_seen_beacon")))

    # Loop through job listings
    for job_card in job_cards:
        try:
            # Job Title
            title = job_card.find_element(By.CSS_SELECTOR, "h2.jobTitle").text
            link = job_card.find_element(By.CSS_SELECTOR, "h2.jobTitle a").get_attribute("href")
            job_titles.append(title)
            link_to_apply.append(link)
        except:
            job_titles.append(None)
            link_to_apply.append(None)

        try:
            # Company Name
            company = job_card.find_element(By.CSS_SELECTOR, '[data-testid="company-name"]').text
            companies.append(company)
        except:
            companies.append(None)

        try:
            # Job Location
            location = job_card.find_element(By.CSS_SELECTOR, '[data-testid="text-location"]').text
            locations.append(location)
        except:
            locations.append(None)

        try:
            # Salary (if available)
            salary = job_card.find_element(By.CLASS_NAME, "salary-snippet").text
            salaries.append(salary)
        except:
            salaries.append(None)

        try:
            # Job Summary
            summary = job_card.find_element(By.CSS_SELECTOR, 'div.underShelfFooter div div').text
            summaries.append(summary)
        except:
            summaries.append(None)
        

    # Close the browser
    driver.quit()

    # Create a pandas DataFrame
    data = {
        "Job Title": job_titles,
        "Company": companies,
        "Location": locations,
        "Salary": salaries,
        "Summary": summaries,
        "Link_To_Apply":link_to_apply,
        "Platform":"Indeed",
    }

    df = pd.DataFrame(data)
    return df

def get_jobs_naukri(job_query):
    try:
        # Initialize the Firefox driver
        driver = webdriver.Firefox()

        # Open the Naukri website
        url = 'https://www.naukri.com'
        driver.get(url)
        
        # Wait for the search input field and enter the job query
        wait = WebDriverWait(driver, 20)
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
        time.sleep(10)  # Adjust this if necessary

        # Extract job details
        job_titles = []
        link_to_apply=[]
        companies = []
        locations = []
        salaries = []
        summaries = []

        # Locate job listing elements
        job_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "srp-jobtuple-wrapper")))

        for job_card in job_cards:
                       
            try:
                # Locate the <a> tag with class "title"
                element = job_card.find_element(By.CLASS_NAME, "title")
                # Extract the href attribute
                title = element.get_attribute("title")
                href = element.get_attribute("href")
                job_titles.append(title)
                link_to_apply.append(href)

            except:
                job_titles.append(None)
                link_to_apply.append(None)
            
            try:
                # locate Company a tag
                element = job_card.find_element(By.CLASS_NAME, "comp-name")
                # Extract the href attribute
                company = element.get_attribute("title")
                companies.append(company)

            except:
                companies.append(None)
            
            try:
                # Company
                element = job_card.find_element(By.CLASS_NAME, "locWdth")
                location = element.get_attribute("title")
                locations.append(location)

            except:
                locations.append(None)
            
            try:
                # Salary
                parent_span = job_card.find_element(By.CLASS_NAME, "ni-job-tuple-icon-srp-rupee")
                child_span = parent_span.find_element(By.TAG_NAME, "span")
                salary = child_span.get_attribute("title")
                salaries.append(salary)
            except:
                salaries.append(None)
            
            try:
                summary = job_card.find_element(By.CLASS_NAME, "job-desc").text
                summaries.append(summary)
            except:
                summaries.append(None)

        # Close the browser
        driver.quit()

        # Create a pandas DataFrame
        data = {
            "Job Title": job_titles,
            "Company": companies,
            "Location": locations,
            "Salary": salaries,
            "Summary": summaries,
            "Link_To_Apply":link_to_apply,
            "Platform":"Naukri",
        }

        df = pd.DataFrame(data)

        return df
    except Exception as e:
        print(f"An error occurred: {e}")

def get_jobs(query):
    #query = "Machine Learning"
    df_indeed = get_jobs_indeed(query)
    df_naukri = get_jobs_naukri(query)

    df_jobs = pd.concat([df_indeed, df_naukri], ignore_index=True)
    jobs_json = df_jobs.to_dict(orient="records")
    return jobs_json
