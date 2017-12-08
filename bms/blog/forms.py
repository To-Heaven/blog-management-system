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
