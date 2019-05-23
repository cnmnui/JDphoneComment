import time
from selenium import webdriver
import csv
from fake_useragent import UserAgent
from lxml import etree


class JDSpider:
    def __init__(self):
        self.base_url = 'https://www.jd.com'
        ua = UserAgent()
        self.headers = {'UserAgent': ua.random}
        self.opt = webdriver.ChromeOptions()
        self.opt.set_headless()
        self.driver = webdriver.Chrome(options=self.opt)
        self.driver_comment = webdriver.Chrome(options=self.opt)
        self.key = '华为p20'

    # 列表下一页
    def click_button(self):
        if self.driver.page_source.find('pn-next disabled') == -1:
            self.driver.find_element_by_xpath('//*[@id="J_bottomPage"]/span[1]/a[9]/em').click()
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(1)
            res = self.driver.page_source
            self.parse_base_html(res)
        else:
            self.driver.quit()

    # 评论下一页
    def comment_next_click(self):
        if self.driver_comment.page_source.find('ui-pager-next') != -1:
            # 可能是这边网速的问题，这里老是提示无法点击
            self.driver_comment.find_element_by_class_name('ui-pager-next').click()
            time.sleep(1)
            res = self.driver.page_source
            self.parse_child_html(res)
        else:
            self.driver_comment.quit()

    # 读取商品列表页面
    def parse_base_html(self, res):
        par_res = etree.HTML(res)
        base_list = par_res.xpath('//*[@id="J_goodsList"]/ul/li/div')
        for base in base_list:
            goods_url = base.xpath('./div[@class="p-img"]/a/@href')[0]
            url = goods_url if "https:" in goods_url else 'https:' + goods_url
            self.driver_comment.get(url)
            time.sleep(1)
            self.driver_comment.find_element_by_xpath('//*[@id="detail"]/div[1]/ul/li[5]').click()
            self.driver_comment.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(2)
            goods_res = self.driver_comment.page_source
            self.parse_child_html(goods_res)
            print('开始解析商品评论')
        time.sleep(1)
        self.click_button()

    # 解析商品详情评论
    def parse_child_html(self, goods_res):
        parse_goods_res = etree.HTML(goods_res)
        goods_base_list = parse_goods_res.xpath('//*[@id="comment-0"]/div[@class="comment-item"]')
        for info in goods_base_list:
            username = info.xpath('./div[1]/div[1]/img/@alt')[0]
            star = info.xpath('./div[2]/div[1]/@class')[0][-5:]
            comment = info.xpath('./div[2]/p/text()')[0]
            print("解析成功")
            self.to_csv(username, star, comment)
        time.sleep(1)
        self.comment_next_click()

    def to_csv(self, username, star, comment):
        with open('aaa.csv', 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow((username, star, comment))
            print("写入成功")

    def work_on(self):
        self.driver.get(self.base_url)
        self.driver.find_element_by_id("key").send_keys(self.key)
        self.driver.find_element_by_class_name("button").click()
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        res = self.driver.page_source
        self.parse_base_html(res)


if __name__ == '__main__':
    spider = JDSpider()
    spider.work_on()

