
from scrapy.spiders import Spider
from scrapyspider.items import BaiKeItem
from scrapy import Request
from scrapy.selector import Selector
from urllib import parse
import re
import json

class BaiKeSpider(Spider):

    name = 'baike'
    urls=[]
    url_counter=0
    
    headers = {
        'User-Agent':
        'Mozilla/5.0 '
        '(Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }

    def start_requests(self):

        self.urls.append(parse.unquote('https://baike.baidu.com/item/%E5%A7%9A%E6%98%8E/28'))
        yield Request(self.urls[self.url_counter], headers=self.headers)




    def parse(self, response):
        sel = Selector(response)
        # sites = sel.xpath('//div[@class="main-content"]')
        item = BaiKeItem()
        
        p=re.compile('.*(\/item\/.*)')#！
        oid=p.match(self.urls[self.url_counter]).group(1)
        item['oid']=parse.unquote(oid)#把oid乱码部分解码为中文

        item['name'] = sel.xpath('//dd[@class="lemmaWgt-lemmaTitle-title"]/h1/text()').extract()

        summary_paras = response.xpath('//div[@class="lemma-summary"]').xpath('div[@class="para"]')
        summary = ""
        for para_node in summary_paras:
            seg_list = para_node.re('>\s*(.*?)\s*<')
            # os._exit(233)  PS:scrapy里的list object在python里并不是list type

            for seg in seg_list:
                summary = "%s%s"%(summary,seg)

        summary=summary.replace("\n","")

        item['descrip'] = re.sub('\[\d+\]','',summary)

        info_names = sel.xpath('//dt[@class="basicInfo-item name"]/text()').extract()
        info_values = []
        info_links=[]
        values_node=sel.xpath('//dd[@class="basicInfo-item value"]')
        for value_node in values_node:
            seg_list=value_node.re('>\s*(.*?)\s*<')
            value=""
            for seg in seg_list:
                value="%s%s"%(value,seg)
            info_values.append(value)

            #提取链接
            tmp_link_list=value_node.re('\"(\/item\/.*)\"')
            if len(tmp_link_list)==0:
                info_links.append('')
            else:
                info_links.append(parse.unquote(tmp_link_list[0]))
        item['infolink']=info_links
        
        count=0
        info_dict={}
        if len(info_names)!=len(info_values):
            print('Error in infobox: fail to match name and value')
        while count<len(info_names):
            tmp_name=info_names[count]
            tmp_value=info_values[count]
            info_dict[tmp_name.replace('\xa0','')]=tmp_value.replace('\xa0','')
            count+=1

        item['infobox']=json.dumps(info_dict, ensure_ascii=False)

        tag_node = sel.xpath('//dd[@id="open-tag-item"]/span')
        tag_list = []
        for tag_tmp in tag_node:
            tags = tag_tmp.re('>\s*(.*?)\s*<')
            x = ""
            for tag in tags:
                x = "%s%s" % (x, tag)
                # 如果存储了空串的话，把空串和有内容的字符串加起来就行
            tag_list.append(x)

        item['tag'] = tag_list
        # 开始保存多义词表

        poly_dict = {}
        polysemy = sel.xpath('//ul[@class="polysemantList-wrapper cmn-clearfix"]/li')

        for poly_tmp in polysemy:
            poly_nodes = poly_tmp.re('>\s*(.*?)\s*<')
            poly_name = ""
            for poly_node in poly_nodes:
                poly_name = "%s%s"%(poly_name,poly_node)
            poly_url = poly_tmp.xpath('./a/@href').extract()
            poly_url = " ".join(list(poly_url))
            poly_url = poly_url.replace("#viewPageContent", "")
            poly_dict[poly_name] = parse.unquote(poly_url)

        item['polysemy'] = poly_dict






        keys = ['name', 'descrip', 'infobox', 'infolink', 'tag', 'oid']
        for key in keys:
            item[key] = str(item[key]).replace('\n', '')  # 转换为字符串，好存进数据库

        yield item
        
        self.url_counter+=1

        # extract links"/item..."注意链接此处还没有解码
        links = []
        for link in sel.xpath('//link/@href').re('.*\/item\/.*'):
            links.append(link)
        for link in sel.xpath('//a[@href]/@href').re('\/item\/.*'):
            links.append("https://baike.baidu.com%s"%link)

        # print(links)

        for link in links:
            unquote_link=parse.unquote(link)
            self.urls.append(unquote_link)            
            request=Request(url=unquote_link,callback=self.parse,headers=self.headers,encoding='utf-8')
            yield request










