from django.template import Library
from django.utils.safestring import mark_safe
import datetime

from blog import models

register = Library()


@register.inclusion_tag(filename='menu.html')
def menu_html():
    """ 渲染左侧菜单页面
    Args:
         装饰器参数filename指定要渲染的模板文件
    Return:
         要传递给该模板的上下文对象
    """

    types = models.Type.objects.all()
    return {'types': types}


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
