from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Condition
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from pathlib import Path
import time
import os

class AutomationLogin:
    @staticmethod
    def CheckDirectory():
        path = Path(os.path.expanduser('~')) / 'Documents'
        if Path(path / 'AutomationS').exists():

            if Path(path / 'AutomationS' / 'Print').exists():
                return Path(path / 'AutomationS' / 'Print')
            else:
                Path(path / 'AutomationS' / 'Print').mkdir()
                return Path(path / 'AutomationS' / 'Print')
        else:
            Path(path / 'AutomationS').mkdir()
            Path(path / 'AutomationS' / 'Print').mkdir()
            return Path(path / 'AutomationS' / 'Print')

    def __init__(self, username, password, arguments=None, experimental_arguments=None):
        self.username = username
        self.password = password
        self._Options(arguments, experimental_arguments)
        print('Creating Browser')
        self.service = Service(ChromeDriverManager().install())
        self.browser = webdriver.Chrome(options=self.options, service=self.service)
        self.wait = WebDriverWait(
            driver=self.browser,
            timeout=25,
            poll_frequency=1,
            ignored_exceptions=[NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException,
                                ElementClickInterceptedException, StaleElementReferenceException]
        )
        print('Starting Automation')
        self._start()

    def _Options(self, arguments, experimental_arguments):
        self.arguments = arguments
        self.experimental_arguments = experimental_arguments
        self.options = Options()
        self.options.add_argument('--lang=en-US')
        if self.arguments is not None:
            for argument in self.arguments:
                self.options.add_argument(argument)
        else:
            self.options.add_argument('--headless=new')

        if self.experimental_arguments is not None:
            for argument in self.experimental_arguments:
                self.options.add_experimental_option(*argument)
        else:
            self.options.add_experimental_option("excludeSwitches", ['enable-automation'])

    def _start(self):
        self.start_time = time.time()
        self.browser.get('https://login.microsoftonline.com/')
        time.sleep(5)
        print('Entering Site')
        self.wait.until(Condition.element_to_be_clickable((By.XPATH, '//*[@id="i0116"]'))).send_keys(self.username)
        print('Writing Email')
        self.wait.until(Condition.element_to_be_clickable((By.XPATH, '//*[@id="idSIButton9"]')))
        self.browser.find_element(By.XPATH, '//*[@id="i0118"]').send_keys(self.password)
        print('Typing Password')
        self.wait.until(Condition.element_to_be_clickable((By.XPATH, '//*[@id="idSIButton9"]'))).click()
        self.wait.until(Condition.element_to_be_clickable((By.XPATH, '//*[@id="idSIButton9"]'))).click()
        print('Login Successful')

class UpdateWorkspace(AutomationLogin):
    def __init__(self, username, password, workspace, arguments=None, experimental_arguments=None):
        super().__init__(username, password, arguments, experimental_arguments)
        self.browser.get(workspace)
        print('Filtering Data')
        self.wait.until(Condition.element_to_be_clickable((By.XPATH,
                                                           "//button[@class='tri-filter-menu-trigger-button"
                                                           " tri-flex tri-justify-center tri-items-center tri-text-sm tri-border "
                                                           "tri-rounded tri-border-solid tri-bg-gray-white tri-border-gray-82 tri-h-32px"
                                                           " tri-text-gray-180 tri-box-border tri-filter-menu-state']"))).click()
        print('Data Set')
        self.wait.until(Condition.element_to_be_clickable((By.XPATH, "//div[@id='1'][@class='tri-flex tri-items-center "
                                                                     "tri-multiselect-list-item-label tri-w-full tri-h-32px tri-px-2']"))).click()

        actions = ActionChains(self.browser)
        list_elements = self.browser.find_elements(By.XPATH, "//mat-icon[@data-mat-icon-name='pbi-glyph-refresh']")
        self.wait.until(Condition.element_to_be_clickable(
            (By.XPATH, '//div[@class="mat-sort-header-container mat-focus-indicator ng-tns-c371-5"]')))
        try:
            for value in range(len(list_elements)):
                print(f'Updating Report {value+1}')
                element = self.browser.find_elements(By.XPATH, '//mat-icon[@fonticon="pbi-glyph-refresh"]')[value]
                actions.move_to_element(element).perform()
                self.wait.until(Condition.visibility_of(element)).click()
                actions.move_to_element(element).perform()
            print('Updated successfully')
        except:
            print('Wait for Scheduled Update')

        print(f'Total Time Spent: {round((time.time() - self.start_time) / 60, 2)} minutes')

class DownloadReport(UpdateWorkspace):
    def __init__(self, username, password, workspace, links, arguments=None, experimental_arguments=None):
        super().__init__(username, password, workspace, arguments, experimental_arguments)
        time.sleep(15)
        for link in links:
            self.browser.execute_script("window.open('', '_blank');")
            self.browser.switch_to.window(self.browser.window_handles[-1])
            self.browser.get(link)
            print('Opening Report')
            self.wait.until(Condition.element_to_be_clickable((By.XPATH, '//button[(@id = "exportMenuBtn")]'))).click()
            self.wait.until(Condition.element_to_be_clickable((By.XPATH, '//button[@data-testid="export-to-pdf-btn"]'))).click()
            self.wait.until(Condition.element_to_be_clickable((By.XPATH, '//button[@id="okButton"]'))).click()
            print('Downloading Report')
            time.sleep(50)
            print(f'Total Time Spent: {round((time.time() - self.start_time) / 60, 2)} minutes')

    def _Options(self, arguments, experimental_arguments):
        current_directory = self.CheckDirectory()
        self.options = Options()
        self.options.add_argument('--lang=en-US')
        if arguments is not None:
            for argument in arguments:
                self.options.add_argument(argument)
        else:
            self.options.add_argument('--headless=new')

        self.options.add_experimental_option("prefs",
                    {"download.default_directory": f"{current_directory}", "download.prompt_for_download": False,
                     "download.directory_upgrade": True, "safebrowsing.enabled": True})
        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])


class ViewReports(UpdateWorkspace):
    def __init__(self, login, password, workspace, interval, links, Arguments=['--lang=pt-BR', '--disable-notifications', '--kiosk','--lang=en-US'], ArgumentsEX=None):
        super().__init__(login, password, workspace, Arguments, ArgumentsEX)
        while True:
            for link in links:
                self.browser.execute_script("window.open('', '_blank');")
                self.browser.switch_to.window(self.browser.window_handles[-1])
                self.browser.get(link + '&chromeless=True')
                self.wait.until(Condition.element_to_be_clickable((By.XPATH, '//i[@aria-label="Next"]')))
                time.sleep(interval)
                while True:
                    try:
                        self.browser.find_element(By.XPATH, '//i[@aria-label="Next"]').click()
                        element = self.browser.find_element(By.XPATH, '//i[@aria-label="Next"]').get_attribute("class")
                        time.sleep(interval)
                        if 'inactive' in element:
                            break
                    except:
                        print('Next')
                        break
            for _ in range(len(links)):
                self.browser.execute_script("window.close()")
                self.browser.switch_to.window(self.browser.window_handles[-1])

