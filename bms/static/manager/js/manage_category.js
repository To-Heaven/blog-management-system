$("#submit_category").click(function () {
    $(".has-error").removeClass('has-error');
    $(".form-group span").text('');
   $.ajax({
       url: '/manage/addCategory/',
       type: 'post',
       data: {
           csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
           title: $("#id_title").val(),
           description: $("#id_description").val()
       },
       success: function (data) {
           data = JSON.parse(data);
           if (data.is_success){
               window.location.href = data.location_href;
           }else {
               for (var error_key in data.error_msg){
                   $("#"+error_key).parent().parent().addClass('has-error');
                   $("#"+error_key).text(data.error_msg[error_key][0]);
               }
           }
       }
   })
});


$("#deleteCategory").click(function () {
    $.ajax({
        url: $("#deleteCategory").parent().attr('del_category_url'),
        type: 'get',
        success: function (data) {
            data = JSON.parse(data);
           if (data.is_success){

           }
        }
    })
});