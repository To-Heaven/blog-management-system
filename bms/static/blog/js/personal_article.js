$(".like_article a").click(function () {
    if (!$("#request_user").val()) {
        swal({
            title: '你还没有登陆',
            text: '先去登陆吗，待会儿会跳转回来呦',
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: '确定登陆！',
            showCloseButton: true,
        })
    } else {
        if (this.name == 'up') {
            var url = $("#article_up").val();
        } else if (this.name == 'down') {
            var url = $("#article_down").val();
        }
        $.ajax({
            url: url,
            type: 'post',
            data: {
                user_id: $('#request_user').attr('user_id'),
                "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val()
            },
            success: function (data) {
                data = JSON.parse(data);
                console.log(data);
                if (data.is_success) {
                    $(".article_up_count").text(data.up_count);
                    $(".article_down_count").text(data.down_count);
                    swal({
                        type: "success",
                        title: data.success_msg,
                        text: '2秒后自动关闭。',
                        timer: 2000
                    })
                } else {
                    swal({
                        type: "error",
                        title: data.error_msg,
                        text: '2秒后自动关闭。',
                        timer: 2000
                    })
                }
            }
        })

    }
    // 跳转函数，需要嵌套在点赞函数中
    $(".swal2-confirm").click(function () {
        localStorage.setItem("target_url", window.location.href);
        window.location.href = '/login/'

    });
});

var father_comment_id = null;

// $(".reply").click(function () {
//     father_comment_id = $(this).next().attr('root_comment_id');
// });

$("#event_father, #comment_tree").on("click", ".reply", function () {
    father_comment_id = $(this).next().attr('root_comment_id');
    var root_comment_user = $(this).next().attr('root_comment_username');
    $("#hidden_reply").removeClass('hides');
    $("#hidden_reply").html("@" + root_comment_user + ":");
    $("#current_user_comment").focus();
});



$("#submit_comment").click(function () {
    if (!$("#current_user").attr('name')) {
        // 用户未登录
        swal({
            title: '你还没有登陆',
            text: '先去登陆吗，待会儿会跳转回来呦',
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: '确定登陆！',
            showCloseButton: true,
        })
    } else {
        // 初始化父级评论
        $.ajax({
            url: $('#pull_comment_url').val(),
            type: 'post',
            data: {
                user_id: $('#current_user').attr('user_id'),
                content: $('#current_user_comment').val(),
                "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
                father_comment_id: father_comment_id
            },
            success: function (data) {
                data = JSON.parse(data);
                $("#current_user_comment").val('');
                $("#hidden_reply").addClass('hides');
                if (data.is_empty) {
                    // 显示bootstrap警告框
                    $("#no_comment_alert").removeClass('hides');
                } else {
                    // var content_html = `<div class="col-md-12" id="per_comment"  root_comment_user_id="${data.comment_user_id}" >
                    //                         <div>
                    //                             <img src="${data.avatar_url}" alt="" width="28px" height="28px">
                    //                             <span>${data.username}</span>
                    //                             <span class="comment_info">&nbsp;&nbsp;发表于${data.create_time}</span>
                    //                             <span class="pull-right">
                    //                                 <a class="reply" href="#hidden_reply" style="color: #31b0d5;">回复</a>
                    //                                 <input type="hidden" root_comment_id="${data.comment_id}" root_comment_user_id="${data.comment_user_id}" root_comment_username="${data.comment_user_name}" current_user="${data.current_user_id}">
                    //                             </span>
                    //                         </div>
                    //                         <p>${data.content}</p>
                    //                         <span class="comment_info pull-right">
                    //                             <a href="">支持<i class="fa fa-thumbs-up" aria-hidden="true"></i>(${data.up_count})</a>
                    //                             &nbsp;&nbsp;
                    //                             <a href="">反对<i class="fa fa-thumbs-down" aria-hidden="true"></i>(${data.down_count})</a>
                    //                         </span>
                    //                     </div>`;
                    var content_html = `<div class="col-md-11 pull-right" id="per_comment"  root_comment_id="${data['comment_id']} father_comment_id="${data.father_comment_id} root_comment_user_id="${data['comment_user_id']}" >
                                <div>
                                    <img src="${data['avatar_url']}" alt="" width="28px" height="28px">
                                    <span>${data['comment_user_name']}</span>
                                    <span class="comment_info">&nbsp;&nbsp;发表于${data['create_time']}</span>
                                    <span class="comment_info">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                           <a href="">支持<i class="fa fa-thumbs-up" aria-hidden="true"></i>(${data['up_count']})</a>
                                    &nbsp;&nbsp;
                                           <a href="">反对<i class="fa fa-thumbs-down" aria-hidden="true"></i>(${data['down_count']})</a>
                                     </span>
                                    <span class="pull-right">
                                        <a class="reply" href="#hidden_reply" style="color: #31b0d5;">回复</a>
                                        <input type="hidden" root_comment_id="${data['comment_id']}" root_comment_user_id="${data['comment_user_id']}" root_comment_username="${data['comment_user_name']}" current_user="${data['current_user_id']}">
                                 </span>
                                </div>
                                <p>${data['content']}</p></div>`;

                    var father_comment_id = data['father_comment_id'];
                    $(`[root_comment_id="${father_comment_id}"]`).append(content_html);

                    // 去除无评论提示
                    if ($("#no_comment")) {
                        $("#no_comment").remove("#no_comment");
                    }
                    swal({
                        title: '哎呦~不错哦',
                        html: '你可以在文章下面看见自己评论' +
                        '<a href="#comment_area"><strong>点击传送</strong>></a>',
                        type: 'success',
                        timer:1000
                    })
                }
            }
        })
    }
    // 跳转函数，需要嵌套在点赞函数中
    $(".swal2-confirm").click(function () {
        localStorage.setItem("redirect", "OK");
        localStorage.setItem("target_url", window.location.href);
        window.location.href = '/login/'

    });
});


function generate_html(data) {
    var inner_html = "";
    $.each(data, function (index, comment) {
        var content = comment["content"];
        var comment_str = `<div class="col-md-11 pull-right" id="per_comment"  root_comment_id="${comment['id']}" father_comment_id="${comment['father_comment_id']}"  root_comment_user_id="${comment['user_id']}" >
                                <div>
                                    <img src="/media/${comment['user__avatar']}" alt="" width="28px" height="28px">
                                    <span>${comment['user__username']}</span>
                                    <span class="comment_info">&nbsp;&nbsp;发表于${comment['create_time']}</span>
                                    <span class="comment_info">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                           <a href="">支持<i class="fa fa-thumbs-up" aria-hidden="true"></i>(${comment['up_count']})</a>
                                    &nbsp;&nbsp;
                                           <a href="">反对<i class="fa fa-thumbs-down" aria-hidden="true"></i>(${comment['down_count']})</a>
                                     </span>
                                    <span class="pull-right">
                                        <a class="reply" href="#hidden_reply" style="color: #31b0d5;">回复</a>
                                        <input type="hidden" root_comment_id="${comment['id']}" root_comment_user_id="${comment['user_id']}" root_comment_username="${comment['user__username']}" current_user="${comment['current_user']}">
                                 </span>
                                </div>
                                <p>${content}</p>`
        if (comment['child_comments']){
            var s = generate_html(comment['child_comments']);
            comment_str += s
        }
        comment_str += "</div>";
        inner_html += comment_str
    });

    return inner_html
}

/*
*     function showCommentTree(comment_list) {    
        var html="";

        $.each(comment_list,function (i,comment_dict) {
            var val=comment_dict["content"];
            var commnent_str= '<div class="comment"><div class="content"><span>'+val+'</span></div>';

            if(comment_dict["chidren_commentList"]){
                var s=showCommentTree(comment_dict["chidren_commentList"]);    // [{},{}]
                commnent_str+=s
            }

            commnent_str+="</div>";
            html+=commnent_str
        });

        return html
    }

* */


$.ajax({
    url:$("#load_comments_url").val(),
    type: 'get',
    success: function (data) {
        data = JSON.parse(data);
        inner_html = generate_html(data);
        $("#comment_tree").html(inner_html);
    }
});


// $(".reply").click(function () {
//     var root_comment_user = $(this).next().attr('root_comment_username');
//     $("#hidden_reply").removeClass('hides');
//     $("#hidden_reply").html("@" + root_comment_user + ":");
// })


