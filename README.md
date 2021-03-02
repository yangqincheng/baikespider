# baikespider
BaiKe Spider

scrapy框架写的爬取百度百科的代码

数据库中一共有两张表 一张是实体表entity_table,一张是同名词表synonym_table，数据实体截图放在/picture文件夹下

保存的图片截图也放在/picture下

spider文件夹中的BaiDuSpider是最终的确定的结果，其余的DouBanSpider是开始学习时候看的demo，PictureSpider是开始爬取图片时用来测试的。

BaiDuSpider中有两个Spider 一个是用来获取百科词条的内容（词条名字，简介，相关领域等，可以参看数据库表的截图）和同义词之间的内容

代码内部有详细的注释

主要思想是我们从多个初始节点出发，保存当前页面我们需要保存的信息，然后把页面中的其他词条的链接作为下一跳。Scrapy框架本身有查重机制，我们在保存到数据库时也会再次查重（因为有同名词表）这是entity_table表收集的信息的主要思想

synonym_table表收集的信息的主要思想是从entity_table表中读取每个词条的url，然后保存当前的词条中的第一张词条图片，并改名为OID+编号的形式，OID是实体表entity_table中每项数据的唯一标识,来源于每个词条url后面的item/数字/

具体的操作文档也放在/picture文件夹下

操作部分：
1.实际项目中的代码目录是这样

![image](https://user-images.githubusercontent.com/23690625/109646793-7f3c4f80-7b93-11eb-9c22-d0ccfceeda70.png)

几个文件夹的含义
（1）	loginfo 这是由我们自己定义的用来保存爬虫当前运行状态的文件夹，位置由我们自己决定，这里我们用的相对路径，所以项目保存在运行起点的文件夹里。
（2）	pictures 是我们用来保存爬取的图片的文件夹，位置可以由我们自己修改，如果想要改变图片的存储路径，修改settings.py文件里的IMAGES_STORE。
如下图
![image](https://user-images.githubusercontent.com/23690625/109646839-8c593e80-7b93-11eb-8785-ce2fdff7ba17.png)

 (3)  spiders文件夹存储我们写的spider文件
 2.启动爬虫需要在命令行中启动，启动的路径取决于scrapy.cfg 文件所在的位置

比如在我电脑中scrapy.cfg 文件位于 ![image](https://user-images.githubusercontent.com/23690625/109646881-9d09b480-7b93-11eb-887c-088d56fd8069.png)
,那么我启动的位置就该在这个地方

启动的命令
Name 是一个爬虫的唯一标识，百科的爬虫的name就是 baike， 图片爬虫的name就是pic,JOBDIR 后面就是我们存储爬虫当前运行状态的路径（注意这里每个爬虫当前信息的保存路径不能是一样的）所以如果要在自己的地方运行，那么启动命令就应该这么写

上面是启动命令，如果我们需要暂时结束今天的爬虫任务，那么我们只需要在命令行中使用按下 ctrl+c 就行（注意按下之后需要等大概10秒,出现类似下图的图片就可以终止了）

![image](https://user-images.githubusercontent.com/23690625/109646920-a8f57680-7b93-11eb-83d4-3e684172fb90.png)

如果我们需要重新启动爬虫，只需要输入启动命令我们就可以重新启动爬虫了。
3.	需要在本地修改的地方

（1）	当前运行状态的保存 
在启动命令的JOBDIR后修改即可，这里使用相对路径即可，请不要使用绝对路径
（2）	图片的存储目录
前面已经说了，请查看第一点
（3）	数据库的连接
数据库的地址，端口，用户名，密码等请在pipeline.py 文件中BaiKeSpiderPipeline类里面的_init_函数修改，如下图,一般只需要修改user和password

![image](https://user-images.githubusercontent.com/23690625/109646951-b3b00b80-7b93-11eb-872b-bcbba4eb4c6b.png)

4.	附录 SQL语句

![image](https://user-images.githubusercontent.com/23690625/109646978-be6aa080-7b93-11eb-8c86-ca8a1d42ab04.png)
![image](https://user-images.githubusercontent.com/23690625/109646997-c4608180-7b93-11eb-8ce9-b55a80761f8f.png)

需要安装的packages
Scrapy,urllib,pymysql 

5.	可能会遇到的情况
有时会出现pic爬虫突然正常中止，这是因为baike爬虫收集的数据里的OID都已经被读取，这个时候只需要等待一会，用同样的启动命令启动pic爬虫即可。（这种情况很少出现）



