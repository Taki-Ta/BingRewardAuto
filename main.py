from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from concurrent.futures import ThreadPoolExecutor

import yaml
import time
import random
import requests

def get_edge_driver(user_data_dir, edge_driver_path):
    edge_options = Options()
    edge_options.add_argument(f"--user-data-dir={user_data_dir}")
    edge_service = Service(edge_driver_path)
    driver = webdriver.Edge(service=edge_service, options=edge_options)
    return driver

def switch_to_mobile_mode(driver):
    # 设置设备模拟参数
    device_metrics = {
        "width": 375,
        "height": 812,
        "deviceScaleFactor": 3.0,
        "mobile": True
    }
    # 设置用户代理
    user_agent = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    )
    # 设备模拟
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", device_metrics)
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})

def perform_bing_search(driver, search_query):
    driver.get("https://www.bing.com")
    time.sleep(2)
    search_box = driver.find_element("name", "q")
    search_box.clear()
    search_box.send_keys(search_query)
    time.sleep(random.uniform(1, 3))
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)

def smooth_scroll_to_bottom(driver):
    scroll_script = """
        var totalHeight = document.body.scrollHeight;
        var distance = Math.random() * 100 + 50;
        var timer = setInterval(function() {
            window.scrollBy(0, distance);
            if (window.pageYOffset >= totalHeight - window.innerHeight) {
                clearInterval(timer);
            }
        }, 30);
    """
    driver.execute_script(scroll_script)

def auto_str_trans(st):
    result = ""
    i = 0
    while i < len(st):
        step = random.randint(2, 5)
        result += st[i:i+step] + " "
        i += step
    return result.strip()

def get_baidu_hot_search():
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            hot_searches = soup.select('.c-single-text-ellipsis')
            return [search.get_text().strip() for search in hot_searches[:50]]
        print(f"Failed to retrieve data: {response.status_code}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_random_elements(array, num_elements):
    return random.sample(array, num_elements) if num_elements <= len(array) else []

def process(driver, keywords, total_count):
    for count in range(total_count):
        search_query = auto_str_trans(keywords[count])
        print(f"【{count+1}/{total_count}】: {search_query}")
        perform_bing_search(driver, search_query)
        smooth_scroll_to_bottom(driver)
        time.sleep(random.uniform(10, 30))

def run_search(user_list, edge_driver_path, keywords, total_count, mobile_mode=False):
    keywords = get_random_elements(keywords, total_count)
    with ThreadPoolExecutor(max_workers=len(user_list)) as executor:
        for user in user_list:
            driver = get_edge_driver(user, edge_driver_path)
            if mobile_mode:
                switch_to_mobile_mode(driver)
            executor.submit(process, driver, keywords, total_count)
            time.sleep(2)

def load_config(config_file="config.yaml"):
    with open(config_file, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def main():
    config = load_config()  # 读取配置文件

    user_list = config["user_list"]
    edge_driver_path = config["edge_driver_path"]
    pc_count = config["pc_count"]
    mobile_count = config["mobile_count"]
    pc_search = config["pc_search"]
    mobile_search = config["mobile_search"]
    
    all_keywords = get_baidu_hot_search()

    if pc_search and pc_count>0:
        print("开始桌面模式搜索...")
        run_search(user_list, edge_driver_path, all_keywords, pc_count, mobile_mode=False)

    if mobile_search and mobile_count>0:
        print("开始移动端模式搜索...")
        run_search(user_list, edge_driver_path, all_keywords, mobile_count, mobile_mode=True)

if __name__ == "__main__":
    main()
