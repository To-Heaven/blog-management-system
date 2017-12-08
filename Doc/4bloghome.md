# 博客系统主界面

## 功能与实现
#### 1. 导航条查询功能
- 导航条查询使用form提交GET请求，但是在提交请求之前会对表单中的数据进行判断
	- **如果表单中用户没有输入要查询的关键字，请求就无法发送并且会弹出警告框提示用户输入要检所的内容。**
		- 实现这个功能，我利用的是form这个DOM对象的特殊的submit()方法
	- 如果用户提交的内容合法，请求数据会根据urls.py中配置的url与视图函数的映射关系找到`home`视图函数，返回标题或者着要重包含关键字的文章，同时页面查询结果左上方会显示"按照关键字key_word的查询结果: "提醒用户，并且查询得到的结果会按照时间排序，最新的文章将会在排列在最上方

```JavaScript
// 验证搜索框是否为空
$("#is_submit").click(function () {
   var key_word = $("[name='search']").val();
   if (key_word){
       $("#search_form")[0].submit();
   }else {
       swal({
            title: '输入框里没有内容咧',
            text: '不输入查找内容无法查找昂',
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            confirmButtonText: '确定！',
            showCloseButton: true
        });
   }
});
```

#### 2. 关于登陆和注册
- 导航条中除了主页logo，查询之外，还包含了一个非常重要的功能
	- 如果当前没有用户登陆，即session中没有关于登陆用户的信息（用户登陆成功之后，个人信息会保存在session中），那么在导航条右侧会显示"登陆"和"注册"超链接
	- 如果当前用户已经登陆，那么导航条右方会显示当前用户的"姓名"，"注销登陆", "我的博客"下拉框
		- 点击用户姓名图标后，会跳转到用户个人博客界面
		- 点击注销登陆后，在FBV中会调用session的flush方法清空当前session中保存的用户相关信息，在数据库的session表中关于用户的信息也会被清除。__这里要注意，在本项目中session是存放在Dajngo提供的session表中的，在大型的网站，一般会有专门的Session服务器集群，用来保存用户会话，这个时候Session 信息都是放在内存的，使用一些缓存服务比如Memcached之类的来放Session__
	- 相关代码如下

```html
<ul class="nav navbar-nav navbar-right">

    {% if request.session.username %}
        <li><a href="{% url 'blog_url' username=request.session.username %}"><i class="fa fa-user" aria-hidden="true"></i>&nbsp;{{ request.session.username }}
        </a></li>
        <li><a href="/logout/">注销</a></li>

        <li class="dropdown">
            <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true"
               aria-expanded="false">我的博客 <span class="caret"></span></a>
            <ul class="dropdown-menu">
                <li><a href="{% url 'blog_url' username=request.session.username %}">我的主页</a></li>
                <li><a href="#">新添文章</a></li>
                <li><a href="#">个人信息</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="#">修改密码</a></li>
            </ul>
        </li>
    {% else %}
        <li><a href="/login/">登陆</a></li>
        <li><a href="/register/">注册</a></li>
    {% endif %}
</ul>
``` 


#### 3. 左侧菜单
- 左侧菜单内容是整个博客系统博文的分类，使用了比较简单的样式每一个子分类后面中都包括了今日该子分类下文章提交的数量。
	1. 为什么子分类后使用该子分类下文章的总数？
		- 对于比较活跃的博客社区来说，如果使用总数的话，那么这个选项就没有什么参考意义了，用户可能想要了解的只是近期该子分类下文章的活跃程度。
		- 如果你测试本项目，并且没有提交文章的话，你会发现所有子项目对应的今日提交文章数量都是"0"。
	2. 当点击其中一个子分类的时候，内容区域中会将该子分类下的文章按照时间顺序依次从上到下排列。
	3. 如何计算"今日该子分类下文章提交的数量"？
		- 在子分类对应的模型类下，定义一个"get_today_article_count()"的对象方法，在对象的"__init__()"方法中调用该方法实现

- 代码如下

```python
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
```

- 渲染左侧菜单。
	- 渲染左侧菜单我使用的是Django提供的自定义标签"inlcusion_tag"，这个自定义标签会渲染一段HTML标签代码并嵌入到调用其的页面中。
	- 使用自定义标签的时候需要几个步骤
		1. 'blog'应用下创建包`templatetags`，并且包名必须是这个
		2. 在该包下创建一个任意名称的`.py`文件，我们要定义的标签就在该文件中
		3. 在该文件中导入`template`模块的`Library`类
			- `from django.template import Library`
		4. 实例化，并创建一个名称为`register`的对象，名称必须为这个
		5. 使用`@register.inclusion(*args, **kwargs)`创建自定义inclusion_tag
		6. 代码如下

```python
# /blog/templatetags/mytag.py

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
```

```html
<!-- 要被渲染的HTML模板 menu.html -->
<ul class="list-unstyled">
    {% for type in types %}
        <div id="per_topic">
            <li class="topic-style text-center">
                <span class="btn">{{ type.name }}</span>
            </li>
            <div class="menu-item hides">
                {% for type_category in type.typecategory_set.all %}
                    <a href="{% url 'category' type_category=type_category.id %}">{{ type_category.name }}&nbsp;<span
                            class="badge">{{ type_category.today_article_count }}</span></a>&nbsp;&nbsp;
                {% endfor %}
            </div>
        </div>
    {% endfor %}
</ul>

```

```javascript
// 左侧菜单js代码

$(".topic-style span.btn").click(function () {
    $(this).parent().next().toggleClass('hides');
    $(this).parent().parent().siblings().children('.menu-item').addClass('hides');
});
```


#### 4. 关于热门文章
- 热门文章是默认按照评论数排序的，在实际的blog社区中，评论数排序的结果集应该是今天发表的文章，在本项目中考虑到是用来测试，就将结果集设置为了所有发表的文章（因为文章少嘛~~）。
- 热门文章除了默认的评论数排序之外，还提供了按时间排序，可以让用户看到当前最新的发布的博客文章。
- 考虑到模板的普适性和扩展性，这里没有使用Ajax来发送排序相关请求，这样视图函数只需要提供相同的"articles"上下文接口即可渲染出想要的页面。代码如下
	- 注意，这里使用到了JavaScript的模板字符串，但是在一些版本的JavaScript中并不支持模板字符串，我认为模板字符串非常实用，并且可以把复杂的问题简单化，在后面的js代码中还会出现模板字符串的身影

```python
def home(request, para=None):
    """ 博客系统主界面路径对应的视图函数，渲染主界面的模板页面
    Args:
        request: 当前客户端请求对象
        para： 字符串，请求url中的参数用于渲染热门文章
    Return:
        返回一个响应对象
    """
    
    articles = models.Article.objects.order_by('comment_count')
    
    if para == 'hot':                                               # 处理按照热度排序
        return render(request, 'home.html', {"articles": articles})
    elif para == 'time':                                            # 处理按照时间排序
        articles = models.Article.objects.order_by('create_time').reverse()
        return render(request, 'home.html', {"articles": articles})
    elif request.method == 'GET':                                   # 处理Get请求
        key_word = request.GET.get('search')
        if key_word:                                            
            articles = models.Article.objects.filter(title__contains=key_word)
            return render(request, 'home.html', {"articles": articles, "is_search": True, "key_word": key_word})
        return render(request, 'home.html', {"articles": articles})
```


```javascript
// 对文章排序
var current_url = window.location.href;

var inner_html = `&nbsp;按热度排序&nbsp;|&nbsp;<a href="/home/time/">按时间排序</a>&nbsp;&nbsp;`;
$("#order_article").html(inner_html);

if (current_url == 'http://127.0.0.1:8000/home/hot/') {
    var inner_html = `&nbsp;按热度排序&nbsp;|&nbsp;<a href="/home/time/">按时间排序</a>&nbsp;&nbsp;`;
    $("#order_article").html(inner_html);
}

if (current_url == 'http://127.0.0.1:8000/home/time/') {
    var inner_html = `&nbsp;<a href="/home/hot/">按热度排序</a>&nbsp;|&nbsp; 按时间排序 &nbsp;&nbsp;`;
    $("#order_article").html(inner_html)
}
```

#### 5. 关于分页
- 分页的样式使用的是BootStrap提供的分页插件，Django为我们提供了专门用来分页的组件"Paginator"，向深入了解，可以点击传送至我的[Django分页插件介绍]()