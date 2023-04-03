from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sendEmail import sendMessage
import logging

import pathlib
import os
import time
import re
import unicodedata
import chromedriver_binary # Adds chromedriver binary to path

ROOT_DIR = os.path.abspath(os.curdir)
SCRAPED_DATA_DIR = ROOT_DIR + '/DATA'
TEMP_DOWNLOAD_PATH = ROOT_DIR + r'\TEMP_DIR\\'
LOGS_DIR = ROOT_DIR + '/logs/run.log'
MUST_CONTAIN_IN_PDF_URL = 'FileServeServlet?TYPE=REPORT'

logging.basicConfig(filename=LOGS_DIR,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

# Create folder for pdf download temp dir
pathlib.Path(TEMP_DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True) 

# prefs = {"plugins.always_open_pdf_externally": True }
prefs = {
            "download.default_directory" : TEMP_DOWNLOAD_PATH,
            "plugins.always_open_pdf_externally": True,
            "directory_upgrade": True
        }
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chrome_options)

wait = WebDriverWait(driver, 10)

url = 'https://greenfield.matrixcare.com'

driver.get(url)

def login():
        
    logging.info("Logging in...")
    username_field = driver.find_element(By.XPATH, '/html/body/form/div/div/main/div[1]/div/div[3]/div/input')
    username_field.send_keys("it7269")

    password_field = driver.find_element(By.XPATH, '/html/body/form/div/div/main/div[1]/div/div[4]/div/input')
    password_field.send_keys("Welcome+1937")

    password_field.send_keys(Keys.ENTER)

def facilities():

    logging.info("Search all facilities...")
    facility_menu = driver.find_element(By.XPATH, '/html/body/div[1]/nav[2]/div/div[2]/ul/li[7]/a')
    facility_menu.click()

    search_facility_menu = driver.find_element(By.XPATH, '/html/body/div[1]/nav[2]/div/div[2]/ul/li[7]/ul/div/div/li/ul/li[1]/a')
    search_facility_menu.click()

    search_all_facility_button = driver.find_element(By.XPATH, '/html/body/div[1]/main/form/div[1]/fieldset/div[3]/input')
    search_all_facility_button.click()

    facility_table = driver.find_element(By.XPATH, '//*[@id="facilitySearchList"]')
    logging.info("Looping through facilities...")
    for row in facility_table.find_elements(By.XPATH, './/tbody/tr'):
        
        facility_name_href = row.find_element(By.XPATH, './/td[1]/a')
        facility_name_href.send_keys(Keys.CONTROL + Keys.ENTER)

        facility_name = facility_name_href.get_attribute('text')

        # Create folder for each facility
        logging.info("Folder for facility " + facility_name + " created.")
        pathlib.Path(SCRAPED_DATA_DIR + '\\FACILITIES\\' + facility_name).mkdir(parents=True, exist_ok=True) 

        driver.switch_to.window(driver.window_handles[1])

        residents(facility_name)

def residents(facility_name):
    
    resident_menu = driver.find_element(By.XPATH, '/html/body/div[1]/nav[2]/div/div[2]/ul/li[3]/a')
    resident_menu.click()

    search_resident_menu = driver.find_element(By.XPATH, '/html/body/div[1]/nav[2]/div/div[2]/ul/li[3]/ul/div/div/li/ul/li[1]/a')
    search_resident_menu.click()

    search_all_resident = driver.find_element(By.XPATH, '/html/body/div[1]/main/form/fieldset[7]/section/input')
    search_all_resident.click()

    resident_table = driver.find_element(By.XPATH, '//*[@id="patientList"]/table')
    
    logging.info("Looping through residents...")

    for row in resident_table.find_elements(By.XPATH, './/tbody/tr'):

        resident_name_href = row.find_element(By.XPATH, './/td[1]/a')
        resident_id_td = row.find_element(By.XPATH, './/td[2]')

        resident_name = resident_name_href.get_attribute('text')
        resident_id = resident_id_td.get_attribute("innerHTML")
        
        facility_dir = SCRAPED_DATA_DIR + '\\FACILITIES\\' + facility_name + '\\'
        #pathlib.Path(SCRAPED_DATA_DIR + '\\FACILITIES\\' + facility_name + '\\' + resident_name).mkdir(parents=True, exist_ok=True) 

        fileToCheck = facility_dir + slugify(resident_name + "_" + resident_id) + '.pdf'
        isExisting = os.path.exists(fileToCheck)
        
        if isExisting:
            logging.info('File already exist: ' + fileToCheck)
            continue

        logging.info('File moved to: ' + fileToCheck)

        resident_name_href.send_keys(Keys.CONTROL + Keys.ENTER)

        driver.switch_to.window(driver.window_handles[2])

        logging.info("Navigating to Resident Reports...")
        resident_menu = driver.find_element(By.XPATH, '/html/body/div[1]/nav[2]/div/div[2]/ul/li[3]/a')
        resident_menu.click()

        resident_menu_reports = driver.find_element(By.XPATH, '/html/body/div[1]/nav[2]/div/div[2]/ul/li[3]/ul/div/div/li/ul/li[20]/a')
        resident_menu_reports.click()

        logging.info("Selecting Event Detail Report...")
        event_detail_list_radio = driver.find_element(By.XPATH, '/html/body/div[1]/form/table[1]/tbody/tr/td[1]/table[4]/tbody/tr[2]/td/input')
        event_detail_list_radio.click()

        time.sleep(2)

        logging.info("Clicking Next Button for Event Detail Report...")
        
        next_button = driver.find_element(By.XPATH, '/html/body/div[1]/form/table[2]/tbody/tr/td/table/tbody/tr/td/input')
        
        next_button.click()

        residents_event_summary_list("01/01/2010", facility_dir, resident_name + "_" + resident_id)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

def residents_event_summary_list(start_date_value, facility_dir, resident_name_id):

    logging.info("Entering Startdate for Date Picker...")
    start_date_picker = driver.find_element(By.XPATH, '/html/body/div[1]/form/table/tbody/tr[4]/td[2]/input')
    start_date_picker.send_keys(Keys.CONTROL + 'a')
    start_date_picker.send_keys(start_date_value)

    # Click the link which opens in a new window
    logging.info("Clicking Report Button...")
    report_button = driver.find_element(By.XPATH, '/html/body/div[1]/form/div[3]/input[2]')
    report_button.click()

    logging.info("Waiting for popup...")
    wait.until(EC.new_window_is_opened(driver.window_handles))
    logging.info("Switch focus to popup...")
    driver.switch_to.window(driver.window_handles[-1])

    logging.info("Giving extra time for download to initiate...")

    is_download_done_processing()
  
    logging.info("Getting the latest downloaded file, rename and move into dedicated facility folder...")
    latest_download_file(facility_dir, resident_name_id)
    
    # wait.until(
    #     EC.url_contains(MUST_CONTAIN_IN_PDF_URL), 
    #     # driver.find_element(By.XPATH, '/html/body/pdf-viewer//viewer-toolbar//div/div[3]/viewer-download-controls//cr-icon-button')
    # )
    
    driver.close()
    driver.switch_to.window(driver.window_handles[2])
    driver.close()
    driver.switch_to.window(driver.window_handles[1])

def latest_download_file(facility_dir, resident_name_id):

    os.chdir(TEMP_DOWNLOAD_PATH)
    fileends = ["tmp", "crdownload"]
    
    while "tmp" in fileends or "crdownload" in fileends:
        files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
        newest = files[-1]
        logging.info('Downloading ' + newest)
        if "tmp" in newest or "crdownload" in newest:
            time.sleep(1)
        else:
            old_filename = TEMP_DOWNLOAD_PATH[:-1] + newest
            new_filename = resident_name_id
            rename_file(old_filename, new_filename, facility_dir)
            break

    logging.info('Download success:' + newest)

def rename_file(old_filename, new_filename, facility_dir):

    valid_filename = facility_dir + slugify(new_filename) + '.pdf'
    isExisting = os.path.exists(valid_filename)

    if not isExisting:
        os.rename(old_filename, valid_filename)


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")

def is_download_done_processing():
    initial_value = 'MatrixCare Report Processing'

    while 'MatrixCare Report Processing' == initial_value:
        if 'MatrixCare Report Processing' == driver.title:
            time.sleep(5)
        else:
            initial_value = 'MatrixCare Report Processing Completed'
        logging.info(initial_value)

try:
    login()
    facilities()
except OSError as err:
    sendMessage('Handling run-time error:' + err.strerror)