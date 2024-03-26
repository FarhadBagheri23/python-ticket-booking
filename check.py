from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from celery import Celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

check = Celery('check', broker = 'amqp://guest:guest@localhost:5672')

driver_location = "/usr/bin/chromedriver"

service = webdriver.ChromeService(driver_location)

# options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')

@check.task(name = 'check.check_ticket', bind = True)
def check_availabilty(self, origin:str, destination:str):
    driver = webdriver.Chrome(service = service)
    driver.get('https://safar724.com')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="route-panel"]/h2')))
    origin_input = driver.find_element(by = By.XPATH, value='//*[@id="route-panel__origin"]')
    origin_input.send_keys(origin + Keys.ENTER)

    destination_input = driver.find_element(by = By.XPATH, value='//*[@id="route-panel__destination"]')
    destination_input.send_keys(destination + Keys.ENTER)

    date = driver.find_element(by = By.XPATH, value = '//*[@id="date-panel__picker"]/div/table/tbody/tr[2]/td[4]/a')

    search_button = driver.find_element(by = By.XPATH, value = '//*[@id="date-panel__btn-search2"]')
    search_button.send_keys(Keys.RETURN)

    out_of_stock = driver.find_element(by = By.XPATH, value = '//*[@id="search-container"]/div[10]/div/div[2]/div/p[1]')
    ticket_exist = driver.find_element(by = By.XPATH, value = '//*[@id="header-panel"]/div/div[2]/h3')
    
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search-container"]/div[10]/div/div[2]/div/p[2]')))

    if out_of_stock:
        if 'متاسفانه' in out_of_stock.text:
            print("No ticket found!")
        else:
            if ticket_exist:
                print("ticket exist!!")
    
    
    driver.close()
