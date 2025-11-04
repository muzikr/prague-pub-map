from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
class ScrapPubs:
    def __init__(self):
        self.chrome_options = Options()
       # self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
       # self.chrome_options.add_argument("--load-extension=c:\\Users\\marti\\Documents\\practice_data\\adblocker\\chrome")  # Load your extension here
        self.start_url = "https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-praha"  

        self.service = Service('chromedriver.exe')  # Update with your chromedriver path
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)

    def get_pub_data(self):
        """1) Get urls of pubs from a directory site
           2) Visit each pub's page and scrape data
           3) Return the data as a list of dictionaries
           4) Move to next page and repeat until no more pages left
        """
        pass

    def get_pubs_urls(self, page_url):
        """Get URLs of pubs from the directory site."""
        try:
            # premiseBox
            # premiseBox withOffer
            self.driver.get(self.start_url) # Open page

            # Handle consent to ads button
            time.sleep(5)  # Wait for the page to load completely
            shadow_host = self.driver.find_element(By.CLASS_NAME, "szn-cmp-dialog-container")
            shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", shadow_host)
            button = shadow_root.find_element(By.CSS_SELECTOR, '[data-testid="cw-button-agree-with-ads"]')
            button.click()

            time.sleep(5)  # Wait for the page to load completely after clicking
            block_containing_urls = self.driver.find_element(By.CLASS_NAME, "premiseList")  # Locate the block with pub links
            hopefully_urls = block_containing_urls.find_elements(By.TAG_NAME, "a")  # Find all anchor tags within the block
            for url in hopefully_urls:
                print(url.get_attribute("href"))

            # Implement logic to extract pub URLs from the page
            pub_urls = []  # Replace with actual extraction logic
            return pub_urls    
        
        except Exception as e:
            print(f"Error fetching pub URLs: {e}")
            return []    
    
if __name__ == "__main__":
    scraper = ScrapPubs()
    scraper.get_pubs_urls(scraper.start_url)
    