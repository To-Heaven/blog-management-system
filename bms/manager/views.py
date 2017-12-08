from django.shortcuts import render, HttpResponse, redirect
import os
import simplejson as json
import datetime

from blog import models
from bms import settings
from manager.forms import BaseArticleForm, CategoryForm


def manage_main(request):
    articles = models.Article.objects.filter(blog__user__username=request.session.get("username"))
    return render(request, 'manage_home.html', {"articles": articles})


def delArticle(request, article_id=None):
    article_queryset = models.Article.objects.filter(id=article_id)
    if article_queryset:
        article = article_queryset[0]
        article.delete()
        data = {"is_success": True}
    else:
        data = {"is_success": False, 'error_msg': '没有篇文章'}
    return HttpResponse(json.dumps(data))


def addArticle(request):
    if request.method == 'GET':
        form = BaseArticleForm()
        type_categorys = models.TypeCategory.objects.all()
        categorys = models.Category.objects.filter(blog__user__username=request.session.get('username'))
        tags = models.Category.objects.filter(blog__user__username=request.session.get('username'))
        return render(request, 'addArticle.html', {"form": form, "categorys": categorys,
                                                   "tags": tags, "type_categorys": type_categorys})
    elif request.method == 'POST':
        tags = [int(tag_id) for tag_id in request.POST.getlist('tags[]')]  # 前端发送的tags被转换成了tags[]
        category_id = int(request.POST.get('category'))
        type_category_id = int(request.POST.get('type_category'))
        form = BaseArticleForm(data=request.POST)
        username = request.POST.get('username')

        if form.is_valid():
            content = form.cleaned_data['content']
            del form.cleaned_data['content']
            article_detail = models.ArticleDetail.objects.create(content=content)
            form.cleaned_data['category_id'] = int(category_id)
            form.cleaned_data['type_category_id'] = int(type_category_id)
            form.cleaned_data['article_detail'] = article_detail
            blog = models.Blog.objects.filter(user__username=username).first()
            form.cleaned_data['blog'] = blog
            article = models.Article.objects.create(**form.cleaned_data)
            # article.tags.add([int(tag_id) for tag_id in tags])      #Cannot use add() on a ManyToManyField which specifies an intermediary model. Use blog.Tag2Article's Manager instead.
            for tag_id in tags:
                models.Tag2Article.objects.create(tag_id=tag_id, article=article)
            data = {"is_success": True, "location_href": '/manage/home/'}
            return HttpResponse(json.dumps(data))
        else:
            if not tags: form.errors['tags'] = ['至少要有一个标签']
            if not category_id: form.errors['category'] = ['必须选择一个分类']
            if not type_category_id: form.errors['type_category'] = ['必须选择一个类型']
            data = {"is_success": False, "error_msg": form.errors}
            return HttpResponse(json.dumps(data))


def editArticle(request, article_id):
    if request.method == 'GET':
        initial_dict = {
            "title": models.Article.objects.filter(id=article_id)[0].title,
            "summary": models.Article.objects.filter(id=article_id)[0].summary,
            "content": models.ArticleDetail.objects.filter(article__id=article_id)[0].content
        }
        user_id = request.session.get('id')
        categorys = models.Category.objects.filter(blog__user__id=user_id)
        type_categorys = models.TypeCategory.objects.all()
        tags = models.Tag.objects.filter(blog__user__id=user_id)
        current_category = models.Category.objects.filter(article__id=article_id)
        current_tags = [obj.id for obj in models.Tag.objects.filter(article__id=article_id)]
        current_type_category = models.TypeCategory.objects.filter(article__id=article_id)

        form = BaseArticleForm(initial=initial_dict)
        return render(request, 'editArticle.html', {"form": form, "categorys": categorys,
                                                    "type_categorys": type_categorys, "tags": tags,
                                                    "current_category": current_category, "current_tags": current_tags,
                                                    "current_type_category": current_type_category,
                                                    "article_id": article_id})
    elif request.method == 'POST':
        tag_ids = [int(tag_id) for tag_id in request.POST.getlist('tags[]')]  # 前端发送的tags被转换成了tags[]
        category_id = int(request.POST.get('category'))
        type_category_id = int(request.POST.get('type_category'))
        form = BaseArticleForm(data=request.POST)
        username = request.POST.get('username')

        if form.is_valid():
            content = form.cleaned_data['content']
            del form.cleaned_data['content']
            article_detail = models.ArticleDetail.objects.filter(article__id=article_id)
            if article_detail:
                article_detail.update(content=content)
            form.cleaned_data['category_id'] = int(category_id)
            form.cleaned_data['type_category_id'] = int(type_category_id)
            form.cleaned_data['article_detail'] = article_detail[0]
            blog = models.Blog.objects.filter(user__username=username).first()
            form.cleaned_data['blog'] = blog
            article = models.Article.objects.filter(id=article_id)
            if article:
                print(form.cleaned_data)
                article.update(**form.cleaned_data)
            # article.tags.add([int(tag_id) for tag_id in tags])      #Cannot use add() on a ManyToManyField which specifies an intermediary model. Use blog.Tag2Article's Manager instead.

            article[0].tags.clear()
            [models.Tag2Article.objects.create(tag_id=tag, article=article[0]) for tag in tag_ids]
            data = {"is_success": True, "location_href": '/manage/home/'}
            return HttpResponse(json.dumps(data))
        else:
            if not tag_ids: form.errors['tags'] = ['至少要有一个标签']
            if not category_id: form.errors['category'] = ['必须选择一个分类']
            if not type_category_id: form.errors['type_category'] = ['必须选择一个类型']
            data = {"is_success": False, "error_msg": form.errors}
            return HttpResponse(json.dumps(data))


def uploadFile(request):
    print(request.FILES)
    fileObj = request.FILES.get('imgFile')
    fileName = fileObj.name
    filePath = os.path.join(settings.MEDIA_ROOT, 'article_files', fileName)
    with open(filePath, 'wb') as fb:
        for chunk in fileObj.chunks():
            fb.write(chunk)
    response_data = {
        'error': 0,
        'url': '/media/article_files/' + fileName + '/'
    }
    return HttpResponse(json.dumps(response_data))


def listCategory(request):
    categorys = models.Category.objects.filter(blog__user__username=request.session.get('username'))
    return render(request, 'listCategory.html', {"categorys": categorys})


def addCategory(request):
    if request.method == 'GET':
        form = CategoryForm()
        return render(request, 'addCategory.html', {"form": form})
    elif request.method == 'POST':
        print(request.body)
        print(request.POST)
        form = CategoryForm(data=request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            data = {"is_success": True, "location_href": "/manage/listCategory/"}
            blog_obj = models.Blog.objects.filter(user__username=request.session.get('username'))
            if blog_obj:
                form.cleaned_data['blog'] = blog_obj[0]
            form.cleaned_data['create_time'] = datetime.datetime.now()
            form.cleaned_data['article_count'] = 0
            models.Category.objects.create(**form.cleaned_data)
            return HttpResponse(json.dumps(data))
        else:
            for item in form.errors:
                print(item)
            data = {"is_success": False, "error_msg": form.errors}
            return HttpResponse(json.dumps(data))


def editCategory(request, category_id=None):
    pass


def delCategory(request, category_id=None):
    category_queryset = models.Category.objects.filter(id=category_id)
    print(category_queryset)
    if category_queryset:
        category_queryset.delete()
        data = {"is_success": True, "location_href": '/manage/listCategory/'}
    else:
        data = {"is_success": False, "error_msg": '该文章分类不存在'}
    return HttpResponse(json.dumps(data))

