from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import argparse
from urllib.parse import urlparse, parse_qs
import tqdm
from selenium.common.exceptions import TimeoutException

START_URL_PRAGUE = "https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-praha"

START_URL_WHOLE_CZECHIA = "https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince"

def write_data(data : dict, file) -> None:
    if data["menu"]:
        for menu_item, price in data["menu"]:
            print(f'{data["url"]};{data["rating"]};{data["number_of_reviews"]};{data["coordinates"][0]};{data["coordinates"][1]};"{menu_item};{price}"',file=file)
    else:
        print(f'{data["url"]};{data["rating"]};{data["number_of_reviews"]};{data["coordinates"][0]};{data["coordinates"][1]};;',file=file)



class ScrapPubs:
    def __init__(self):
        self.chrome_options = Options()
        # Run in headless mode so the browser window doesn't pop up
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")

        #self.service = Service('chromedriver.exe')  # Update with your chromedriver path
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 30)  # 10 seconds wait
        self.was_restarted = False

    def restart_driver(self):
        """Restart the WebDriver."""
        self.driver.quit()
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        self.was_restarted = True

    def _extract_coordinates_from_url(self, url):
        """Extract latitude and longitude from a given URL."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        x = query_params.get('x', [None])[0]
        y = query_params.get('y', [None])[0]
        return x, y
        
    def _get_rating(self):
        """Extract rating from the page."""
        try:
            rating_elem = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mapyRatingBadge.hydrated")))
            rating = rating_elem.get_attribute("rating")
            number_of_ratings = rating_elem.get_attribute("reviews")
            return rating, number_of_ratings
        except Exception as e:
            print(f"Error extracting rating: {e}")
            return None, None
    
    def _get_coordinates(self):
        """Extract coordinates from the page."""
        url_plan = self.driver.find_element(By.CSS_SELECTOR, ".detailPlanRoute > a:nth-child(1)").get_attribute("href")
        lat, lon = self._extract_coordinates_from_url(url_plan)
        return lat, lon
    
    def _get_menu(self):
        buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.btn.btn-black.wholeList")
        if len(buttons) > 0:
            self.driver.execute_script("arguments[0].click();", buttons[0])
        menu = []

        def get_one_menu():
            menu_items = self.driver.find_elements(By.CSS_SELECTOR, "div.menuItem.withPrice .description")
            prices = self.driver.find_elements(By.CSS_SELECTOR, "div.menuItem.withPrice .price")
            menu.extend([(menu_item.text,price.text) for menu_item, price in zip(menu_items, prices)])

        buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.pillBtn")

        for button in buttons:
            self.driver.execute_script("arguments[0].click();", button)
            get_one_menu()
        
        if not buttons:
            get_one_menu()

        return menu

    def get_pub_data(self, url: str):
        """1) Get urls of pubs from a directory site
           2) Visit each pub's page and scrape data
           3) Return the data as a list of dictionaries
           4) Move to next page and repeat until no more pages left
        """
        try:
            # Ensure page load / scripts don't hang indefinitely
            try:
                self.driver.set_page_load_timeout(30)
            except Exception:
                pass
            try:
                self.driver.set_script_timeout(30)
            except Exception:
                pass

            self.driver.get(url)
            if self.was_restarted:
                shadow_host = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "szn-cmp-dialog-container")))
                shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", shadow_host)
                time.sleep(2)
                buttons = shadow_root.find_elements(By.CSS_SELECTOR, '[data-testid="cw-button-agree-with-ads"]')
                if buttons:
                    buttons[0].click()
                self.was_restarted = False

            rating, number_of_reviews = self._get_rating()
            lat, lon = self._get_coordinates()
            menu = self._get_menu()
            pub_data = {
                "url": url,
                "rating": rating,
                "coordinates": (lat, lon),
                "menu": menu,
                "number_of_reviews": number_of_reviews
            }
            return pub_data
        
        except TimeoutException as e:
            # Page load or script timed out — skip this pub
            print(f"Timeout fetching data for {url}: {e}")
            try:
                self.restart_driver()
            except Exception:
                pass
            return None

        except Exception as e:
            self.restart_driver()
            print(f"Error fetching data for {url}: {e}")
            return None


    def get_pubs_urls(self, start_url : str) -> list[str]:
        """Get URLs of pubs from the directory site."""
        pub_urls = []
        try:
            self.driver.get(start_url) # Open page
                # Handle consent to ads button
                # please wait until the shadow DOM is available
            shadow_host = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "szn-cmp-dialog-container")))
            shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", shadow_host)
            time.sleep(2)
            button = shadow_root.find_element(By.CSS_SELECTOR, '[data-testid="cw-button-agree-with-ads"]')
            button.click()
            is_there_more = True

            while is_there_more:
                block_containing_urls =self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "premiseList")))  # Locate the block with pub links

                #We take different types of premiseBoxes
                hopefully_urls = block_containing_urls.find_elements(By.CLASS_NAME, "premiseBox")  # Find all anchor tags within the block
                hopefully_urls.extend(block_containing_urls.find_elements(By.CLASS_NAME, "premiseBox withOffer"))
                hopefully_urls.extend(block_containing_urls.find_elements(By.CLASS_NAME, "premiseBox freeProfile"))
                
                for block in hopefully_urls[:-1]: # for some reason last one does not have link
                    try:
                        print(block.find_element(By.CSS_SELECTOR, '[data-dot="premise"]').get_attribute("href"))
                        pub_urls.append(block.find_element(By.CSS_SELECTOR, '[data-dot="premise"]').get_attribute("href"))
                    except Exception as e:
                        print(f"Error extracting URL from block: {e}")

                is_there_more = self.__get_another_page()  # Check if there's a next page and navigate to it
            print(f"Total URLs found: {len(pub_urls)}")
            return pub_urls    
        
        except Exception as e:
            print(f"Error fetching pub URLs: {e}")
            return []    
    
    def __get_another_page(self):
        """Navigate to the next page of the directory."""
        try:
            next_button = self.wait.until(EC.presence_of_element_located((By.ID, "nextBtn")))  # Adjust selector as needed
            # Scroll into view to avoid interception
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            except Exception:
                # fallback simple scroll
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)

            try:
                self.driver.execute_script("arguments[0].click();", next_button)
            except Exception as js_err:
                return False
    
            return True
        
        except Exception as e:
            print(f"No more pages or error navigating to next page: {e}")
            return False
    
if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Scrape pub data from a directory site.")
    argparser.add_argument("--all_czechia", action="store_true", help="Scrape pubs from the whole Czechia instead of just Prague.", default=None)
    args = argparser.parse_args()
    scraper = ScrapPubs()
    start_url = START_URL_WHOLE_CZECHIA
    filename = "pubs_data_czechia_1604.csv"
    if args.all_czechia is None :
        start_url = START_URL_PRAGUE
        filename = "pubs_data_pragueadadada.csv"
    list_of_pubs = scraper.get_pubs_urls(start_url)
    print(f"Total pubs to scrape: {len(list_of_pubs)}")

    pubs_data = []
    failed = []

    with open(filename,"w",encoding = "utf-8") as f:
        print("url;rating;number_of_reviews;latitude;longitude;menu_item;price",file=f)
        for i in tqdm.tqdm(range(1604,len(list_of_pubs))):
            url = list_of_pubs[i]

            # Reuse the main scraper's driver — faster because we don't recreate Chrome each time.
            pub_data = scraper.get_pub_data(url)
            if pub_data is None:
                failed.append(url)
                continue
            pubs_data.append(pub_data)
            write_data(pub_data,f)

    pubs_with_no_menu_count = len([pub for pub in pubs_data if len(pub['menu']) == 0])
    print(f"data with no menu percentage: {pubs_with_no_menu_count / len(pubs_data) * 100}%")
    print(f"Total pubs scraped: {len(pubs_data)}")
    print(f"Pubs with no menu: {pubs_with_no_menu_count}")
    print(f"Pubs with menu: {len(pubs_data) - pubs_with_no_menu_count}")
    print(f"Failed to scrape {len(failed)} pubs.")