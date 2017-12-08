import datetime

from django.db import models


class UserInfo(models.Model):
    """
        用户信息表
    """

    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=32, verbose_name='登录名')
    password = models.CharField(max_length=64, verbose_name='密码')
    nick_name = models.CharField(max_length=32, verbose_name='昵称')
    join_time = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')
    telephone = models.CharField(max_length=11, verbose_name='手机号', unique=True, null=True)
    email = models.EmailField(verbose_name='联系邮箱')
    avatar = models.FileField(verbose_name='头像', upload_to='avatar', default='/avatar/default.png')

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

    read_count = models.IntegerField(verbose_name='阅读次数', default=0)
    comment_count = models.IntegerField(verbose_name='评论次数', default=0)
    up_count = models.IntegerField(verbose_name='点赞次数', default=0)
    down_count = models.IntegerField(verbose_name='反对次数', default=0)

    blog = models.ForeignKey(to='Blog', to_field='id', verbose_name='博客')
    article_detail = models.OneToOneField(to='ArticleDetail', to_field='id', verbose_name='文章详细')
    category = models.ForeignKey(to='Category', to_field='id', verbose_name='文章分类')
    tags = models.ManyToManyField(verbose_name='文章标签', to='Tag', through='Tag2Article',
                                  through_fields=('article', 'tag'))
    type_category = models.ForeignKey(to='TypeCategory', to_field='id', verbose_name='文章类型分类名称')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '文章表'


class TypeCategory(models.Model):
    """
        文章类型分类表
    """

    def __init__(self, *args, **kwargs):
        """ 初始化对象
        """
        super().__init__(*args, **kwargs)
        self.today_article_count = self.get_today_article_count(Article)

    def get_today_article_count(self, Article):
        """ 计算当天self对应子分类下文章个数
        Args:
            Article: 文章模型类
        Return:
            count: 文章个数
        """

        now = datetime.datetime.now()
        count = Article.objects.filter(type_category_id=self.id, create_time__year=now.year,
                                       create_time__month=now.month, create_time__day=now.day).count()
        return count

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, verbose_name='分类')
    today_article_count = models.IntegerField(verbose_name='今日该类文章数量', default=0)

    type = models.ForeignKey(to='Type', to_field='id', verbose_name='文章类型')



    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '文章类型分类表'


class Type(models.Model):
    """
        文章类型表
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, verbose_name='文章类型名称')
    total_count = models.IntegerField(verbose_name='今日该类型文章数量', default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '文章类型表'


class ArticleDetail(models.Model):
    """
        文章内容表
    """

    id = models.BigAutoField(primary_key=True)
    content = models.TextField(max_length=40960, verbose_name='文章内容')

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

    father_comment_id = models.ForeignKey(to='Comment', to_field='id', null=True,  verbose_name='上级评论id', blank=True)

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
        unique_together = (('article', 'user', 'is_like'), )


class Tag(models.Model):
    """
        文章标签表
    """

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=16)

    blog = models.ForeignKey(to='Blog', to_field='id', verbose_name='所属博客')

    def __str__(self):
        return self.title

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

