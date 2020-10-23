import os
import time
from selenium import webdriver
from .tasks import download_image

def scroll(wd, config):
    '''
    Google images uses an infinite scroll and will only load more results
    upon reaching the bottom of the page. Here, we give the web driver will 
    a way to throw throw javascript that will direct the page to scrholl
    '''

    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(config['wait_time'])   


def gather_images(target, wd, config):
    '''
    We will search through images returned by the query, determine the URI
    and send tasks to our workers.
    '''

    # This is the simple query
    query_string = 'https://www.google.com/search?q={q}&tbm=isch'.format(q=target.replace(' ','%20'))

    # Initial page load
    wd.get(query_string)

    # Scanning the scrolled page will bring back all of the images we've 
    # already seen, so we have to keep track
    seen = list()

    # Succesful URIs captured. Unfortunately this will not exactly be the
    # successful images captured as the workers may run into HTTP errors. But
    # we are just scraping, we aren't really worried about exactitude
    success = list()

    while len(success) < config['limit']:
        # Grab images by this odd class type 
        thumbnail_results = wd.find_elements_by_css_selector('img.Q4LuWd')

        # Remove the ones we've seen
        thumbnail_results = list(set(thumbnail_results) - set(seen))

        for img in thumbnail_results:
            seen.append(img)

            # The thumbnail is hiding the real URI, which is behind a click
            try:
                img.click()
                time.sleep(config['wait_time'])  # Pause for loading
            except Exception:
                continue

            # Extract the URI
            # Multiple potential targets (actual_images) are returned because
            # Google also inserts a base64 encoding which we can just ignore
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')

            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_uri = actual_image.get_attribute('src')
                    download_image(image_uri, target)
                    print('Found {}'.format(image_uri))
                    success.append(image_uri)

            # Quit if we've reached our limit
            if len(success) >= config['limit']:
                break

    
if __name__ == '__main__':
    # The magic pseudo-browser
    wd = webdriver.Chrome(executable_path = 'buzz_celery/chromedriver')

    # Configuration
    config = {'limit': 5,
              'wait_time': 1}

    # Read in the queries
    with open('buzz_celery/targets.txt', 'r') as t:
        targets = [target.strip() for target in t.readlines()]

    # Accumulate images for each target
    for target in targets:
        gather_images(target, wd, config)