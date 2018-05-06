from scrapy.spiders import Spider
from scrapyspider.items import BaiKeItem, PicturesItem
from scrapy import Request
from scrapy.selector import Selector
from urllib import parse
import re
import json
from scrapyspider import pipelines

# import time


# import win_unicode_console
#
# win_unicode_console.enable()

# Linux不用加


class BaiKeSpider(Spider):
    name = 'baike'

    headers = {
        'User-Agent':
            'Mozilla/5.0 '
            '(Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapyspider.pipelines.BaiKeSpiderPipeline': 300
        }
    }
    def __init__(self):
        self.sqls = pipelines.BaiKeSpiderPipeline()
        # self.sqls.create_entity_table('entity_table')
        # self.sqls.create_polysemant_table('synonym_table')

    def start_requests(self):
        urls = ['https://baike.baidu.com/item/%E9%B2%81%E8%BF%85/36231',
                'https://baike.baidu.com/item/%E9%98%BF%E5%B0%94%E4%BC%AF%E7%89%B9%C2%B7%E7%88%B1%E5%9B%A0%E6%96%AF%E5%9D%A6',
                'https://baike.baidu.com/item/苹果公司/304038',
                'https://baike.baidu.com/item/%E5%A7%9A%E6%98%8E/28',
                'https://baike.baidu.com/item/里奥·梅西/4443471',
                'https://baike.baidu.com/item/%E7%9A%87%E5%AE%B6%E9%A9%AC%E5%BE%B7%E9%87%8C%E8%B6%B3%E7%90%83%E4%BF%B1%E4%B9%90%E9%83%A8/4606558',
                'https://baike.baidu.com/item/国际足联世界杯/7872861',
                'https://baike.baidu.com/item/欧洲冠军联赛/4256767',
                'https://baike.baidu.com/item/勒布朗·詹姆斯/1989503',
                'https://baike.baidu.com/item/%E7%BE%BD%E6%AF%9B%E7%90%83/32511',
                'https://baike.baidu.com/item/%E8%A3%B3%E5%87%A4%E8%9D%B6',
                'https://baike.baidu.com/item/%E9%93%81%E6%A0%91/110475',
                'https://baike.baidu.com/item/%E5%B9%BF%E5%BA%9C%E6%96%87%E5%8C%96',
                'https://baike.baidu.com/item/%E8%B4%9D%E5%8B%92%E5%A4%A7%E5%AD%A6',
                'https://baike.baidu.com/item/%E6%9B%B9%E6%93%8D/6772',
                'https://baike.baidu.com/item/%E8%88%9F%E5%B1%B1',
                'https://baike.baidu.com/item/%E6%AF%9B%E7%BB%86%E8%A1%80%E7%AE%A1',
                'https://baike.baidu.com/item/绿日/1491833',
                'https://baike.baidu.com/item/%E7%89%9B%E8%82%89%E4%B8%B8',
                'https://baike.baidu.com/item/%E4%BA%9A%E4%BC%AF%E6%8B%89%E7%BD%95%C2%B7%E6%9E%97%E8%82%AF/25619',
                'https://baike.baidu.com/item/%E5%A7%AC%E5%8F%91/529116',
                'https://baike.baidu.com/item/%E9%98%BF%E5%9F%BA%E7%B1%B3%E5%BE%B7/121228',
                'https://baike.baidu.com/item/%E9%B2%81%E8%BF%85/36231',
                'https://baike.baidu.com/item/%E5%88%9D%E9%9F%B3%E6%9C%AA%E6%9D%A5/8231955',
                'https://baike.baidu.com/item/%E9%B2%81%E4%BC%AF%E7%89%B9%C2%B7%E9%BB%98%E5%A4%9A%E5%85%8B/4172117',
                'https://baike.baidu.com/item/%E6%B2%83%E4%BC%A6%C2%B7%E5%B7%B4%E8%8F%B2%E7%89%B9'
                ]

        for url in urls:
            yield Request(url, headers=self.headers)
            # yield Request(url, headers=self.headers,dont_filter=True)
            # scrapy会对request的URL去重(RFPDupeFilter)，加上dont_filter则告诉它这个URL不参与去重

    def parse(self, response):
        sel = Selector(response)
        # sites = sel.xpath('//div[@class="main-content"]')
        item = BaiKeItem()

        current_url = response.url

        p = re.compile('.*(\/item\/[^\?]+).*')  # 去掉无意义的？及后面的部分

        oid = p.match(current_url).group(1)
        oid = oid.replace("#viewPageContent", "")
        item['oid'] = parse.unquote(oid)  # 把oid乱码部分解码为中文
        # 1.保存当前页面的url，通过调用response对象的url来找到当前页面的url
        item['name'] = sel.xpath('//dd[@class="lemmaWgt-lemmaTitle-title"]/h1/text()').extract()[0]
        # 2.找到该词条的name，直接通过xpath方法找到相应的词条名字
        summary_paras = response.xpath('//div[@class="lemma-summary"]').xpath('div[@class="para"]')
        # 3. 开始保存该词条的简介，因为简介的文本内容是由多个标签的文本内容组成，所以我们先找到简介的父节点
        summary = ""
        for para_node in summary_paras:
            seg_list = para_node.re('>\s*(.*?)\s*<')
            # 3.1 通过正则找到><标签的内容 \s是匹配任何空白字符
            # os._exit(233)  PS:scrapy里的list object在python里并不是list type

            for seg in seg_list:
                summary = "%s%s" % (summary, seg)
            # 3.2 把分割的内容连接成字符串，'%s%d'%('spider',1)相当于'spider1'，%s是替换字符串，%d是替换数字

        summary = summary.replace("\n", "")
        # 3.3 把字符串里面的\n替换掉
        item['descrip'] = re.sub('\[\d+\]', '', summary)
        # 3.4 用正则把summary中的形如[1][2]去掉，保存在item里面
        info_names = sel.xpath('//dt[@class="basicInfo-item name"]/text()').extract()
        # 4.1 找到info_box name的节点
        info_values = []
        info_links = []
        # 4.2 创建列表
        values_node = sel.xpath('//dd[@class="basicInfo-item value"]')
        # 4.3 找到value值的父节点
        for value_node in values_node:
            seg_list = value_node.re('>\s*(.*?)\s*<')
            # 4.4 找到每个节点的value值
            value = ""
            for seg in seg_list:
                value = "%s%s" % (value, seg)
            # 4.5 把value值连起来
            info_values.append(value)
            # 4.6 加入values列表里面

            # 提取链接
            tmp_link_list = value_node.re('\"(\/item\/[^\"]+)\"')
            p = re.compile('(\/item\/[^\?]+).*')  # 去掉引号,以及?等无意义部分
            # 5.1 用正则找info_box里面的链接 形如 "/item/123456" 这样的地方
            if len(tmp_link_list) == 0:
                info_links.append('')
            else:
                info_links.append(p.match(parse.unquote(tmp_link_list[0])).group(1))
                # 5.2 保存链接到列表前先转码

        item['infolink'] = info_links

        count = 0
        info_dict = {}
        # 6.开始保存info_box
        if len(info_names) != len(info_values):
            print('Error in infobox: fail to match name and value')
        while count < len(info_names):
            tmp_name = info_names[count]
            tmp_value = info_values[count]
            info_dict[tmp_name.replace('\xa0', '')] = tmp_value.replace('\xa0', '')
            # 6.1开始组成字典形式 info_dict[name]=value,\xa0是为了替换掉空格
            count += 1

        item['infobox'] = json.dumps(info_dict, ensure_ascii=False)
        # 6.2 json.dumps 是把dict格式转化成str模式，想输出真正的中文需要指定ensure_ascii=False，不然是输出的中文编码
        tag_node = sel.xpath('//dd[@id="open-tag-item"]/span')
        # 7.开始保存标签
        tag_list = []
        for tag_tmp in tag_node:
            tags = tag_tmp.re('>\s*(.*?)\s*<')
            x = ""
            for tag in tags:
                x = "%s%s" % (x, tag)
                # 如果存储了空串的话，把空串和有内容的字符串加起来就行
            tag_list.append(x)

        item['tag'] = tag_list
        # 8.开始保存多义词表

        poly_dict = {}
        polysemy = sel.xpath('//ul[@class="polysemantList-wrapper cmn-clearfix"]/li')

        first_poly_run = True

        for poly_tmp in polysemy:
            poly_nodes = poly_tmp.re('>\s*(.*?)\s*<')
            poly_name = ""
            for poly_node in poly_nodes:
                poly_name = "%s%s" % (poly_name, poly_node.replace('▪', ''))
            if first_poly_run is True:
                poly_url = item['oid']
                poly_dict[poly_name] = parse.unquote(poly_url)
                first_poly_run = False
            else:
                poly_url = poly_tmp.xpath('./a/@href').extract()
                poly_url = " ".join(list(poly_url))
                poly_url = poly_url.replace("#viewPageContent", "")
                poly_dict[poly_name] = parse.unquote(poly_url)

        item['polysemy'] = poly_dict

        keys = ['name', 'descrip', 'infobox', 'infolink', 'tag', 'oid']
        for key in keys:
            item[key] = str(item[key]).replace('\n', '')  # 转换为字符串，好存进数据库

        yield item

        # extract links"/item..."注意链接此处还没有解码
        # 9.下一步的跳转，找到所有可以跳转的链接
        links = []
        for link in sel.xpath('//link/@href').re('.*\/item\/.*'):
            links.append(link)
        for link in sel.xpath('//a[@href]/@href').re('\/item\/.*'):
            links.append("https://baike.baidu.com%s" % link)

        # print(links)

        for link in links:
            unquote_link = parse.unquote(link)
            request = Request(url=unquote_link, callback=self.parse, headers=self.headers, encoding='utf-8')

            yield request

class PicturesSpider(Spider):
    name = 'pic'
    headers = {
        'User-Agent':
            'Mozilla/5.0 '
            '(Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapyspider.pipelines.PictureUrlsPipeline': 400,
            'scrapyspider.pipelines.PicturePipeline': 500
        }
    }
    counts_and_oids={}#使用字典存储当前图片的序号和oid，以便命名
    def __init__(self):
        self.pics=pipelines.PictureUrlsPipeline()#sqls可调用pipeline的函数

        # self.img_urls=[]

    def start_requests(self):
        count=1
        maxWantID=100000
        while count <= maxWantID:
            oid = parse.quote(self.pics.get_oid("entity_table", count))
            self.counts_and_oids[oid]=str(count) #避免后期存储入文件夹时，斜杠被当做路径分割符号
            page_url = "%s%s" % ("https://baike.baidu.com", oid)
            print("page_url:",page_url)
            request=Request(page_url, headers=self.headers,callback=self.parse, encoding='utf-8')
            yield request
            count+=1

    def parse(self, response):
        item=PicturesItem()
        sel = Selector(response)

        if len(response.xpath('//div[@class="summary-pic"]/a/img/@src'))==0:#判断该页是否有图片
            item['image_urls']="none"
            item['image_name']="none"
        else:
            img_url=sel.xpath('//div[@class="summary-pic"]/a/img/@src').extract()[0]
            print('image_url appended:',img_url)
            item['image_urls']=img_url

            oid_pattern=re.compile('https://baike.baidu.com(.*)')#提取oid
            m=oid_pattern.match(response.url)
            oid=m.group(1)
            img_count=self.counts_and_oids[oid]

            item['image_name']="%s.%s"%(parse.unquote(oid.replace("/","_")),"1")

            print(item['image_name'])

        # ticks = time.time()
        # 当前时间


        yield item


