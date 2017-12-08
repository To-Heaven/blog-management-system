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