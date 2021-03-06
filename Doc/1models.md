# 模型设计

- 对于Blog CMS来说，项目模型(Model)的设计是整个项目最核心最终要的一个环节。**CMS项目中大部分功能都是与数据库打交道，数据库模型设计的好坏直接牵扯到了项目中期功能的实现**。下面是对本项目中模型设计的概述以及遇到的问题

## 设计表
- 设计模型之前需要先设计表。总的来说，表的设计主要考虑到了两个方面
	1. 表结构
		- 字段、字段的属性及参数要与将要实现的功能相符合，比如用来存储用户上传文件的字段就要采用FileField，并且在参数中指定存储路径。（这里要插一嘴，本项目中不涉及服务器的部署，既然是开发Blog CMS，本项目的重点是项目功能的实现）。比如用户注册时的手机号、邮箱、登陆时所使用的用户名这些字段对应的值需要在整张表中时唯一的，而有些字段则需要联合唯一（比如用户点赞、文章id、用户id，保证用户只能对同一篇文章点赞一次）等，这里不一一陈述。
		- 表结构还要考虑到查询的效率，这个非常重要。比如在本项目中，对于一篇博客文章的评论数量这个字段来说，其实它是可以不用存在于Article表中的，但是考虑到查询性能的优化，我们可以在Article中添加一个comment_count字段专门用来存放文章的评论数，当文章新添加一个评论的时候comment_count就会自增1，要获取文章评论数的时候就不需要再跨表去分组统计每一篇文章的评论数了。这里用到的思想优点类似缓存，但是它不是缓存，可以说是对时间的查询优化，让前端需要的数据在查询之前就将结果集准备好，加快的服务端获取响应结果的应速度。
	2. 关联关系
		- 本项目中为了测试方便，使用的是比较轻便的SQLite数据库，在实际中，可以替换成其他关系型数据库，只需要修改settings.py配置即可。
		- 整个项目可以说有两张表是最核心的表，即文章表和用户表，其他表均与这两张表建立了关联关系，表与表之间有着不同的关联关系，比如
			- 用户表(User)与用户个人博客表(Blog)之间建立的是一对一的关系
			- 文章表(Article)与文章评论表(Comment)之间建立的是外键关系(一对多)
			- 文章评论表内部又自关联，用于形成"评论树"（用户可以对文章的评论进行评论/回复）
			- 文章表与文章内容表是一对一的关系

#### 表关系介绍与分析（部分）
- ![可以先看下我画的表关系结构图]()
- 或者去看一下[models.py源码]()


###### 1. Blog、UserInfo
- 先说，Blog与UserInfo，两者之间是一对一的关系，UserInfo中主要存放的是用户登陆即相关的信息。
	- 为什么没有将Userinfo表拆成两张表（一张用于登陆验证，一张用于存放用户信息）？
		- 用户登陆之后，几乎都会进入到个人博客页面，而在个人博客页面中个就有关于用户个人的一些信息（比如博客年龄，昵称，头像等），如果将这些数据单独存放在一个表中，渲染用户个人博客页面的时候，从数据库查询数据就需要"跨表查询"，跨表查询相对与非跨表查询来说是比较浪费服务器性能的，并且存在IO阻塞，因此这些用户一登录就需要获取的用户数据信息，尽量和用户登陆信息存放在一张表中，丑陋但是高效！
	- 为什么要有Blog表？
		- 每一个用户的个人博客页面都对应着一个唯一的url路径，并且每一个博客都对应着自己的标题和主题（这个主题可以是一个css文件的路径），这些信息与用户个人信息不同，所以要单独用一张表存放。另外，这张表应该与用户表一对一建立联系，保证一个用户只能有一个“个人博客”

 
###### 2. 关于各种xxx_count字段
- 这些存放统计数据的字段存在的最大意义就在于**以空间换时间的方式来提高查询效率**，渲染页面时，可以直接从数据库中获取统计好的数据信息，而不是在每次需要渲染前通过Count计算出统计数据。


###### 3. Article与ArticleDetail
- 不论是在博客首页还是个人博客页面，并不会将整个文章内容显示给用户，需要给用户显示的仅仅是“文章标题”、“评论数”、“作者”、“发表时间”、“摘要”等，将文章内容单独存放在ArticleDetail表中并与Article表建立一对一的关系，用户需要查看整个文章内容的时候再去ArticleDetail表中获取文章详细内容数据，服务器就不需要一次性将文章信息报错文章内容加载到内存传输给客户端，这样可以显著降低服务器的运行压力


###### 4.TypeCategory与Category
- 前者是针对整个博客系统而言的文章类型，而后者是由用户个人博客自定义的各种分类。

###### 5. Tags与Category
- 对于一篇文章而言，他可以由多个标签，比如可以同时拥有"python", "技术", "项目"等标签，而对于文章的分类来说，一篇文章只能有一个分类

###### 6. Comment评论表
- 在一篇文章的评论中，评论有两种
	1. 对"文章"的评论
	2. 对"评论"的评论
- 对文章的评论我们暂且称为"根评论"，根评论下可以有多个子评论，子评论甚至也可以有多个自己的子评论，这在本项目中是完全支持的
- 要实现对"评论"的评论这种结构模型，我们需要建立表内关联关系，每一条评论记录都额外添加一个"father_comment_id"字段
	- 如果该字段为null，表示该字段是一个根评论
	- 如果该字段是其他字段的id值，那么该评论就是对应id评论的子评论
- 这种结构不但解决了多层评论的问题，而且在后面我们要利用该模型生成一种数据结构，使用递归来生成"评论树"


###### 接下来？
- 如果后续发现还有未能详尽陈述的内容，我会继续补充。。。


