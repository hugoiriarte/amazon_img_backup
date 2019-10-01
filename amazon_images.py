#Imports
from selenium import webdriver
import time
import requests
from selenium.webdriver.common.action_chains import ActionChains


def main():
    """
    Supplement to Category Listing Report, download all product images by ASIN
    """
    chromedriver = 'Path To Driver'
    driver = webdriver.Chrome(chromedriver)
    url = 'https://sellercentral.amazon.com/'
    email = 'Your Seller Central Email'
    pw = 'Password'
    driver.get(url)
    time.sleep(3)

    #Login
    driver.find_element_by_id('ap_email').send_keys(email)
    driver.find_element_by_id('ap_password').send_keys(pw)
    driver.find_element_by_id('signInSubmit').click()
    input('Enter OTP, then press any key to continue')

    #Navigate to Inventory
    driver.find_element_by_id('sc-navtab-inventory').click()

    #Expand to 250 results per page
    #If you have over 250 products this section should be adjusted
    driver.find_element_by_id('a-autoid-44-announce').click()
    time.sleep(3)
    driver.find_element_by_id('dropdown1_4').click()
    time.sleep(10)
    #Extract href from elements
    urls = driver.find_elements_by_css_selector('table > tbody > tr > td:nth-child(6) > div > div > div > a')
    urls = [x.get_attribute('href') for x in urls]

    for url in urls:
        imageURL = []
        driver.get(url)
        time.sleep(3)
        #Obtain product ASIN
        asin = driver.find_element_by_css_selector('#skuCent-overview > div > div.a-box.skuCent-detail > div > div:nth-child(2) > div:nth-child(4) > span').text
        time.sleep(4)
        #Edit product
        driver.find_elements_by_class_name('menuButtonGroup')[0].click()
        #Switch to newly opened tab
        newTab = driver.window_handles[1]
        driver.switch_to_window(newTab)
        #Check for product error
        try:
            error = driver.find_element_by_css_selector('body > div:nth-child(13) > ul.restricted-messages > li').text
            errorFound = True
        except:
            errorFound = False
        #Return to original window and go to next product
        if errorFound == True:
            driver.close()
            driver.switch_to_window(driver.window_handles[0])
        else:
            #Error handler if page is broken and there is no images tab        
            try:
                driver.find_element_by_id('image-tab').click()
                broken = False
            except:
                broken = True
            if broken == False:
                time.sleep(3)
                #Error handler if there are no images within product
                try:
                    images = driver.find_elements_by_class_name('previewImage')
                    broken2 = False
                except:
                    broken2 = True
                if broken2 == False:
                    for i in images:
                        if i.get_attribute('src') != '':
                            #If the src is not an empty string append to imageURL variable
                            imageURL.append(i.get_attribute('src'))
                    loop = 0
                    for image in imageURL:
                        #Open request session and get image url                
                        s = requests.session()
                        r = s.get(image)
                        #If its first loop dont add _ + loop counter
                        if loop == 0:
                            open(asin + '.png', 'wb').write(r.content)
                        #If other than first itteration add loop counter
                        else:
                            open(asin + '_' + str(loop) + '.png', 'wb').write(r.content)
                        loop += 1
                    #Close current tab
                    driver.close()
                    windows = driver.window_handles
                    #Error handler if there are more than 1 tab open
                    if len(windows) > 1:
                        for i in windows:
                            if i != driver.window_handles[0]:
                                driver.switch_to_window(i)
                                driver.close()
                    #Return to original window
                    driver.switch_to_window(driver.window_handles[0])     