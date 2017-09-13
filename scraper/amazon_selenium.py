import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def init_driver():
    driver = webdriver.Firefox()
    driver.wait = WebDriverWait(driver, 5)
    return driver


def lookup(driver, query):
    driver.get("http://www.amazon.com")
    try:
        box = driver.wait.until(EC.presence_of_element_located(
            (By.NAME, "field-keywords")))
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "nav-input")))
        box.send_keys(query)
        button.click()

        time.sleep(5)

        # ids = driver.find_elements_by_xpath('//*[@id]')
        # for ii in ids:
        # # print ii.tag_name
        # print ii.get_attribute('id')  # id name amazon_selenium.py string

        t1 = driver.find_elements_by_xpath("//*[@id='gwt-uid-191-menu']/li/a")
        tmp = driver.find_elements_by_class_name('a-list-item')
        print(len(tmp))
        for l in tmp: #driver.find_elements_by_class_name('a-size-small a-color-base'):
            if "a-size-small a-color-base" in l.get_attribute("outerHTML").encode('ascii','ignore') \
                    and len(l.text)>2 \
                    and "a-declarative" not in l.get_attribute("outerHTML").encode('ascii','ignore'):
                print l.text
                #print l.get_attribute("class")
                #print l.get_attribute("innerHTML")
                #print l.get_attribute("outerHTML") ## lloks like we need this

    except TimeoutException:
        print("Box or Button not found in google.com")


if __name__ == "__main__":
    driver = init_driver()
    lookup(driver, "nivea")
    time.sleep(5)
    driver.quit()
