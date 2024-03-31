from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from celery import Celery
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

class TicketChecker:
    def __init__(self, driver_location):
        self.driver_location = driver_location
        self.service = webdriver.ChromeService(driver_location)

    def check_availability(self, origin, destination):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(service = self.service, options = options)
        driver.set_page_load_timeout(20)

        driver.get("https://safar724.com")
        wait = WebDriverWait(driver,10)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[4]/div/div[1]/div/a/img')))
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
                logger.info("No ticket found!, retrying in 10's")
                raise SoftTimeLimitExceeded(countdown = 10)
            else:
                if ticket_exist:
                    print("ticket exist!!")

        driver.close()



app = Celery('tester', broker='amqp://guest:guest@localhost:5672')
logger = get_task_logger(__name__)

@app.task(name = 'tester.checker',bind = True ,max_retries = 5)
def check_availability_task(self, origin, destination):
    bot = TicketChecker('/usr/bin/chromedriver')
    bot.check_availability(origin, destination)

if __name__=="__main__":
    try:
        check_availability_task('tehran', 'shiraz')
    except Exception as e:
        print(e)
    

bot = TicketChecker('/usr/bin/chromedriver')

bot.check_availability('tehran', 'shiraz')


# options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')