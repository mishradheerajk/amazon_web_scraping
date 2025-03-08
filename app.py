from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

app = Flask(__name__)

def get_amazon_images(asin):
    # Setup for Selenium WebDriver
    options = Options()
    options.headless = True  # To run in headless mode (without opening the browser window)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # URL of the product page
    url = f'https://www.amazon.in/dp/{asin}'
    driver.get(url)
    
    # Wait for the page to load
    time.sleep(3)
    
    # First, find and click on the main image to open the image gallery
    main_image = driver.find_element(By.XPATH, '//img[contains(@class,"a-dynamic-image")]')
    
    # Extract the URL of the first image (main image)
    main_image_url = main_image.get_attribute('src')
    image_urls = [main_image_url]  # Start with the main image URL
    
    # Click on the main image to open the gallery
    main_image.click()
    
    # Wait for the image gallery to load
    time.sleep(2)

    # Now, find all the thumbnails and click on each to open the large image
    thumbnails = driver.find_elements(By.XPATH, '//div[@class="ivThumb"]')
    
    for thumb in thumbnails:
        try:
            thumb.click()  # Click on each thumbnail to open the large image
            time.sleep(1)  # Wait for the large image to load
            
            # Find the large image and extract its URL
            large_image = driver.find_element(By.XPATH, '//div[@id="ivLargeImage"]/img')
            large_image_url = large_image.get_attribute('src')
            if large_image_url:
                image_urls.append(large_image_url)
        except Exception as e:
            print(f"Error occurred: {e}")
            continue
    
    driver.quit()
    return image_urls

@app.route('/get_images', methods=['GET'])
def get_images():
    # Get the ASIN from the request
    asin = request.args.get('asin')
    if not asin:
        return jsonify({"error": "ASIN is required"}), 400
    
    # Get image URLs
    image_urls = get_amazon_images(asin)
    
    # Return image URLs as JSON response
    return jsonify({"asin": asin, "image_urls": image_urls})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Run on all network interfaces, port 5000
