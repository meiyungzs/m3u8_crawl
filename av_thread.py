import re
import time
import urllib
from urllib import request
from lxml import html
import os
import threading

# 主页，暂时未用到，可以手动访问，查找到喜欢的movie_url
index_url = "http://777tv.co"
headers = ('User-Agent',
           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')
path = "F:/mPicture/video/sexy2/"

class Crawl_video(object):

    def __init__(self):
        # 视频下载的url
        self.download_url = ""
        # .ts 文件数
        self.num = 0
        # 下载的文件存储路径
        self.path = path

    def callbackfunc(self, blocknum, blocksize, totalsize):
        '''回调函数
        用于request.rlretrieve() 方法的获取远程文件时的进度显示
        @blocknum: 已经下载的数据块
        @blocksize: 数据块的大小
        @totalsize: 远程文件的大小
        '''
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
        print("\r" + "%.2f%%" % percent, end="")

    def get_url0(url):
        """
        自定义的一个封装方法
        :param url:
        :return:
        """
        request = urllib.request.Request(url=url, method="GET")
        request.add_header(headers[0], headers[1])

        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError as e:
            print(e.reason)

        html_page = response.read().decode()

        return html_page

    def get_url(self, movie_url):
        """
        获取视频下载的url
        :return
        """
        html_page = Crawl_video.get_url0(url=movie_url)

        # with open("page.txt",'w',encoding='utf-8') as f:
        #     f.write(html_page)

        selector = html.etree.HTML(html_page)
        content = selector.xpath('//video[@id="video"]/source[1]/@src')
        # 获取m3u8地址文件的url
        down_url = str(content[0])

        opener = request.build_opener()
        opener.addheaders = [headers]
        request.install_opener(opener)
        request.urlretrieve("http:" + down_url, self.path + "m3u8_address.txt")
        # 获取的m3u8文件的url保存在 m3u8_address.txt 中

        # # 使用正则表达式匹配 m3u8_address.txt 中的 url，然后交给get_video(url)下载
        with open(self.path + "m3u8_address.txt", 'r') as f:
            content = f.readlines()[-2]
        res = re.search('(?P<url>^http://.+?video)(?P<num>\d{3})', content)
        urlandNum = res.groups()

        self.download_url = str(urlandNum[0])
        self.num = int(urlandNum[1])

    def get_video(self, url_num):
        """
        通过get_url方法获取的url下载video
        :return:
        """
        opener = request.build_opener()
        opener.addheaders = [headers]
        request.install_opener(opener)

        # for i in range(1, self.num + 1):
        #     num = str("%03d" % i)  # 相同位数数字，如001,002,010,110
        #     try:
        #         request.urlretrieve(self.download_url + num + ".jpg", self.path + num + ".ts", self.callbackfunc)
        #     except:
        #         print("未获取到第 %s 条内容" % i)
        #         continue
        #     else:
        #         print("\t获取第 %s 条内容成功" % i)

        num = str("%03d" % url_num)  # 相同位数数字，如001,002,010,110
        try:
            request.urlretrieve(self.download_url + num + ".jpg", self.path + num + ".ts", self.callbackfunc)
        except:
            print("未获取到第 %s 条内容" % url_num)
        else:
            print("\t获取第 %s 条内容成功" % url_num)


def combine():  # 组合资源方法
    """
        将下载的 .ts 视频文件合并为一个大的.mp4文件
       合并方法：
       可以通过cmd命令的方式将所有的ts合并成一个文件：
       copy /b d:\download_ts\*   d:\download_ts\new.mp4
    """
    try:
        print("开始组合资源...")
        os.chdir(path)
        copy_str = r'copy /b "' + path + r'*.ts" "' + path + 'new_video.mp4"'
        os.system(copy_str)  # 使用cmd命令将资源整合

        del_str = r'del "' + path + r'*.ts"'
        os.system(del_str)  # 删除原来的文件
    except:
        print("资源组合失败")
    else:
        print("资源组合成功!")


# 多线程爬取视频
def app(m_url):
    video = Crawl_video()
    video.get_url(m_url)
    # 多线程下载
    threads= []
    for i in range(0, video.num + 1):
        th = threading.Thread(target=video.get_video, args=[i])
        threads.append(th)
        # 设置守护进程，主线程等待子线程都结束后再结束
        th.setDaemon(True)
        th.start()
    for item in threads:
        item.join()

if __name__ == "__main__":
    start_time = time.time()
    # 通过主页获取的进入一个movie详情页面的url
    movieUrl = "http://777tv.co/video/1494/%E7%BE%8E%E6%9C%88%E3%82%A2%E3%83%B3%E3%82%B8%E3%82%A7%E3%83%AA%E3%82%A2%E3%81%AE%E7%A5%9E%E3%83%86%E3%82%AF%E3%82%92%E6%88%91%E6%85%A2%E3%81%A7%E3%81%8D%E3%81%9F%E3%82%89%E7%94%9F%E4%B8%AD%E5%87%BA%E3%81%97-%E7%BE%8E%E6%9C%88%E3%82%A2%E3%83%B3%E3%82%B8%E3%82%A7%E3%83%AA%E3%82%A2-092118-757"
    app(movieUrl)
    # combine()
    print('主线程结束了！', threading.current_thread().name)
    print('一共用时：', time.time() - start_time)
