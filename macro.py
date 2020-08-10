from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep

FIRST_KEYWORD = []
SECOND_KEYWORD = []

# 네이버 검색 시 블로그탭에서 찾으려는 text
BLOG_KEYWORD = []
# 구글 검색 시 찾고자하는 링크 일부
GOOGLE_KEYWORD = []

# 네이버 블로그 몇 페이지까지 검색할 것인지
NAVER_PAGE = 5
# 구글 블로그 몇 페이지까지 검색할 것인지
GOOGLE_PAGE = 5

def chromeOpen(): 
    options = webdriver.ChromeOptions()
    # secret 모드
    options.add_argument("--incognito")
    driver = webdriver.Chrome('./chromedriver', options=options)
    driver.implicitly_wait(3)
    return driver

def moveNaver(driver):
    driver.get("https://www.naver.com")
    # 해당 사이트 제목이 NAVER 확인
    assert "NAVER" in driver.title

def moveGoogle(driver):
    driver.get("https://www.google.com/")

def searchNaver(driver, viewType, keyword):
    if viewType == 0: # www.naver.com
        search_elem = driver.find_element_by_xpath("//input[@class='input_text']")
        # 천천히 검색하도록 
        for character in keyword:
            search_elem.send_keys(character)
            sleep(0.3)

        search_elem.submit()
    else: # 상세페이지에서 다시 검색하는 경우
        search_elem = driver.find_element_by_xpath("//input[@class='box_window']")
        # 천천히 검색하도록 
        search_elem.clear()

        for character in keyword:
            search_elem.send_keys(character)
            sleep(0.3)

        search_elem.submit()

    driver.implicitly_wait(3)

def searchGoogle(driver, keyword):
    search_elem = driver.find_element_by_xpath("//input[@title='검색']")
    search_elem.clear()
    # 천천히 검색하도록 
    for character in keyword:
        search_elem.send_keys(character)
        sleep(0.3)

    search_elem.submit()

def clickBlog(driver):
    # 블로그 클릭
    blog_elem = driver.find_element_by_xpath("//span[text()='블로그']")
    blog_elem.click()

    driver.implicitly_wait(3)

def closeTab(driver):
    # 현재 탭 종료
    driver.switch_to.window(driver.window_handles[1])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

def findKeyword(driver, keyword):
    page = NAVER_PAGE
    while(page):
        # 검색 결과 페이지에서 특정 문자열을 포함하는 링크 텍스트 찾기
        try:
            elem = driver.find_element_by_partial_link_text(keyword)
            elem.click()

            # 1분간 쉼
            sleep(60)
            closeTab(driver)
            return
        except NoSuchElementException:
            page -= 1
            try:
                next_elem = driver.find_element_by_xpath("//a[text()='다음페이지']")
                next_elem.click()
                driver.implicitly_wait(3)
            except NoSuchElementException:
                page = 0
                break

    if page == 0:
        print("❌ error: 현재 페이지에서", keyword, "를 찾을 수 없습니다.")

def findLink(driver, keyword):
    page = GOOGLE_PAGE
    while(page):
        try:
            path = "//a[contains(@href,'" + keyword + "')]"
            elem = driver.find_element_by_xpath(path)
            elem.click()

            # 1분간 쉼
            sleep(60)

            driver.back()
            return
        except NoSuchElementException:
            page -= 1
            try:
                next_elem = driver.find_element_by_xpath("//span[text()='다음']")
                next_elem.click()
                driver.implicitly_wait(3)
            except NoSuchElementException:
                page = 0
                break

    if page == 0:
        print("❌ error: 현재 페이지에서", keyword, "를 찾을 수 없습니다.")

def macroNaverBlog(driver):
    clickBlog(driver)
    for blogKeyword in BLOG_KEYWORD:
        findKeyword(driver, blogKeyword)

def macroNaver(driver, firstKeyword, secondKeyword):
    moveNaver(driver)
    searchNaver(driver, 0, firstKeyword)
    macroNaverBlog(driver)
    searchNaver(driver, 1, firstKeyword + ' ' + secondKeyword)
    macroNaverBlog(driver)
    driver.close()

def macroGoogle(driver, firstKeyword, secondKeyword):
    moveGoogle(driver)
    searchGoogle(driver, firstKeyword)
    for googleKeyword in GOOGLE_KEYWORD:
        findLink(driver, googleKeyword)
    searchGoogle(driver, firstKeyword + ' ' + secondKeyword)
    for googleKeyword in GOOGLE_KEYWORD:
        findLink(driver, googleKeyword)
    driver.close()

if __name__ == "__main__":
    while(1):
        idx = 0
        cnt = 2 * len(FIRST_KEYWORD) * len(SECOND_KEYWORD)
        for firstKeyword in FIRST_KEYWORD:
            for secondKeyword in SECOND_KEYWORD:
                driver = chromeOpen()
                idx += 1
                print("Naver - ", firstKeyword, secondKeyword, "검색 시작! 🍀 (", idx, "/", cnt , ")")
                macroNaver(driver, firstKeyword, secondKeyword)
                driver = chromeOpen()
                idx += 1
                print("Google - ", firstKeyword, secondKeyword, "검색 시작! 🐳 (", idx, "/", cnt , ")")
                macroGoogle(driver, firstKeyword, secondKeyword)
        
        # 30분마다 반복
        sleep(1800)
