from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

class ScrapPubs:
    def __init__(self):
        self.chrome_options = Options()
       # self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--load-extension=c:\\Users\\marti\\Documents\\practice_data\\adblocker\\chrome")  # Load your extension here
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
            self.driver.get(self.start_url) # Open page
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
    