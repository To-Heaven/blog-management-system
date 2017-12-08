var edit_editor = KindEditor.create('#id_content', {
    uploadJson: '/manage/uploadFile/',
    extraFileUploadParams: {
        csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val()
    }
});


$("#edit_submit").click(function () {
    edit_editor.sync();          // 必须有这个，才能获取数据
    var content = $("#id_content").val();
    var title = $("#id_title").val();
    var type_category = $("#id_type_category").val();
    var category = $("#id_category").val();
    var tags = $("#id_tag").val();
    var summary = $("#id_summary").val();
    var username = $("#current_user").val();
    $.ajax({
        url: $("#edit_url").val(),
        type: 'post',
        data: {
            content: content,
            title: title,
            type_category: type_category,
            category: category,
            tags: tags,
            summary: summary,
            username: username,
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val()
        },
        success: function (data) {
            data = JSON.parse(data);
            console.log(data)
            if (data['is_success']){
                window.location.href = data['location_href'];
            }else {
                for (var key in data['error_msg']){
                    console.log(key);
                    $("#"+key).parent().parent().addClass('has-error');
                    $("#"+key).text(data['error_msg'][key][0]);
                }
            }
        }
    })
});



