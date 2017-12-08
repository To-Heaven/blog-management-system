# 注册页面设计

## 注册页面要实现的功能
1. form表单获取用户基本信息
2. 预览用户上传的头像
3. 对用户不合规范的信息进行提示（提示错误信息）
4. 实现用户注册


## 设计
#### 1. 创建页面
###### 1.1 form组件
- 创建`blog/forms文件`，文件内容如下

```python
from django.forms import Form
from django.forms import fields
from django.forms import widgets
from django.core.validators import RegexValidator, ValidationError

from blog import models


class BaseInfoForm(Form):
    """ 基本用户信息form组件类

    """
    username = fields.CharField(required=True,
                                error_messages={'required': '用户名不能为空'},
                                widget=widgets.TextInput(attrs={'placeholder': '用户名',
                                                                'class': 'form-control',
                                                                'aria-describedby': "username"}))

    password = fields.CharField(required=True,
                                validators=[RegexValidator(regex=r'^.{6,18}$', message='密码长度为6~18位'), ],
                                error_messages={'required': '密码不能为空'},
                                widget=widgets.PasswordInput(attrs={'placeholder': '密码',
                                                                    'class': 'form-control',
                                                                    'aria-describedby': "password"}))


class LoginForm(BaseInfoForm):
    """
        用于用户登陆的form组件类
    """
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request



class RegisterForm(BaseInfoForm):
    """
        用于注册注册用户的form组件类
    """
    email = fields.EmailField(required=True,
                              error_messages={'required': '请输入邮箱地址', 'invalid': '邮箱格式错误'},
                              widget=widgets.TextInput(attrs={'placeholder': '需要通过邮件激活账户', 'class': 'form-control'}))

    telephone = fields.CharField(required=True,
                                 error_messages={'required': '手机号不能为空'},
                                 validators=[RegexValidator(regex=r'^\d{11}$', message='手机号为11位数字'), ],
                                 widget=widgets.TextInput(
                                     attrs={'placeholder': '激活账户需要手机短信验证', 'class': 'form-control'}))

    nick_name = fields.CharField(required=True,
                                 max_length=32, min_length=2,
                                 error_messages={'required': '昵称不能为空', 'invalid': '昵称最少2个字符，最多20个字符'},
                                 widget=widgets.TextInput(attrs={'placeholder': '昵称，不少于2字符', 'class': 'form-control'}))

    confirm_password = fields.CharField(required=True,
                                        error_messages={'required': '确认密码不能为空'},
                                        widget=widgets.PasswordInput(
                                            attrs={'placeholder': '请输入确认密码', 'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if models.UserInfo.objects.filter(username=username):
            raise ValidationError('用户名已存在')

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password.isdigit():
            raise ValidationError('密码不能全是数字')

        if password.isalpha():
            raise ValidationError('密码不能全是字母')

        return password

    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError('两次输入的密码不一致')

        return self.cleaned_data

```
 
##### 1.2 配置路由

```python
from django.conf.urls import url
from django.contrib import admin

from blog import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/$', views.register),
]
```

###### 1.3 register.html页面
- form组件中字段的`widget`参数中`attr`参数就是用来指定标签的属性和类，方便我们渲染Bootstrap提供的样式。**注意**，在上面，attr中的`aria-describedby`将会在form验证时校验使用，并且其对用的值最好与字段名保持一致，这样在前端js获取服务端返回error_message的时候，可以很方便的渲染。（其实在设计字段甚至是其他数据结构的时候，我们要充分考虑其对后续功能实现的影响，要选择一个较适合的数据结构或参数）

- `/templates/register.html`代码如下

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>用户注册——cms</title>
    <link rel="stylesheet" href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/css/register.css">
</head>
<body>
<nav class="navbar my-navbar-style border-style ">
    <div class="container my-navbar-style ">
        <!-- 导航条  -->
        <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse"
                    data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand font-style" href="#">blog management system</a>
        </div>

        <!-- 导航条链接 -->
        <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
            <ul class="nav navbar-nav navbar-right">
                <li><a href="#" class="font-style">Link</a></li>
                <li><a href="#" class="font-style">Link</a></li>
                <li><a href="#" class="font-style">Link</a></li>
                <li><a href="#" class="font-style">Link</a></li>
            </ul>
        </div><!-- /.navbar-collapse -->
    </div><!-- /.container-fluid -->
</nav>

<div class="container">
    <div class="row">
        <div class="col-md-10 col-md-offset-1">
            <p class="title-font">注册新用户</p>
            <hr>
        </div>
    </div>
    <div class="row row-style">
        <div class="col-md-7">
            <form class="form-horizontal" novalidate>
                {% csrf_token %}

                <div class="col-md-10">
                    <div class="form-group">
                        <label for="avatar" class="col-sm-4 control-label ">选择头像</label>
                        <div class="col-sm-8" id="father_avatar">
                            <img src="/media/avatar/default.png" id="img_avatar">
                            <input type="file" value="选择头像" id="file_avatar">
                            <span id="avatar" class="help-block my-display"></span>
                        </div>
                    </div>
                </div>

                <div class="col-md-10">
                    <div class="form-group">
                        <label for="id_email" class="col-sm-4 control-label text-justify">邮箱</label>
                        <div class="col-sm-8">
                            {{ form.email }}
                            <!-- 显示错误信息  -->
                            <span id="email" class="help-block my-display"></span>
                        </div>
                    </div>
                </div>
                <div class="col-md-10">
                    <div class="form-group">
                        <label for="id_telephone" class="col-sm-4 control-label text-justify">手机号码</label>
                        <div class="col-sm-8">
                            {{ form.telephone }}
                            <span id="telephone" class="help-block my-display"></span>
                        </div>
                    </div>
                </div>
                <div class="col-md-10">
                    <div class="form-group">
                        <label for="id_username" class="col-sm-4 control-label text-justify">登陆名称</label>
                        <div class="col-sm-8">
                            {{ form.username }}
                            <span id="username" class="help-block my-display"></span>
                        </div>
                    </div>
                </div>
                <div class="col-md-10">
                    <div class="form-group">
                        <label for="id_nick_name" class="col-sm-4 control-label text-justify">显示名称</label>
                        <div class="col-sm-8">
                            {{ form.nick_name }}
                            <span id="nick_name" class="help-block my-display"></span>
                        </div>
                    </div>
                </div>
                <div class="col-md-10">
                    <div class="form-group">
                        <label for="id_password" class="col-sm-4 control-label text-justify">密码</label>
                        <div class="col-sm-8">
                            {{ form.password }}
                            <span id="password" class="help-block my-display"></span>
                        </div>
                    </div>
                </div>
                <div class="col-md-10">
                    <div class="form-group">
                        <label for="id_confirm_password" class="col-sm-4 control-label text-justify">确认密码</label>
                        <div class="col-sm-8">
                            {{ form.confirm_password }}
                            <span id="confirm_password" class="help-block my-display"></span>
                        </div>
                    </div>
                </div>
            </form>
            <div class="col-md-10">
                <div class="col-md-8">
                    <button class="btn btn-primary col-md-offset-11">注册</button>
                </div>
            </div>
            <div class="col-md-7 col-md-offset-3 ">
                <span>&nbsp;&nbsp;&nbsp;&nbsp;* “注册” 按钮，即表示您同意并愿意遵守</span><a href=""
                                                                             style="text-decoration-line: underline">&nbsp;用户协议</a>
            </div>
        </div>

        <div class="col-md-5">
            <img src="https://account.cnblogs.com/images/registersideimg.png?v=SuVn_GWSEJByGrNm06GT-sxx_RW9nUtfd625myn_CsE"
                 class="img-style" alt="">
        </div>
    </div>
    <div class="row text-center">
        <hr>
        <a href="">关于blog management system&nbsp;&nbsp;&nbsp;</a>
        <a href="">联系我们 &nbsp;&nbsp;&nbsp;</a>
        <span>©2015-2017 &nbsp;&nbsp;&nbsp;</span>
        <a href="">blog management system&nbsp;&nbsp;&nbsp;</a>
        <span>保留所有权利&nbsp;Powered&nbsp;by&nbsp;Django&nbsp;Core&nbsp;on&nbsp;小霸王</span>
    </div>
</div>
<script src="https://cdn.bootcss.com/jquery/3.2.1/jquery.min.js"></script>
<script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
<script src="/static/register.js"></script>
</body>
</html>
```

###### 1.4 配置静态文件register.css
1. 配置settings.py中static路径

2. 在项目目录下创建static目录如下

```
├─static
│  └─blog
│      └─css
```

3. 在css目录下创建`register.css`文件，其内存放渲染register.html的css代码
	- 代码如下

```css
#father_avatar{
    position: relative;
    width: 40px;
    height: 40px;
}

#img_avatar, #file_avatar{
    position: absolute;
    width: 40px;
    height: 40px;
    top: 0;
    left: 15px;
}

#file_avatar{
    opacity: 0;
}

.my-navbar-style {
    background-color: rgb(40, 62, 92);
    border-color: #e7e7e7;
    color: rgb(255, 255, 255);
    height: 50px;
}

.help-block {
    font-size: 10px;
}

.navbar-nav {
    float: left;
    margin: 0
}

.navbar-nav > li {
    float: left
}

.col-md-10 {
    height: 60px;
}

.col-md-7 {
    margin-top: 15px;
}

.col-md-5 {
    margin-top: 15px;
}

.navbar-nav > li > a {
    padding-top: 15px;
}

.font-style {
    color: white;
}

.title-font {
    font-size: 25px;
    margin-top: 30px;
}

.border-style {
    border-radius: 0;
    border: 0;
}

.row-style {
    margin-top: 30px;
}

.img-style {
    margin-left: -20px;
    height: 320px;
    width: 300px;
}

.form-style {
    border-right: 1px;
    border-color: black;
    border-right: 165px;
}

.my-display {
    display: block;
}
```
 

###### 1.5.1 创建视图函数
- 在`register`视图函数中，要完成以下几个功能
	1. `GET`请求: 返回页面
	2. `POST`请求: 接收客户端数据并使用form组件验证
	3. 验证失败: 将错误信息返回给客户端
	4. 验证成功: 将用户信息保存到数据库，并向客户端返回注册成功的状态信息

- 代码如下

```python
import datetime
from json import dumps
from django.shortcuts import render, HttpResponse

from blog.forms import RegisterForm
from blog import models


def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    elif request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if not form.is_valid():
            data = {'form_errors': form.errors}
            return HttpResponse(dumps(data))

        form.cleaned_data['join_time'] = datetime.datetime.now()
        del form.cleaned_data['confirm_password']

        avatar = request.FILES.get('avatar')                    # 获取用户头像
        form.cleaned_data['avatar'] = avatar
        models.UserInfo.objects.create(**form.cleaned_data)

        data = {'success': True}
        return HttpResponse(dumps(data))
```




###### 1.5.2 配置静态文件register.js
- 创建目录`/static/blog/js`，并创建register.js文件
- register.js文件应该实现的功能如下
	1. 预览客户端头像
	2. Ajax异步提交表单信息（csrf）
	3. 接收服务端返回的响应信息
		- 验证失败： 取出错误信息并渲染到页面
		- 验证成功: 跳转至登陆页面

```javascript
$(".btn").click(function () {
        $("form span").text('');
        $("div.form-group").removeClass('has-error');

        var formData = new FormData();
        formData.append("email", $('#id_email').val());
        formData.append("telephone", $('#id_telephone').val());
        formData.append("username", $('#id_username').val());
        formData.append("nick_name", $('#id_nick_name').val());
        formData.append("password", $('#id_password').val());
        formData.append("confirm_password", $('#id_confirm_password').val());
        formData.append("csrfmiddlewaretoken", $('input:hidden').val());
        formData.append("avatar", $('input:file')[0].files[0]);

        $.ajax({
            url: '/register/',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
                data = JSON.parse(data);

                if (data["success"]){
                    window.location.href = "/login/";
                }

                if (data["form_errors"]) {
                    for (var key in data["form_errors"]) {
                        for (var key in data["form_errors"]) {

                            if (key == "__all__") {
                                $("#confirm_password").text(data["form_errors"][key]);
                                $("#confirm_password").parent().parent().addClass('has-error');
                            } else {
                                $("#" + key).text(data["form_errors"][key]);
                                $("#" + key).parent().parent().addClass('has-error');
                            }
                        }
                    }
                }
            }
        })
    });

// 图片预览 方法一
// $("input:file").change(function () {
//    var fileObj = this.files[0];
//
//    var readerObj = new FileReader();
//    readerObj.readAsDataURL(fileObj);
//
//    readerObj.onload = function () {
//        $("#img_avatar")[0].src = this.result;
//    }
//
// });

// 图片预览方法二 
$("input:file").change(function () {
   $("#img_avatar")[0].src = window.URL.createObjectURL($(this)[0].files[0]);
});
```

 
