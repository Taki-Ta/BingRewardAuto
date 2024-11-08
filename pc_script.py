from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor

def get_edge_driver(user_data_dir, edge_driver_path):
    edge_options = Options()
    edge_options.add_argument(f"--user-data-dir={user_data_dir}")
    edge_service = Service(edge_driver_path)
    driver = webdriver.Edge(service=edge_service, options=edge_options)
    return driver

def perform_bing_search(driver, search_query):
    time.sleep(2)  # 等待页面加载
    search_box = driver.find_element("name", "q")
    search_box.clear()
    search_box.send_keys(search_query)
    time.sleep(random.uniform(1, 3))  # 等待1-3秒
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)  # 等待搜索结果加载

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
    y_str = st
    r_str = " "
    z_str = ""
    pre_po = 0
    i = 0
    while i < len(y_str):
        step = random.randint(2, 5)
        if i > 0:
            z_str += y_str[pre_po:i] + r_str
            pre_po = i
        i += step
    if pre_po < len(y_str):
        z_str += y_str[pre_po:]
    return z_str

def get_baidu_hot_search():
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        hot_searches = soup.select('.c-single-text-ellipsis')
        keywords = [search.get_text().strip() for search in hot_searches[:50]]
        return keywords
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return []

def get_random_elements(array, num_elements):
    if num_elements > len(array):
        raise ValueError("数字元素的数量应小于或等于数组的长度")
    return random.sample(array, num_elements)

def process(driver, keywords, total_count):
    driver.get("https://www.bing.com")
    for count in range(total_count):
        search_query = auto_str_trans(keywords[count])
        print(f"【{count+1}/{total_count}】: {search_query}")
        perform_bing_search(driver, search_query)
        smooth_scroll_to_bottom(driver)
        time.sleep(random.uniform(10, 30))  # 等待10-30秒

def main():
    user_list = [
        "C:\\Users\\27217\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default",
        "C:\\Users\\27217\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 1",
        "C:\\Users\\27217\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 2",
        "C:\\Users\\27217\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 3",
        "C:\\Users\\27217\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 4",
    ]
    edge_driver_path = "D:\\myData\\Taki\\msedgedriver.exe"
    total_count = 32
    keywords = get_random_elements(get_baidu_hot_search(), total_count)
    
    # 使用 ThreadPoolExecutor 进行多线程处理
    with ThreadPoolExecutor(max_workers=user_list.count()) as executor:
        for user in user_list:
            driver = get_edge_driver(user, edge_driver_path)
            executor.submit(process, driver, keywords, total_count)
            time.sleep(2)  # 确保每个浏览器实例有时间启动

if __name__ == "__main__":
    main()
