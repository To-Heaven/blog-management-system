# 登陆页面设计

## 登陆页面要实现的基本功能
1. 滑动验证码
2. 用户登陆验证
3. 回显验证失败的信息
4. 使用form表单提交用户数据


## 设计
#### 1. 创建页面
###### 1.1 form组件
- form组件类这次要使用`LoginForm`，在实例化的时候，需要传入`request`对象，这是为了在用户登陆验证成功之后，将用户的信息保存到session 中，的要把可变参数添加上

```python
class LoginForm(BaseInfoForm):
    """
        用于用户登陆的form组件类
    """
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
```


###### 1.2 配置路由

```python
from django.conf.urls import url
from django.contrib import admin
from django.views.static import serve

from blog import views
from bms import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/$', views.register),
    url(r'^login/$', views.login),

    # media配置
    url(r'^media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT})
]
```

###### 1.3 滑动验证码
1. 安装`social_auth_app_django`模块
2. blog应用下创建文件`geetest.py`，代码如下

```python
#!coding:utf8
import sys
import random
import json
import requests
import time
from hashlib import md5


if sys.version_info >= (3,):
    xrange = range    

VERSION = "3.0.0"


class GeetestLib(object):

    FN_CHALLENGE = "geetest_challenge"
    FN_VALIDATE = "geetest_validate"
    FN_SECCODE = "geetest_seccode"

    GT_STATUS_SESSION_KEY = "gt_server_status"

    API_URL = "http://api.geetest.com"
    REGISTER_HANDLER = "/register.php"
    VALIDATE_HANDLER = "/validate.php"
    JSON_FORMAT = False

    def __init__(self, captcha_id, private_key):
        self.private_key = private_key
        self.captcha_id = captcha_id
        self.sdk_version = VERSION
        self._response_str = ""


    def pre_process(self, user_id=None,new_captcha=1,JSON_FORMAT=1,client_type="web",ip_address=""):
        """
        验证初始化预处理.
        //TO DO  arrage the parameter
        """
        status, challenge = self._register(user_id,new_captcha,JSON_FORMAT,client_type,ip_address)
        self._response_str = self._make_response_format(status, challenge,new_captcha)
        return status

    def _register(self, user_id=None,new_captcha=1,JSON_FORMAT=1,client_type="web",ip_address=""):
        pri_responce = self._register_challenge(user_id,new_captcha,JSON_FORMAT,client_type,ip_address)
        if pri_responce:
            if JSON_FORMAT == 1:
                response_dic = json.loads(pri_responce)
                challenge = response_dic["challenge"]
            else:
                challenge = pri_responce
        else:
            challenge=" "
        if len(challenge) == 32:
            challenge = self._md5_encode("".join([challenge, self.private_key]))
            return 1,challenge
        else:
            return 0, self._make_fail_challenge()

    def get_response_str(self):
        return self._response_str

    def _make_fail_challenge(self):
        rnd1 = random.randint(0, 99)
        rnd2 = random.randint(0, 99)
        md5_str1 = self._md5_encode(str(rnd1))
        md5_str2 = self._md5_encode(str(rnd2))
        challenge = md5_str1 + md5_str2[0:2]
        return challenge

    def _make_response_format(self, success=1, challenge=None,new_captcha=1):
        if not challenge:
            challenge = self._make_fail_challenge()
        if new_captcha:
            string_format = json.dumps(
                {'success': success, 'gt':self.captcha_id, 'challenge': challenge,"new_captcha":True})
        else:
            string_format = json.dumps(
                {'success': success, 'gt':self.captcha_id, 'challenge': challenge,"new_captcha":False})
        return string_format

    def _register_challenge(self, user_id=None,new_captcha=1,JSON_FORMAT=1,client_type="web",ip_address=""):
        if user_id:
            register_url = "{api_url}{handler}?gt={captcha_ID}&user_id={user_id}&json_format={JSON_FORMAT}&client_type={client_type}&ip_address={ip_address}".format(
                    api_url=self.API_URL, handler=self.REGISTER_HANDLER, captcha_ID=self.captcha_id, user_id=user_id,new_captcha=new_captcha,JSON_FORMAT=JSON_FORMAT,client_type=client_type,ip_address=ip_address)
        else:
            register_url = "{api_url}{handler}?gt={captcha_ID}&json_format={JSON_FORMAT}&client_type={client_type}&ip_address={ip_address}".format(
                    api_url=self.API_URL, handler=self.REGISTER_HANDLER, captcha_ID=self.captcha_id,new_captcha=new_captcha,JSON_FORMAT=JSON_FORMAT,client_type=client_type,ip_address=ip_address)
        try:
            response = requests.get(register_url, timeout=2)
            if response.status_code == requests.codes.ok:
                res_string = response.text
            else:
                res_string = ""
        except:
            res_string = ""
        return res_string

    def success_validate(self, challenge, validate, seccode, user_id=None,gt=None,data='',userinfo='',JSON_FORMAT=1):
        """
        正常模式的二次验证方式.向geetest server 请求验证结果.
        """
        if not self._check_para(challenge, validate, seccode):
            return 0
        if not self._check_result(challenge, validate):
            return 0
        validate_url = "{api_url}{handler}".format(
            api_url=self.API_URL, handler=self.VALIDATE_HANDLER)
        query = {
            "seccode": seccode,
            "sdk": ''.join( ["python_",self.sdk_version]),
            "user_id": user_id,
            "data":data,
            "timestamp":time.time(),
            "challenge":challenge,
            "userinfo":userinfo,
            "captchaid":gt,
            "json_format":JSON_FORMAT
        }
        backinfo = self._post_values(validate_url, query)
        if JSON_FORMAT == 1:
            backinfo = json.loads(backinfo)
            backinfo = backinfo["seccode"]
        if backinfo == self._md5_encode(seccode):
            return 1
        else:
            return 0

    def _post_values(self, apiserver, data):
        response = requests.post(apiserver, data)
        return response.text

    def _check_result(self, origin, validate):
        encodeStr = self._md5_encode(self.private_key + "geetest" + origin)
        if validate == encodeStr:
            return True
        else:
            return False

    def failback_validate(self, challenge, validate, seccode):
        """
        failback模式的二次验证方式.在本地对轨迹进行简单的判断返回验证结果.
        """
        if not self._check_para(challenge, validate, seccode):
            return 0
        validate_result = self._failback_check_result(
            challenge, validate,)
        return validate_result

    def _failback_check_result(self,challenge,validate):
        encodeStr = self._md5_encode(challenge)
        if validate == encodeStr:
            return True
        else:
            return False



    def _check_para(self, challenge, validate, seccode):
        return (bool(challenge.strip()) and bool(validate.strip()) and  bool(seccode.strip()))



    def _md5_encode(self, values):
        if type(values) == str:
            values = values.encode()
        m = md5(values)
        return m.hexdigest()


```

3. 配置项目setting.py文件，在TEMPLATES.OPTIONS.context_processors下添加配置如下

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',  						# 验证码配置项
                'social_django.context_processors.login_redirect', 					 # 验证码配置项
            ],
        },
    },
]
```



4. urls.py中添加如下配置

```python
from django.conf.urls import url
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', views.login),
    url(r'^register/$', views.register),
    url(r'^home/$', views.home),
    url(r'^pc-geetest/register/$', views.pcgetcaptcha, name='pcgetcaptcha'),
    url(r'^pc-geetest/validate/$', views.pcvalidate, name='pcvalidate'),
    url(r'^pc-geetest/ajax_validate/$', views.pcajax_validate, name='pcajax_validate'),
]
```

5. views.py中需要添加视图函数及相应配置

```python
import json
from app.geetest import GeetestLib

pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"
mobile_geetest_id = "7c25da6fe21944cfe507d2f9876775a9"
mobile_geetest_key = "f5883f4ee3bd4fa8caec67941de1b903"


def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


def pcvalidate(request):
    if request.method == "POST":
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]

        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)

        result = "<html><body><h1>登录成功</h1></body></html>" if result else "<html><body><h1>登录失败</h1></body></html>"
        return HttpResponse(result)
    return HttpResponse("error")


def pcajax_validate(request):

    if request.method == "POST":
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        print("status",status)
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status":"success"} if result else {"status":"fail"}
        return HttpResponse(json.dumps(result))
    return HttpResponse("error")
```


6. 至此，滑动验证码完成了一半，接下来的一部分要在login.html和login.js文件中完成



###### 1.4 login.html页面
1. 创建页面
	- 注意页面中滑动验证码部分的html标签属性及属性值

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>用户登陆-cms</title>
    <link rel="stylesheet" href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/login.css">
</head>
<body>

<div class="container  container-position">
    <div class="row">
        <div class="col-md-4 col-md-offset-5">
            <p class="title">登陆博客——let's funking the bug</p>
        </div>
    </div>
    <div class="row">
        <div class="col-md-4 col-md-offset-4">
            <!-- form 表单 -->
            <form class="form-horizontal" novalidate>
                {% csrf_token %}
                <div class="form-group">
                    <label for="id_username" class="col-sm-4 control-label text-justify">用户名</label>
                    <div class="col-sm-8">
                        {{ form.username }}
                        <span id="username" class="help-block my-display"></span>
                    </div>
                </div>
                <div class="form-group">
                    <label for="id_password" class="col-sm-4 control-label text-justify">密码</label>
                    <div class="col-sm-8">
                        {{ form.password }}
                        <span id="password" class="help-block"></span>
                    </div>
                </div>


                <div class="form-group">
                    <div class="col-sm-offset-2 col-sm-10">
                        <div class="checkbox">
                            <label>
                                <input type="checkbox"> 下次自动登录
                            </label>
                        </div>
                    </div>
                </div>
            </form>
            <div class="col-md-8 col-md-offset-5">
                <!-- 滑动验证码 -->
                <div class="popup">
                    <button class="btn btn-default"  id="popup-submit" style="font-weight: bold;color: #904">登陆</button>
                    <div id="popup-captcha"></div>
                </div>
                <a id="register" href="/register/" style="color: #990044; font-weight: bold">&nbsp;&nbsp;&nbsp;&nbsp;还没账号？点我注册</a>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.bootcss.com/jquery/3.2.1/jquery.min.js"></script>
<script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
<script src="http://static.geetest.com/static/tools/gt.js"></script>
<script src="/static/login.js"></script>
</body>
</html>
```

2. 使用css渲染页面
	- 在`/static/blog/css`下创建css文件`login.css`

```css
body{
    background-color: #eee;
}

.container-position{
    margin-top: 100px;
}

.my-free-style{
    background-color: white;
}


#register{
    text-decoration: none;
}

.my-display{
    display: block;
}


.title{
    margin-left: -35px;
    font-size: 20px;
    color: #904;
    font-weight: bold;
    margin-bottom: 25px;
}

```


###### 1.5 前后端交互
1. 使用Ajax提交用户登陆信息

```javascript


```


2. 视图函数

```python
def login(request):
    if request.method == 'GET':
        form = LoginForm(request=request)
        return render(request, 'login.html', {'form': form})
    elif request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if not form.is_valid():
            data = {'form_errors': form.errors}
            return HttpResponse(dumps(data))        # {"form_errors": {"username": ["\u7528\u6237\u540d\u4e0d\u80fd\u4e3a\u7a7a"], "password": ["\u5bc6\u7801\u4e0d\u80fd\u4e3a\u7a7a"]}}

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user_queryset = models.UserInfo.objects.filter(username=username, password=password)
        if not user_queryset:
            form.add_error(field='password', error='用户名或密码错误')
            data = {'form_errors': form.errors}
            return HttpResponse(dumps(data))
        else:
            request.session[settings.SESSION_KEY] = {"username": username}
            data = {'success': True}
            return HttpResponse(dumps(data))
``` 






