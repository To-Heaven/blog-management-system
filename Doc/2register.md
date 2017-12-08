# 用户注册

#### 用户注册概述
###### 表单字段信息
- 用户注册页面需要用户提交的字段信息包括
	- 头像
	- 邮箱
	- 手机号码
	- 昵称
	- 登陆名称
	- 登陆密码
	- 确认登陆密码

###### 功能实现
- 页面form表单使用了Django提供的form组件创建，用户点击注册按钮之后会向服务端发送POST类型的Ajax请求，服务端会使用form组件进行验证并返回响应
	- 如果用户提交信息有误，Ajax将会在页面异步渲染错误
	- 如果用户提交信息验证成功，用户的注册信息就会被保存到数据库，浏览器端接收到响应信息之后会自动跳转到登陆界面

- 注册页面导航条以及页面布局使用Bootstrap前端框架完成。
- 实现了头像预加载功能，用户选择了要上传的头像之后，前端js会在本地找到该图片并渲染到页面，只有当用户提交了该头像数据之后，服务端才会保存该头像

## 代码实现
#### form组件完成登陆验证及前端渲染
- 在blog应用下，forms文件中存放了form组件类，代码如下

```python
# /bms/blog/forms.py

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
        """ 局部钩子函数，验证用户名是否已经存在
        Return:
            如果用户名合法，返回该用户名
        """

        username = self.cleaned_data.get('username')
        if models.UserInfo.objects.filter(username=username):
            raise ValidationError('用户名已存在')

        return username

    def clean_password(self):
        """ 局部钩子函数，验证用户密码是否合法
        Return:
            如果用户密码合法，将返回该用户密码
        """

        password = self.cleaned_data.get('password')
        if password.isdigit():
            raise ValidationError('密码不能全是数字')

        if password.isalpha():
            raise ValidationError('密码不能全是字母')

        return password

    def clean(self):
        """ 全局钩子函数，验证用户两次输入密码是否一致
        Return:
            如果两次输入的密码一致，将返回存放当前验证通过有数据的clean_data对象
        """
        
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError('两次输入的密码不一致')

        return self.cleaned_data
```


#### 预加载图片
- 头像预加载应该在前端来完成，前端头像预加载有多中方式，这里给出两种方式。

```
// 文件路径： /static/blog/register.js


// 第一种方式
$("input:file").change(function () {
   var fileObj = this.files[0];					// 通过input中已选择的文件创建一个对象

   var readerObj = new FileReader();			
   readerObj.readAsDataURL(fileObj);			// 读取文件路径

   readerObj.onload = function () {
       $("#img_avatar")[0].src = this.result;	// 使用result属性返回文件路径
   }

});

// 第二种方式
$("input:file").change(function () {
   $("#img_avatar")[0].src = window.URL.createObjectURL($(this)[0].files[0]);			// 简单粗暴，直接使用window全局对象的createObjectURL获取文件路径
});
```



#### Ajax提交数据和渲染前端页面
- 注册页面前后端交互是通过Ajax完成的
	- 用户注册失败，ajax会将错误信息利用BootStrap渲染至`<span>`标签中
	- 用户注册成功，前端视图函数会返回一个包含跳转页面url路径的值，然后使用`window.location.href`实现跳转

###### 1. ajax提交数据
> 此处使用jQuery提供的Ajax接口

- 这里使用formData提交数据，主要是可读性高，当formdata中包含文件的时候，注意要为Ajax设置参数"contentType"和"processData"的值为`false`

```javascript
// 前后端Ajax数据交互
$(".btn").click(function () {
        // 每次提交初始化页面错误信息
        $("form span").text('');
        $("div.form-group").removeClass('has-error');

        // 封装表单数据到formData对象中
        var formData = new FormData();
        formData.append("email", $('#id_email').val());
        formData.append("telephone", $('#id_telephone').val());
        formData.append("username", $('#id_username').val());
        formData.append("nick_name", $('#id_nick_name').val());
        formData.append("password", $('#id_password').val());
        formData.append("confirm_password", $('#id_confirm_password').val());
        formData.append("csrfmiddlewaretoken", $('input:hidden').val());
        formData.append("avatar", $('input:file')[0].files[0]);

        // Ajax
        $.ajax({
            url: '/register/',
            type: 'POST',
            data: formData,
            contentType: false,         // 不要忘了这两个参数
            processData: false,
            success: function (data) {
                data = JSON.parse(data);

                // 验证成功
                if (data["success"]){
                    window.location.href = data["location_href"];
                }

                // 验证失败
                if (data["form_errors"]) {
                    for (var key in data["form_errors"]) {
                        for (var key in data["form_errors"]) {

                            // 渲染验证错误信息
                            if (key == "__all__") {
                                $("#confirm_password").text(data["form_errors"][key]);
                                $("#confirm_password").parent().parent().addClass('has-error');
                            } else {
                                $("#" + key).text(data["form_errors"][key]);                // 注意将span标签的id值设置成key，这样可以方便渲染错误信息
                                $("#" + key).parent().parent().addClass('has-error');
                            }
                        }
                    }
                }
            }
        })
    });
```

###### 2.视图函数
- 这里视图使用了FBV(视图函数)，没有使用CBV，大概是脑子抽风了，其实使用CBV更pythonic，可读性更高。
	- 对于用户的密码，我使用了`hashlib`进行了加密，同样的，当用户登录之后，会将用户登陆提交的面膜进行加密处理后再与数据库中数据进行比较判断
	- FBV代码如下

```python
def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})
    elif request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if not form.is_valid():                                 # 验证失败，返回错误信息
            data = {'form_errors': form.errors}
            return HttpResponse(dumps(data))
        
        form.cleaned_data['join_time'] = datetime.datetime.now()
        del form.cleaned_data['confirm_password']               # 组装创建记录所需字段西悉尼

        avatar = request.FILES.get('avatar')                    # 获取用户头像
        if avatar:
            form.cleaned_data['avatar'] = avatar

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        shaObj = sha256(username.encode(encoding='utf-8'))
        shaObj.update(password.encode(encoding='utf-8'))
        form.cleaned_data['password'] = shaObj.hexdigest()      # 对用户密码sha256加密
        
        models.UserInfo.objects.create(**form.cleaned_data)     # 创建用户

        data = {'success': True, "location_href": '/login/'}  
        return HttpResponse(dumps(data))

```