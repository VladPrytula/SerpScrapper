import threading
import time
import io
from datetime import timedelta, date

# install selenium https://pypi.python.org/pypi/selenium
from selenium import webdriver

# make sure geckodriver is in the PATH

# change the date here, 1 keyword a thread/browser
keywords = ['arganoel']
# change the date here, 1 day a thread/browser
# No. browsers opened = No. keywords * No. days
start_year = 2017
start_month = 8
start_day = 1
end_year = 2017
end_month = 8
end_day = 2

# twitter required params
login_url = 'https://www.twitter.com/login'
base_url = 'https://twitter.com/search?q='
since = '%20since%3A'
until = '%20until%3A'
src = '&src=typd'
time_sleep = 5
js_scroll_down = 'window.scrollTo(0, document.body.scrollHeight);'

# new file header
file_header = 'tweets-'


def dater_ange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def get_tweets(keyword, start_date, end_date):
    # please create files for storing credentials
    MY_SCREEN_NAME = "test" # open('username.txt').read().strip()
    MY_PASSWORD = "test" # open("password.txt").read().strip()
    # please remove encoding argument if using Mac
    ftweets = io.open('{}_{}_{}_{}'.format(file_header, keyword, start_date, end_date), 'w')
    browser = webdriver.Firefox()
    browser.get(login_url)
    time.sleep(time_sleep)

    username = browser.find_element_by_class_name("js-username-field")
    username.send_keys(MY_SCREEN_NAME)
    password = browser.find_element_by_class_name("js-password-field")
    password.send_keys(MY_PASSWORD)

    query = keyword + since + start_date + until + end_date + src
    url = base_url + query

    browser.get(url)
    time.sleep(time_sleep)

    with open("output_tweet.txt", "w") as of:
        while True:
            time.sleep(time_sleep)
            target_set = set()
            browser.execute_script(js_scroll_down)
            body = browser.find_element_by_class_name('stream')
            tweets = browser.find_elements_by_class_name('tweet-text')
            for tweet in tweets:
                of.write((tweet.text).encode('utf-8'))


start_date = date(start_year, start_month, start_day)
end_date = date(end_year, end_month, end_day)

for i in range(len(keywords)):
    # this should be limited to 5 or 10, no more.
    # then I am not sure how to run different queries
    # should go in batches.0
    for rank, single_date in zip(range((end_date - start_date).days), dater_ange(start_date, end_date)):
        current_date = single_date.strftime('%Y-%m-%d')
        y, m, d = current_date.split('-')
        next_date = (date(int(y), int(m), int(d)) + timedelta(1)).strftime('%Y-%m-%d')
        y_n, m_n, d_n = next_date.split('-')
        p = threading.Thread(target=get_tweets, args=(keywords[i], current_date, next_date))
        p.start()
