# 模型分析与设计
- 每一个项目的数据库设计都是整个项目的重中之重，它牵扯到后期项目功能的实现，并且数据库特别是关系型数据库表的设计要保证考虑到性能（主要是查询数据的性能）以及表与表之间的关系。


## 模型分析
#### 用户信息表

#### 博客表

#### 文章信息表

#### 文章内容表

#### 文章分类表

#### 文章标签表

#### 文章评论表

#### 文章点赞表

#### 评论点赞表


## 模型设计
- 设置模型如下

```python
from django.db import models
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    """
        用户信息表
    """
    id = models.BigAutoField(primary_key=True)
    nick_name = models.CharField(max_length=32, verbose_name='昵称')
    join_time = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')
    telephone = models.CharField(max_length=11, verbose_name='手机号', unique=True, null=True)
    email = models.EmailField(verbose_name='联系邮箱')
    avatar = models.FileField(verbose_name='头像', upload_to='avatar', default='media/img/avatar/default.png')

    def __str__(self):
        return self.nick_name

    class Meta:
        verbose_name_plural = '用户表'


class Blog(models.Model):
    """
        博客表
    """
    id = models.BigAutoField(primary_key=True)
    user_site = models.CharField(max_length=64, verbose_name='blog站点', unique=True)
    blog_title = models.CharField(max_length=64, verbose_name='博客标题')
    theme = models.CharField(max_length=16, verbose_name='主题')

    user = models.OneToOneField(to='UserInfo', to_field='id', verbose_name='用户')

    def __str__(self):
        return self.user_site

    class Meta:
        verbose_name_plural = '博客表'


class Category(models.Model):
    """
        分类表
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32, verbose_name='文章分类名')
    article_count = models.IntegerField(verbose_name='文章数量')
    description = models.CharField(max_length=64, verbose_name='分类描述')
    create_time = models.DateTimeField(verbose_name='创建时间')

    blog = models.ForeignKey(to='Blog', to_field='id', verbose_name='所属博客')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '分类表'


class Article(models.Model):
    """
        文章信息表
    """
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=64, verbose_name='文章标题')
    summary = models.CharField(max_length=512, verbose_name='文章概要')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now_add=True)

    read_count = models.IntegerField(verbose_name='阅读次数')
    comment_count = models.IntegerField(verbose_name='评论次数')
    up_count = models.IntegerField(verbose_name='点赞次数')
    down_count = models.IntegerField(verbose_name='反对次数')

    blog = models.ForeignKey(to='Blog', to_field='id', verbose_name='博客')
    article_detail = models.OneToOneField(to='ArticleDetail', to_field='id', verbose_name='文章详细')
    category = models.ForeignKey(to='Category', to_field='id', verbose_name='文章分类')
    tags = models.ManyToManyField(verbose_name='文章标签', to='Tag', through='Tag2Article',
                                  through_fields=('article', 'tag'))

    type_choices = [
        (1, '技术'),
        (2, '音乐'),
        (3, '生活'),
        (4, '经济'),
        (5, '时政'),
        (6, '文化'),
        (7, '其他'),
    ]
    type_id = models.IntegerField(choices=type_choices, verbose_name='文章类型')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '文章表'


class ArticleDetail(models.Model):
    """
        文章内容表
    """
    id = models.BigAutoField(primary_key=True)
    content = models.TextField(max_length=20480, verbose_name='文章内容')

    class Meta:
        verbose_name_plural = '文章内容表'


class Comment(models.Model):
    """
        文章评论表
    """
    id = models.BigAutoField(primary_key=True)
    content = models.CharField(max_length=512, verbose_name='评论内容')
    create_time = models.DateTimeField(verbose_name='评论时间')
    up_count = models.IntegerField(verbose_name='点赞数', default=0)
    down_count = models.IntegerField(verbose_name='反对数', default=0)

    father_comment_id = models.ForeignKey(to='Comment', to_field='id', verbose_name='上级评论id')

    article = models.ForeignKey(to='Article', to_field='id', verbose_name='文章')
    user = models.ForeignKey(to='UserInfo', to_field='id', verbose_name='评论用户')

    class Meta:
        verbose_name_plural = '评论表'


class CommentUpDown(models.Model):
    """
        评论点赞表
    """
    id = models.BigAutoField(primary_key=True)
    is_like = models.BooleanField(verbose_name='点赞or反对')

    comment = models.ForeignKey(to='Comment', to_field='id', verbose_name='关联评论')
    user = models.ForeignKey(to='UserInfo', to_field='id', verbose_name='关联用户')

    class Meta:
        verbose_name_plural = '评论点赞表'


class ArticleUpDown(models.Model):
    """
        文章点赞表
    """
    id = models.BigAutoField(primary_key=True)
    is_like = models.BooleanField(verbose_name='点赞or反对')

    article = models.ForeignKey(to='Article', to_field='id', verbose_name='关联文章')
    user = models.ForeignKey(to='UserInfo', to_field='id', verbose_name='关联用户')

    class Meta:
        verbose_name_plural = '文章点赞表'


class Tag(models.Model):
    """
        文章标签表
    """
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=16)

    blog = models.ForeignKey(to='Blog', to_field='id', verbose_name='所属博客')

    class Meta:
        verbose_name_plural = '标签表'


class Tag2Article(models.Model):
    """
        文章_标签多对多关系表
    """
    id = models.BigAutoField(primary_key=True)

    tag = models.ForeignKey(to='Tag', to_field='id', verbose_name='标签')
    article = models.ForeignKey(to='Article', to_field='id')

    class Meta:
        unique_together = [('tag', 'article'), ]
        verbose_name_plural = '标签文章表'

```

#### UserInfo
- 这里创建的UserInfo继承自`django.contrib.auth`内置应用下models中的AbstractUser。这样做我们可以在用户注册后台创建用户的时候使用Model对象的`create_user`方法，这样用户的登陆密码会被加密，当然，如果你想自己创建一个表，使用自定义的加密方式来对密码进行加密也是可以的。
- 使用`AbstractUser`配置
	1. 导入
	2. settings.py下`AUTH_USER_MODEL = 'blog.UserInfo'`


#### Article
- 文章信息表中，将文章的类型使用`choice`而非额外创建一个文章类型表有两个原因
	1. 这个文章的类型主要用于“博客论坛系统”中文章的分类，并且这些分类几乎是不会再变化的，
	2. 对于这种不经常变化的字段，使用choice可以**省去服务端额外的跨表查询性能开销**

