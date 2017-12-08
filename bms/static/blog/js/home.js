// 左侧菜单
$(".topic-style span.btn").click(function () {
    $(this).parent().next().toggleClass('hides');
    $(this).parent().parent().siblings().children('.menu-item').addClass('hides');
});


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


