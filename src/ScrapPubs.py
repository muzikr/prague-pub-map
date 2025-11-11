from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import urlparse, parse_qs

class ScrapPubs:
    def __init__(self):
        self.chrome_options = Options()
       # self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
       # self.chrome_options.add_argument("--load-extension=c:\\Users\\marti\\Documents\\practice_data\\adblocker\\chrome")  # Load your extension here
        self.start_url = "https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-praha"  

        #self.service = Service('chromedriver.exe')  # Update with your chromedriver path
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 10)  # 10 seconds wait

    def _extract_coordinates_from_url(self, url):
        """Extract latitude and longitude from a given URL."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        x = query_params.get('x', [None])[0]
        y = query_params.get('y', [None])[0]
        return x, y

    def get_pub_data(self):
        """1) Get urls of pubs from a directory site
           2) Visit each pub's page and scrape data
           3) Return the data as a list of dictionaries
           4) Move to next page and repeat until no more pages left
        """

        # Fix some pub temporarily
        self.driver.get("https://www.firmy.cz/detail/2220349-restaurace-u-blekotu-praha-kobylisy.html")
        shadow_host = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "szn-cmp-dialog-container")))
        shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        button = shadow_root.find_element(By.CSS_SELECTOR, '[data-testid="cw-button-agree-with-ads"]')
        button.click()
        time.sleep(5)
        #print(self.driver.page_source)
        #attributes = self.driver.execute_script("""
        #var items = {}; 
        #for (index = 0; index < arguments[0].attributes.length; ++index) {
        #    items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value
        #}; 
        #return items;
        #""", self.driver.find_element(By.CLASS_NAME, "mapyRatingBadge.hydrated"))
        time.sleep(2)
        #rating = attributes['rating']
        rating = self.driver.find_element(By.CLASS_NAME, "mapyRatingBadge.hydrated").get_attribute("rating")
        print("Rating:", rating)
        button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-black.wholeList")
        self.driver.execute_script("arguments[0].click();", button)
        time.sleep(1)

        url_plan = self.driver.find_element(By.CSS_SELECTOR, ".detailPlanRoute > a:nth-child(1)").get_attribute("href")
        print("Plan route URL:", url_plan)
        lat, lon = self._extract_coordinates_from_url(url_plan)
        print("Latitude:", lat)
        print("Longitude:", lon)

        buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.pillBtn")
        for button in buttons:
            self.driver.execute_script("arguments[0].click();", button)
            time.sleep(1)

            menu_item = self.driver.find_elements(By.CSS_SELECTOR, "div.menuItem.withPrice .description")
            price = self.driver.find_elements(By.CSS_SELECTOR, "div.menuItem.withPrice .price")
            for item, price in zip(menu_item, price):
                print(f"{item.text}: {price.text}")


    def get_pubs_urls(self, page_url):
        """Get URLs of pubs from the directory site."""
        try:
            # premiseBox
            # premiseBox withOffer
            self.driver.get(self.start_url) # Open page

            # Handle consent to ads button
            # please wait until the shadow DOM is available
            shadow_host = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "szn-cmp-dialog-container")))
            shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", shadow_host)
            button = shadow_root.find_element(By.CSS_SELECTOR, '[data-testid="cw-button-agree-with-ads"]')
            button.click()

            block_containing_urls =self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "premiseList")))  # Locate the block with pub links

            #We take different types of premiseBoxes
            hopefully_urls = block_containing_urls.find_elements(By.CLASS_NAME, "premiseBox")  # Find all anchor tags within the block
            hopefully_urls.extend(block_containing_urls.find_elements(By.CLASS_NAME, "premiseBox withOffer"))
            hopefully_urls.extend(block_containing_urls.find_elements(By.CLASS_NAME, "premiseBox freeProfile"))
            for block in hopefully_urls:
                print(block.find_element(By.CSS_SELECTOR, '[data-dot="premise"]').get_attribute("href"))
            #    print(url.find_element(By.CSS_SELECTOR, '[data-dot="premise"]').get_attribute("href"))
            # Implement logic to extract pub URLs from the page
            pub_urls = []  # Replace with actual extraction logic
            return pub_urls    
        
        except Exception as e:
            print(f"Error fetching pub URLs: {e}")
            return []    
    
if __name__ == "__main__":
    scraper = ScrapPubs()
    #scraper.get_pubs_urls(scraper.start_url)
    scraper.get_pub_data()
    