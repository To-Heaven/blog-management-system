# 用户登陆

## 功能
#### 1.登陆验证
- 登陆验证发送的请求也是使用Ajax实现，类似用户注册，但是会将用户密码进行匹配
	- 如果用户输入的密码有误，将返回错误信息并渲染到页面上
	- 如果用户输入的密码正确，在视图函数中，还要将用户的一些必要信息保存到当前会话session中，比如用户id、登录名、头像再服务端存储的路径等等
	- 代码如下

```python
def login(request):
    if request.method == 'GET':
        form = LoginForm(request=request)
        return render(request, 'login.html', {'form': form})        
    elif request.method == 'POST':                                  # 登陆验证开始
        form = LoginForm(request=request, data=request.POST)
        if not form.is_valid():                                     # 验证信息格式错误
            data = {'form_errors': form.errors}
            return HttpResponse(dumps(data))
        
        username = form.cleaned_data['username']					# 开始匹配用户名和密码
        raw_password = form.cleaned_data['password']
        shaObj = sha256(username.encode(encoding='utf-8'))
        shaObj.update(raw_password.encode(encoding='utf-8'))
        password = shaObj.hexdigest()	
        
        user_queryset = models.UserInfo.objects.filter(username=username, password=password)
        if not user_queryset:                                        # 登陆失败
            form.add_error(field='password', error='用户名或密码错误')
            data = {'form_errors': form.errors}                       
            return HttpResponse(dumps(data))                         # 返回错误信息
        else:
            avatar_url = user_queryset[0].avatar                     # 登陆成功，初始化session数据
            request.session['username'] = username
            request.session['id'] = user_queryset[0].id
            request.session['avatar_url'] = avatar_url.url
            data = {'success': True}
            return HttpResponse(dumps(data))
```


#### 2. 验证码
> 简单的验证码比如图片验证码由于太过容易被程序识别，在本项目中，我选择滑动验证码，滑动验证码插件使用起来很方便，只需要我们修改一下服务端配置和前端js代码

1. 首先修改setting.py配置，修改TEMPLATES配置项如下

```
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
                'social_django.context_processors.backends',  # 验证码配置项
                'social_django.context_processors.login_redirect',  # 验证码配置项
            ],
        },
    },
]
```

2. 导入模块视图函数
	- 将滑动验证码`geetest.py`文件移至blog下
	- 导入`geetest`至`views.py`
	- 添加视图函数及配置项

```python
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

        print("status", status)
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
        print("status", status)
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail"}
        return HttpResponse(json.dumps(result))
    return HttpResponse("error")
```

3. 修改urls.py，需要增加三组路由映射关系

```python
    url(r'^pc-geetest/register', views.pcgetcaptcha, name='pcgetcaptcha'),
    url(r'^pc-geetest/validate$', views.pcvalidate, name='pcvalidate'),
    url(r'^pc-geetest/ajax_validate', views.pcajax_validate, name='pcajax_validate'),
```


4. 最最重要的一部分，修改我们的js文件
	-  在js文件中，将我们的Ajax代码嵌入到验证码验证成功之后的回调函数中，这样就可以保证我们在滑动验证成功之后向服务端发送Ajax请求
	-  **还有一点要注意的是**，用户可能是跳转到login界面的，比如用户未登录的时候，如果要评论一篇文章，会跳转到登陆界面，这个时候在前端js代码中，我会使用`localStorage`将用户跳转之前的页面路径保存下来，当用户登陆成功之后，就对localStorage中的数据进行判断，如果判断出登陆成功之后需要跳转，就会跳转到指定的路径而非博客系统主页
		-  实现这种调准的方式有很多，除了使用localStorage之外，还可以使用"document.referrer"或者cookie实现
	- 代码如下

```javascript
var handlerPopup = function (captchaObj) {
    $("#popup-submit").click(function () {
        captchaObj.show();
    });

    // 验证码验证成功之后的回调函数
    captchaObj.onSuccess(function () {
        var validate = captchaObj.getValidate();
        
        // 发送Ajax请求
        $.ajax({
            url: "/login/",
            type: "post",
            dataType: "json",
            data: {
                username: $('#id_username').val(),
                password: $('#id_password').val(),
                "csrfmiddlewaretoken": $("input:hidden").val(),
                geetest_challenge: validate.geetest_challenge,
                geetest_validate: validate.geetest_validate,
                geetest_seccode: validate.geetest_seccode
            },
            success: function (data) {
                
                // 用户登陆成功
                if (data["success"]) {
                    var redirect = localStorage.getItem("redirect");                // 从localStorage中获取路径
                    if (localStorage.getItem("target_url") && redirect==='OK'){
                        window.location.href = localStorage.getItem("target_url");  // 登陆后跳转到登陆前的页面
                        localStorage.setItem("redirect", "NO")                      // 跳转之后再次设置为NO，相当于一个"开关" 
                    }else {
                        window.location.href = "/home/";                            // 跳转至博客系统主页
                    }
                }
                
                // 用户登陆失败，渲染错误信息
                if (data["form_errors"]) {
                    for (var key in data["form_errors"]) {
                        $("#" + key).text(data["form_errors"][key]);
                        $("#" + key).parent().parent().addClass('has-error');
                    }
                }
            }
        })
    });
    captchaObj.appendTo("#popup-captcha");
};


// 一下为滑动验证部分，一般不需要修改
// 将验证码加到id为captcha的元素里
// 验证开始需要向网站主后台获取id，challenge，success（是否启用failback）
$.ajax({
    url: "/pc-geetest/register?t=" + (new Date()).getTime(), // 加随机数防止缓存
    type: "get",
    dataType: "json",
    success: function (data) {
        // 使用initGeetest接口
        // 参数1：配置参数
        // 参数2：回调，回调的第一个参数验证码对象，之后可以使用它做appendTo之类的事件
        initGeetest({
            gt: data.gt,
            challenge: data.challenge,
            product: "popup", // 产品形式，包括：float，embed，popup。注意只对PC版验证码有效
            offline: !data.success // 表示用户后台检测极验服务器是否宕机，一般不需要关注
        }, handlerPopup);
    }
});

```

