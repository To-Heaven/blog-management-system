1. this

```
$("table").on('click', '#delete', function () {
    var that = this;
    $.ajax({
        url: $("#delete").parent().attr('value'),
        type: 'get',
        success: function (data) {
            data = JSON.parse(data);
            if (data['is_success']){
                $(that).parent().parent().parent().remove();
                // console.log(that);      // button 标签
                // console.log(this)       // {url: "/manage/delArticle/3/", type: "GET", isLocal: false, global: true, processData: true, …}
            }else {
                swal({
            title: '错误',
            text: data['error_msg'],
            type: 'warning',
            confirmButtonColor: '#3085d6',
            confirmButtonText: '确定',
            showCloseButton: true,
        })
        }
        }
    })
});
```

2. 多选框，服务端接收到的值

```javascript
# ajax 发送的数据

```

```python
def addArticle(request):
    if request.method == 'GET':
        form = BaseArticleForm()
        type_categorys = models.TypeCategory.objects.all()
        categorys = models.Category.objects.filter(blog__user__username=request.session.get('username'))
        tags = models.Category.objects.filter(blog__user__username=request.session.get('username'))
        return render(request, 'addArticle.html', {"form": form, "categorys": categorys,
                                               "tags": tags, "type_categorys": type_categorys})
    elif request.method == 'POST':
        tags = [int(tag_id) for tag_id in request.POST.getlist('tags[]')]           # 前端发送的tags被转换成了tags[]
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
```