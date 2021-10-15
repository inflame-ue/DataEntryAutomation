# imports
import bs4
import requests
from selenium import webdriver
from time import sleep

# constants
GOOGLE_FORM_URL = "your google form"
ZILLOW_URL = "https://www.zillow.com/homes/for_rent/1-_beds/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22mapBounds%22%3A%7B%22west%22%3A-123.16122993742587%2C%22east%22%3A-121.55447944914462%2C%22south%22%3A37.34418863281167%2C%22north%22%3A37.92926180527435%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D"
HEADERS_FOR_ZILLOW = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15",
    "Accept-Language": "en-US"
}
DRIVER_PATH = "your web browser driver path"


# function block
def make_a_request():
    """
    This function makes a request for all the HTML code on the Zillow website
    :return: HTML code
    """
    response = requests.get(url=ZILLOW_URL, headers=HEADERS_FOR_ZILLOW)
    response.raise_for_status()

    return response.text


def check_links(links_to_check: list) -> list:
    """
    This function converts non workable links in workable ones
    :param links_to_check: links that you want to check
    :return: working links
    """
    for index in range(len(links_to_check)):
        if not links_to_check[index].startswith("http"):
            links_to_check[index] = "https://www.zillow.com" + links_to_check[index]

    return links_to_check


# class block
class DataScrapper:
    """
    This class is responsible for scrapping all the data from Zillow website
    """

    def __init__(self, html_code):
        """
        Here we initialize create an object BeautifulSoup class
        :param html_code: html_code that we want to parse
        """
        self.soup = bs4.BeautifulSoup(html_code, "html.parser")

    def get_links(self):
        """
        This function scraps html code from Zillow and gets links for all the listings
        :return: scrapped data
        """
        code_with_links = self.soup.find_all(name="a", class_="list-card-link")
        links_to_return = check_links([code.get("href") for code in code_with_links])

        return links_to_return

    def get_prices(self):
        """
        This function scraps html code from Zillow and gets prices for all the listings
        :return: prices
        """
        code_with_prices = self.soup.find_all(name="div", class_="list-card-price")
        prices_to_return = [code.text.split("/", )[0] for code in code_with_prices]

        return prices_to_return

    def get_addresses(self):
        """
        This function scraps html code from Zillow website and gets addresses for all the listings
        :return: addresses
        """
        code_with_addresses = self.soup.find_all(name="address", class_="list-card-addr")
        addresses_to_return = [code.text for code in code_with_addresses]

        return addresses_to_return


class DataEntry:
    """
    This class is responsible filling the google form and creating a google sheet
    """

    def __init__(self):
        """
        Initialize selenium
        """
        self.driver = webdriver.Chrome(DRIVER_PATH)
        # self.driver.get(GOOGLE_FORM_URL)  # open google form

    def fill_the_form(self, address, price, link):
        """
        This function is responsible for filling the form
        :param address: address from the Zillow
        :param price: price from the Zillow
        :param link: link from the Zillow
        :return: nothing
        """
        sleep(3)
        self.driver.find_element_by_xpath(
            "//*[@id=\"mG61Hd\"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input"
        ).send_keys(address)  # address
        sleep(3)

        self.driver.find_element_by_xpath(
            "//*[@id=\"mG61Hd\"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input"
        ).send_keys(price)  # price
        sleep(3)

        self.driver.find_element_by_xpath(
            "//*[@id=\"mG61Hd\"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input"
        ).send_keys(link)  # link
        sleep(3)

    def send_the_form(self):
        """
        This function is responsible for sending the form.
        :return: nothing
        """
        # send the form
        self.driver.find_element_by_xpath("//*[@id=\"mG61Hd\"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span").click()
        sleep(3)

        # open the form once again
        self.driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/div[4]/a").click()
        sleep(3)

    def create_a_table(self):
        """
        This function is responsible for creating a table in responses tab of google form.
        :return: nothing
        """
        self.driver.get("https://docs.google.com/forms/d/1g3JQhcHE6MFM9Vs4SScqE-RLX3lJQfKxSDvszG1ZyJM/edit?usp=sharing")
        sleep(3)

        self.driver.find_element_by_xpath("//*[@id=\"tJHJj\"]/div[3]/div[1]/div/div[2]/span/div").click()
        sleep(3)

        # create a table
        self.driver.find_element_by_xpath("//*[@id=\"ResponsesView\"]/div/div[1]/div[1]/div[2]/div[1]/div/div/span").click()
        sleep(3)

    def close_tab(self):
        """
        This function just closes the tab
        :return: nothing
        """
        self.driver.close()


# Scrap Zillow
scrapper = DataScrapper(make_a_request())
links = scrapper.get_links()
prices = scrapper.get_prices()
addresses = scrapper.get_addresses()

# Fill the Google Form
bot = DataEntry()

for index in range(len(prices)):
    bot.fill_the_form(addresses[index], prices[index], links[index])
    bot.send_the_form()
    sleep(3)

bot.create_a_table()
bot.close_tab()
