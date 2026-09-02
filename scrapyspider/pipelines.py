# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import re
import sys

import pymysql.cursors
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings


class BaiKeSpiderPipeline(object):
    '''保存到数据库中对应的class
       1、在settings.py文件中配置
       2、在自己实现的爬虫类中yield item,会自动执行'''

    def __init__(self):
        # Keep credentials outside source control. The defaults are suitable
        # for a local MySQL development instance and can be overridden with
        # the BAIKESPIDER_DB_* environment variables documented in README.md.
        self.dbparams = {
            'host': os.getenv('BAIKESPIDER_DB_HOST', '127.0.0.1'),
            'port': int(os.getenv('BAIKESPIDER_DB_PORT', '3306')),
            'user': os.getenv('BAIKESPIDER_DB_USER', 'root'),
            'password': os.getenv('BAIKESPIDER_DB_PASSWORD', ''),
            'db': os.getenv('BAIKESPIDER_DB_NAME', 'scrapy_baike'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
        }

    def execute_sql(self, sql):
        # 连接数据库，存到t中
        self.db = pymysql.connect(**self.dbparams)
        self.cursor = self.db.cursor()

        try:
            self.cursor.execute("SET NAMES 'utf8mb4';")
            self.cursor.execute("SET CHARACTER SET 'utf8mb4';")
            self.cursor.execute("SET character_set_connection=utf8mb4")
            self.cursor.execute(sql)
            self.db.commit()
            affected_rows = self.cursor.rowcount
            self.db.close()
            return affected_rows
        except Exception:
            print("ERR in sql execution!!; The sql is {}".format(sql))
            self.db.rollback()
            self.db.close()
            raise

    def deal_with_quotes(self, processed_str):  # 处理插入MySQL的引号问题
        return processed_str.replace("\"", "\\\"").replace("\'", "\\\'")

    def create_entity_table(self, table_name):  # datas is a dictionary
        sql = """
        CREATE TABLE %s(
        id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        oid         TEXT NOT NULL,
        name        TEXT NOT NULL,
        descrip     TEXT NOT NULL,
        infobox     TEXT,
        infolink   TEXT,
        tag         TEXT
        );
        """ % table_name
        self.execute_sql(sql)

        sql_db = """
        ALTER DATABASE %s CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
        """ % self.dbparams['db']
        self.execute_sql(sql_db)

    def create_polysemant_table(self, table_name, ):
        sql = """
        CREATE TABLE %s(
        id      BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        name    TEXT NOT NULL,
        descrip TEXT NOT NULL,
        oid     TEXT NOT NULL
        );
        """ % table_name
        self.execute_sql(sql)

    def exists_in_table(self, table_name, attribute_name, value_name):
        sql = """
        SELECT * FROM
        %s
        WHERE %s="%s" ;
        """ % (table_name, attribute_name, self.deal_with_quotes(value_name))
        if self.execute_sql(sql) == 0:
            return False
        else:
            return True

    def add_a_value(self, table_name, attributes):
        count = 0
        names = ""
        values = ""
        firstRun = True

        try:
            for name, value in attributes.items():
                name = str(name)
                value = str(value)
                if count >= len(attributes):
                    break

                if firstRun is False:
                    names = "%s,%s" % (names, name)
                    values = "%s,\"%s\"" % (values, self.deal_with_quotes(value))
                else:
                    names = "%s" % name
                    values = "\"%s\"" % self.deal_with_quotes(value)
                    firstRun = False
                count += 1
        except Exception:
            raise

        sql = """
        INSERT INTO %s(%s)
        VALUES
        (%s);
       """ % (table_name, names, values.replace("\\\\\"", "\\\""))
        self.execute_sql(sql)

    # pipeline默认调用
    def process_item(self, item, spider):
        data_dict = dict(item)

        self.entity_tbl_name = 'entity_table'
        entity_data_types = ['oid', 'name', 'descrip', 'infobox', 'infolink', 'tag']
        entity_data_dict = {}
        for t in entity_data_types:
            entity_data_dict[t] = data_dict[t]
        if self.exists_in_table(self.entity_tbl_name, 'oid', data_dict['oid']) is False:
            self.add_a_value(self.entity_tbl_name, entity_data_dict)
        else:
            print('Warning: This item already exists in entity_table !! (checked by oid)')

        self.synonym_tbl_name = 'synonym_table'
        if self.exists_in_table(self.synonym_tbl_name, 'name', data_dict['name']) is True:
            print('这个意思的同义词已经存入')
        else:
            polysemants_dict = data_dict['polysemy']
            for meaning, oid in polysemants_dict.items():
                if self.exists_in_table(self.synonym_tbl_name, 'oid', oid) is False:
                    self.add_a_value(self.synonym_tbl_name, {'name': data_dict['name'], 'descrip': meaning, 'oid': oid})
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

    # 存储图片到数据库
    baiduPipelines = BaiKeSpiderPipeline()
    dbparams = baiduPipelines.dbparams
    execute_sql = baiduPipelines.execute_sql
    deal_with_quotes = baiduPipelines.deal_with_quotes
    before_insert_img = True

    def add_an_attribute(self, table_name, attribute_name, attribute_type):
        sql = """
        ALTER TABLE %s
        ADD %s %s;
        """ % (table_name, attribute_name, attribute_type)
        self.execute_sql(sql)

    def read_file(self, filename):
        with open(filename, 'rb') as f:
            picture = f.read()
        return picture

    def insert_img(self, img_name, img_oid, table_name="entity_table", attribute_name="image_list"):
        img_list = []
        img_list.append(img_name)

        sql = """
        UPDATE %s
        SET %s=\'%s\'
        WHERE oid=\'%s\';
        """ % (table_name, attribute_name, self.deal_with_quotes(str(img_list)), self.deal_with_quotes(img_oid))
        print("update", sql)

        self.execute_sql(sql)

    def get_media_requests(self, item, info):
        image_url = item['image_urls']
        self.default_headers['referer'] = image_url
        if image_url != "none":
            yield Request(image_url, meta={'image_name': item['image_name']}, headers=self.default_headers)

    def item_completed(self, results, item, info):
        settings = get_project_settings()
        images_dir_path = settings.get('IMAGES_STORE')

        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        else:
            image_path = image_paths[0]
            oid_pattern = re.compile("full\/([^\.]+)\.\d+\.jpg")
            m = oid_pattern.match(image_path)
            oid = m.group(1)

            name_pattern = re.compile("full\/([^\.]+\.(\d+)\.jpg)")
            name = name_pattern.match(image_path).group(1)

            self.insert_img(name, oid.replace("_", "/"))

        item['images_paths'] = image_paths
        return item

    def file_path(self, request, response=None, info=None):
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

    baiduPipelines = BaiKeSpiderPipeline()
    dbparams = baiduPipelines.dbparams

    def execute_sql(self, sql):
        self.db = pymysql.connect(**self.dbparams)
        self.cursor = self.db.cursor()

        try:
            self.cursor.execute('SET NAMES utf8mb4')
            self.cursor.execute("SET CHARACTER SET utf8mb4")
            self.cursor.execute("SET character_set_connection=utf8mb4")
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            self.db.commit()
            self.db.close()
            return result
        except Exception:
            print("ERR in sql execution!!; The sql is {}".format(sql))
            self.db.rollback()
            self.db.close()
            raise

    def max_id(self, table_name):
        sql = """
        SELECT MAX(id) FROM %s;
        """ % table_name
        result = int(float(self.execute_sql(sql)['MAX(id)']))
        print("the max_id is ", result)
        if result <= 0:
            print('Err in get max_id: got max id <= 0')
            sys.exit(233)
        else:
            return result

    def get_oid(self, table_name, id):
        tbl_max_id = self.max_id(table_name)
        if id > tbl_max_id:
            print("ERR: The id you give is to big! No such row")
            sys.exit(233)

        sql = """
        SELECT oid FROM %s
        WHERE id=%s;
        """ % (table_name, id)
        return self.execute_sql(sql)['oid']


