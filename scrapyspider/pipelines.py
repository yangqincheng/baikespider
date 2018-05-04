# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql.cursors
import sys
from scrapy import Request

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings

import re
import os

class BaiKeSpiderPipeline(object):
    '''保存到数据库中对应的class
       1、在settings.py文件中配置
       2、在自己实现的爬虫类中yield item,会自动执行'''

    def __init__(self):
        self.dbparams = {
            'host':'127.0.0.1',
            'port': 3306,
            # 'user': 'root',
            # 'password': '1240',
            'user': 'yqc',
            'password': '123456',
            'db': 'scrapy_baike',
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
        }



    def execute_sql(self,sql):

        # 连接数据库，存到t中
        self.db = pymysql.connect(**self.dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        self.cursor = self.db.cursor()

        try:
            self.cursor.execute("SET NAMES 'utf8mb4';")
            self.cursor.execute("SET CHARACTER SET 'utf8mb4';")
            self.cursor.execute("SET character_set_connection=utf8mb4")
            # 执行sql语句

            if self.cursor.execute(sql) != 1:
                print("Warning: fetch too many attributes for randow data!!By default excute_sql just return one row's data")
            #
            # rows = self.cursor.fetchall()
            # for row in rows:
            #     for data in row:
            #         if data is None:
            #             continue
            #         else:
            #             # 关闭数据库连接
            #             self.db.close()
            #             return data
            self.db.commit()
            # 提交到数据库执行
            
            self.db.close()# 关闭数据库
            return self.cursor.rowcount# 返回cursor运行过程中affected rows的数量
        except:
            # 如果发生错误则回滚
            print("ERR in sql execution!!; The sql is {}".format(sql))
            self.db.rollback()
            sys.exit(233)




    def deal_with_quotes(self,processed_str):#处理插入MySQL的引号问题
        return processed_str.replace("\"","\\\"").replace("\'","\\\'")

    def create_entity_table(self,table_name):#datas is a dictionary
        sql="""
        CREATE TABLE %s(
        id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        oid         TEXT NOT NULL,
        name        TEXT NOT NULL,
        descrip     TEXT NOT NULL,
        infobox     TEXT,
        infolink   TEXT,
        tag         TEXT    
        );
        """%table_name
        self.execute_sql(sql)

        sql_db="""
        ALTER DATABASE %s CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
        """%self.dbparams['db']
        self.execute_sql(sql_db)

    def create_polysemant_table(self,table_name,):
        sql="""
        CREATE TABLE %s(
        id      BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        name    TEXT NOT NULL,
        descrip TEXT NOT NULL,
        oid     TEXT NOT NULL
        );
        """%table_name
        self.execute_sql(sql)

    def exists_in_table(self,table_name,attribute_name,value_name):
        sql="""
        SELECT * FROM 
        %s
        WHERE %s="%s" ;
        """%(table_name,attribute_name,self.deal_with_quotes(value_name))
        if self.execute_sql(sql)==0:
            return False
        else:
            return True

    def add_a_value(self,table_name,attributes):
        count=0
        names=""
        values=""
        firstRun=True

        try:
            for name,value in attributes.items():
                name=str(name)
                value=str(value)
                if count>=len(attributes):
                    break

                if firstRun is False:
                    names="%s,%s"%(names,name)
                    values="%s,\"%s\""%(values,self.deal_with_quotes(value))
                else:
                    names="%s"%name
                    values="\"%s\""%self.deal_with_quotes(value)
                    firstRun=False
                count+=1
        except:
            sys.exit(104)

        sql = """
        INSERT INTO %s(%s)
        VALUES
        (%s);
       """ % (table_name, names, values.replace("\\\\\"","\\\""))
        self.execute_sql(sql)

    # pipeline默认调用
    def process_item(self, item, spider):
        data_dict=dict(item)

        self.entity_tbl_name='entity_table'
        entity_data_types=['oid','name','descrip','infobox','infolink','tag']
        entity_data_dict={}
        for t in entity_data_types:
            entity_data_dict[t]=data_dict[t]
        if self.exists_in_table(self.entity_tbl_name,'oid',data_dict['oid']) is False:
            self.add_a_value(self.entity_tbl_name,entity_data_dict)
        else:
            print('Warning: This item already exists in entity_table !! (checked by oid)')

        self.synonym_tbl_name='synonym_table'
        if self.exists_in_table(self.synonym_tbl_name,'name',data_dict['name']) is True:
            print('这个意思的同义词已经存入')
        else:
            polysemants_dict=data_dict['polysemy']
            for meaning, oid in polysemants_dict.items():
                if self.exists_in_table(self.synonym_tbl_name,'oid',oid) is False:
                    self.add_a_value(self.synonym_tbl_name,{'name':data_dict['name'],'descrip':meaning,'oid':oid})
                else:
                    print('Warning: the meaning/oid already exists in ')

        return item

class PicturePipeline(ImagesPipeline):
    default_headers = {
        'accept': 'image/webp,image/*,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'cookie': 'bid=yQdC/AzTaCw',
        'referer': 'https://www.douban.com/photos/photo/2370443040/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    }

    #存储图片到数据库
    baiduPipelines = BaiKeSpiderPipeline()  # 引用前一个pipelline的各项功能
    dbparams = baiduPipelines.dbparams
    execute_sql = baiduPipelines.execute_sql
    deal_with_quotes=baiduPipelines.deal_with_quotes
    before_insert_img=True

    def add_an_attribute(self,table_name, attribute_name,attribute_type):
        sql="""
        ALTER TABLE %s
        ADD %s %s;
        """% (table_name,attribute_name,attribute_type)
        self.execute_sql(sql)

    def read_file(self,filename):
        with open(filename, 'rb') as f:
            picture = f.read()
        return picture

    def insert_img(self,img_name,img_oid,table_name="entity_table",attribute_name="image_list"):
        img_list=[]
        img_list.append(img_name)

        #将图片插入实体表
        sql="""
        UPDATE %s
        SET %s=\'%s\'
        WHERE oid=\'%s\';
        """%(table_name,attribute_name,self.deal_with_quotes(str(img_list)),self.deal_with_quotes(img_oid))
        print("update",sql)

        self.execute_sql(sql)

    def get_media_requests(self, item, info):
        image_url = item['image_urls']
        self.default_headers['referer'] = image_url
        if image_url != "none":
            yield Request(image_url, meta = {'image_name': item['image_name']}, headers=self.default_headers)
        # meta = {'image_name': item['image_name']},

    def item_completed(self, results, item, info):
        settings=get_project_settings()
        images_dir_path=settings.get('IMAGES_STORE')#找到存储图片的根目录

        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        else:
            image_path=image_paths[0]
            oid_pattern=re.compile("full\/([^\.]+)\.\d+\.jpg")
            m=oid_pattern.match(image_path)
            oid=m.group(1)#图片的count值，对应数据库中的id值

            name_pattern=re.compile("full\/([^\.]+\.(\d+)\.jpg)")
            name=name_pattern.match(image_path).group(1)

            self.insert_img(name,oid.replace("_","/"))

        item['images_paths'] = image_paths
        return item

    def file_path(self, request, response=None, info=None):
        # tmp = request.url.split('/')[-1]
        # # name = tmp+".jpg"
        # return 'full/%s' % (tmp)
        return 'full/%s.jpg' % request.meta['image_name']

class PictureUrlsPipeline(object):
    '''保存到百度百科的词条图片
       1、从数据库中提取oid
       2、检查id是否越界
    '''

    default_headers = {
        'accept': 'image/webp,image/*,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'cookie': 'bid=yQdC/AzTaCw',
        'referer': 'https://www.douban.com/photos/photo/2370443040/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    }

    baiduPipelines=BaiKeSpiderPipeline()#引用前一个pipelline的各项功能
    dbparams=baiduPipelines.dbparams
    def execute_sql(self,sql):

        # 连接数据库，存到t中
        self.db = pymysql.connect(**self.dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        self.cursor = self.db.cursor()

        try:
            self.cursor.execute('SET NAMES utf8mb4')
            self.cursor.execute("SET CHARACTER SET utf8mb4")
            self.cursor.execute("SET character_set_connection=utf8mb4")
            # 执行sql语句

            if self.cursor.execute(sql) != 1:
                print("Warning: fetch too many attributes for randow data!!By default excute_sql just return one row's data")
            
            self.db.commit()
            # 提交到数据库执行

            self.db.close()
            return self.cursor.fetchone()#fetchone()只返回sql语句执行的结果中的第一行（字典形式），如：self.cursor.fetchone()['oid']对应此行的oid
        except:
            # 如果发生错误则回滚
            print("ERR in sql execution!!; The sql is {}".format(sql))
            self.db.rollback()
            sys.exit(233)

    def max_id(self, table_name):#找出最大的id值
        sql = """
        SELECT MAX(id) FROM %s;
        """ % table_name
        result=int(float(self.execute_sql(sql)['MAX(id)']))#MySQL默认返回的是浮点类型
        print("the max_id is ",result)
        if result <= 0:
            print('Err in get max_id: got max id <= 0')
            sys.exit(233)
        else:
            return result

    def get_oid(self, table_name, id):
        tbl_max_id=self.max_id(table_name)
        if id > tbl_max_id:#检查id是否越界
            print("ERR: The id you give is to big! No such row")
            sys.exit(233)

        sql = """
        SELECT oid FROM %s
        WHERE id=%s;
        """ % (table_name, id)
        return self.execute_sql(sql)['oid']#注意fetchone返回的是字典类型


