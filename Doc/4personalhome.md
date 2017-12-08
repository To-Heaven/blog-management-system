# 个人博客界面
- 在博客主界面中，点击用户头像就可以进入到该文章所属作者的个人博客空间中
- 个人博客空间主要有3部分构成
	1. 导航条
	2. 博主个人及文章归档信息
	3. 文章展示区域

## 功能与实现
#### 1. 博主blog年龄
- blog在数据库中存放的是datetime对象，如果要转换成中文的年龄比如"xx年xx月xx日"，光使用Django提供的过滤器"date"是不够的，我们需要自己定义一个过滤器
	- 步骤和上一节自定义"inlcusion_tag"基本一样，有些地方需要修改和处理
		- 这里需要使用python的datetime模块以及字符串的处理得到最终结果
		- mytags.py中相关代码如下

```python
@register.filter
def blog_age(create_time):
    """ 生成用户博客账号年龄
    Args:
        create_time: 用户账号创建时间
    Return:
        博客年龄字符串
    """
    
    now = datetime.datetime.now()
    create_time = datetime.datetime(create_time.year,
                                    month=create_time.month,
                                    day=create_time.day,
                                    hour=create_time.hour,
                                    minute=create_time.minute,
                                    second=create_time.second)
    age_string = str(now - create_time)[:-16]                   # 计算去除多余的时分秒片段
    if 'days' in age_string:
        age_string = age_string.replace('days', '天')
    if 'months' in age_string:
        age_string = age_string.replace('months', '月')
    if 'years' in age_string:
        age_string = age_string.replace('years', '年')

    return age_string
```



#### 2. 归档


    
###### 按照时间归档
- 使用了Django提供的extra函数，由于使用的时sqllite数据库，这里使用的时"strftime("%%Y/%%m", create_time)"，如果是mysql，就要将"strftime"替换成"dateType"


```python
    dates = models.Article.objects.filter(blog__user__username=username).\
        extra(select={'create_date_format': 'strftime("%%Y/%%m", create_time)'}).\
        values_list('create_date_format').annotate(c=Count("id")).values_list('create_date_format', 'c')

```

###### 按照分类和标签归档
- 都是使用了分组进行查询

```python
    categorys = models.Category.objects.filter(blog__user=user).annotate(c=Count("article__id")).values_list('title','c', 'id')
    tags = models.Tag.objects.filter(blog__user=user).annotate(c=Count("article__id")).values_list('title', 'c', 'id')
```