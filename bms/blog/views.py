import datetime
import json
from json import dumps
from django.shortcuts import render, HttpResponse, redirect
from hashlib import sha256
from django.db.models import Count, Sum
from django.db.models import F
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.db import transaction

from blog.forms import RegisterForm, LoginForm
from blog import models
from blog.geetest import GeetestLib

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


def login(request):
    if request.method == 'GET':
        form = LoginForm(request=request)
        return render(request, 'login.html', {'form': form})
    elif request.method == 'POST':                                  # 登陆验证开始
        form = LoginForm(request=request, data=request.POST)
        if not form.is_valid():                                     # 验证信息格式错误
            data = {'form_errors': form.errors}
            return HttpResponse(dumps(data))

        username = form.cleaned_data['username']
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


def logout(request):
    request.session.flush()
    return redirect('/login/')

# def personal_site(request, username):
#     user_queryset = models.UserInfo.objects.filter(username=username)
#     if not user_queryset:
#         return render(request, '404.html')
#     time_dict = {}
#     articles = models.Article.objects.filter(blog__user__username=username)
#     for article in articles:
#         str_time = article.create_time.strftime(format="%Y-%m")
#         if str_time in time_dict:
#             time_dict[str_time] += 1
#         else:
#             time_dict[str_time] = 1
#     return render(request, 'personnal_site.html', {"user": user_queryset[0], "time_dict": time_dict})


def personal_site(request, username):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, '404.html')

    categorys = models.Category.objects.filter(blog__user=user).annotate(c=Count("article__id")).values_list('title',
                                                                                                             'c', 'id')
    tags = models.Tag.objects.filter(blog__user=user).annotate(c=Count("article__id")).values_list('title', 'c', 'id')
    dates = models.Article.objects.extra(select={'create_date_format': 'strftime("%%Y/%%m", create_time)'}).values_list(
        'create_date_format').annotate(c=Count("id")).values_list('create_date_format', 'c')

    return render(request, 'personnal_site.html',
                  {"categorys": categorys, "tags": tags, "dates": dates, "username": username})


def homesite(request, type_category=None, para=None, para_content=None, username=None, article_id=None,*args, **kwargs):
    if type_category:
        articles = models.Article.objects.filter(type_category_id=type_category)
        type_category_obj = models.TypeCategory.objects.get(id=type_category)
        return render(request, 'categorytype_articles.html', {"articles": articles, "type_category_obj": type_category_obj})

    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, '404.html')

    categorys = models.Category.objects.filter(blog__user=user).annotate(c=Count("article__id")).values_list('title','c', 'id')
    tags = models.Tag.objects.filter(blog__user=user).annotate(c=Count("article__id")).values_list('title', 'c', 'id')
    dates = models.Article.objects.filter(blog__user__username=username).\
        extra(select={'create_date_format': 'strftime("%%Y/%%m", create_time)'}).\
        values_list('create_date_format').annotate(c=Count("id")).values_list('create_date_format', 'c')

    if para:
        if para == 'category':
            articles = models.Article.objects.filter(category_id=para_content)
        elif para == 'tag':
            articles = models.Article.objects.filter(tags__id=para_content)
        elif para == 'date':
            year, month = para_content.split(r'/')
            articles = models.Article.objects.filter(blog__user__username=username, create_time__year=year, create_time__month=month)
        return render(request, 'personnal_site.html',{"articles": articles, "categorys": categorys, "tags": tags, "dates": dates, "user": user})
    elif article_id:
        article = models.Article.objects.filter(id=article_id).first()
        if not article:
            return render(request, '404.html')
        return render(request, 'personnal_article.html', {'article':article, "categorys": categorys, "tags": tags, "dates": dates, "user": user})
    articles = models.Article.objects.filter(blog__user__username=username).order_by('-create_time')
    return render(request, 'personnal_site.html', {"articles": articles, "categorys": categorys, "tags": tags, "dates": dates, "user": user})


def updown(request, username=None, option=None, article_id=None):
    user_id = request.POST.get('user_id')
    article = models.Article.objects.filter(id=article_id)
    try:
        if option == 'up':
            models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_like=True)
            article.update(up_count=F('up_count')+1)
        else:
            models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_like=False)
            article.update(down_count=F('down_count') + 1)
    except IntegrityError:
        data = {'is_success': False, "error_msg": '你只能点一次赞或反对', "up_count": article[0].up_count, "down_count": article[0].down_count}
    except Exception as e:
        print(e)
        data = {'is_success': False, "error_msg": '服务端出现了小问题，请稍后再试', "up_count": article[0].up_count, "down_count": article[0].down_count}
    else:
        data = {'is_success': True, "success_msg": '谢谢你哒评价', "up_count": article[0].up_count, "down_count": article[0].down_count}
    return HttpResponse(dumps(data))


def pull_comment(request, username=None, article_id=None):
    article = models.Article.objects.filter(id=article_id)
    user_id = request.POST.get('user_id')
    user = models.UserInfo.objects.filter(id=user_id)
    content = request.POST.get('content')
    father_comment_id = request.POST.get('father_comment_id')
    if not content:
        data = {'is_empty': True}
        return HttpResponse(dumps(data))
    create_time = datetime.datetime.now()
    if father_comment_id:
        comment = models.Comment.objects.create(user=user[0], article=article[0], create_time=create_time, content=content, father_comment_id_id=int(father_comment_id))
    else:
        comment = models.Comment.objects.create(user=user[0], article=article[0], create_time=create_time, content=content)
    data = {
        'is_empty': False,
        'content': content,
        'username': user[0].username,
        'avatar_url': user[0].avatar.url,
        'create_time': create_time.strftime('%Y-%m-%d %H:%M:%S'),
        'up_count': comment.up_count,
        'down_count': comment.down_count,
        'comment_user_id': comment.user.id,
        'comment_user_name': comment.user.username,
        'comment_id': comment.id,
        'current_user_id': request.session.get("id"),
        'father_comment_id': father_comment_id
    }
    return HttpResponse(dumps(data))


def load_comments(request, article_id=None):
    comments = models.Comment.objects.filter(article_id=article_id).values('id', 'content',
                                                                           'father_comment_id',
                                                                           'up_count', 'down_count',
                                                                           'user__username', 'user__avatar',
                                                                           'create_time', 'user_id', 'user__username',
                                                                           )
    for comment in comments:
        comment["child_comments"] = []
        comment['create_time'] = comment['create_time'].strftime('%Y-%m-%d %H:%M:%S')
        comment['current_user'] = request.session.get('username')
    print(comments)

    comment_dict = {}
    for comment in comments:
        comment_dict[comment['id']] = comment
        if comment['father_comment_id']:
            comment_dict[comment['father_comment_id']]['child_comments'].append(comment)

    comment_list = []
    for comment in comment_dict.values():
        if not comment['father_comment_id']:
            comment_list.append(comment)

    return HttpResponse(dumps(comment_list))
