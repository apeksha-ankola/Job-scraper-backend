from scraper import get_jobs_indeed, get_jobs_naukri, get_jobs_internshala
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

def filter_jobs(job_list):
    filtered_list = []
    for job in job_list:
        job_title = job.get("Job Title", "")
        # Check if any word in the Job Title starts with "intern" (case insensitive)
        if not any(word.lower().startswith("intern") for word in job_title.split()):
            filtered_list.append(job)
    return filtered_list

from concurrent.futures import ThreadPoolExecutor

def get_jobs(query):
    # Helper function to wrap get_jobs_internshala with the additional argument
    def internshala_wrapper(query):
        return get_jobs_internshala(query, "jobs")
    
    # Use ThreadPoolExecutor to run the functions in parallel
    with ThreadPoolExecutor() as executor:
        # Submit all jobs to the executor
        future_indeed = executor.submit(get_jobs_indeed, query)
        future_naukri = executor.submit(get_jobs_naukri, query)
        future_internshala = executor.submit(internshala_wrapper, query)

        # Collect the results, ensuring that None is replaced with an empty list
        jobs_indeed = future_indeed.result() or []
        jobs_naukri = future_naukri.result() or []
        jobs_internshala = future_internshala.result() or []
    
    # Combine the results
    combined_jobs = jobs_indeed + jobs_naukri + jobs_internshala
    filtered_jobs = filter_jobs(combined_jobs)
    
    return filtered_jobs


def filter_internships(job_list):
    filtered_list = []
    for job in job_list:
        job_title = job.get("Job Title", "")
        platform = job.get("Platform", "").lower()  
        if platform == "internshala" or any(word.lower().startswith("intern") for word in job_title.split()):
            filtered_list.append(job)
    return filtered_list

def get_internships(query):
    query = query + " intern"
    # Helper function to wrap get_jobs_internshala with the additional argument
    def internshala_wrapper(query):
        return get_jobs_internshala(query, "internships")
    
    # Use ThreadPoolExecutor to run the functions in parallel
    with ThreadPoolExecutor() as executor:
        # Submit all jobs to the executor
        future_indeed = executor.submit(get_jobs_indeed, query)
        future_naukri = executor.submit(get_jobs_naukri, query)
        future_internshala = executor.submit(internshala_wrapper, query)

        # Collect the results
        jobs_indeed = future_indeed.result()
        jobs_naukri = future_naukri.result()
        jobs_internshala = future_internshala.result()
    
    # Combine the results
    combined_jobs = jobs_indeed + jobs_naukri + jobs_internshala
    filtered_jobs = filter_internships(combined_jobs) 
    return filtered_jobs

# print(get_internships("Machine Learning"))
# print(get_jobs("Machine Learning"))