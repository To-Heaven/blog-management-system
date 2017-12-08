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

// 图片预览 方法一
// $("input:file").change(function () {
//    var fileObj = this.files[0];
//
//    var readerObj = new FileReader();
//    readerObj.readAsDataURL(fileObj);
//
//    readerObj.onload = function () {
//        $("#img_avatar")[0].src = this.result;
//    }
//
// });

// 图片预览方法二 
$("input:file").change(function () {
   $("#img_avatar")[0].src = window.URL.createObjectURL($(this)[0].files[0]);
});


// ======== 动态背景 =======
;(function() {
    'use strict';

    var c = document.getElementById('c');
    var ctx = c.getContext('2d');
    var w = c.width = window.innerWidth;
    var h = c.height = window.innerHeight;
    var cx = w / 2;
    var cy = h / 2;
    var P = function(x, y) {
        this.x = x;
        this.y = y;
        this.vx = 0;
        this.vy = 0;
        this.r = 1 + Math.random() * 10;
        this.sa = Math.random() * Math.PI * 2;
        this.ea = Math.random() * Math.PI * 2;
        this.rt = Math.random() * Math.PI * 2;
        this.vrt = 0;
        this.h = 0;
    };
    P.prototype = {
        constructor: P,
        update: function() {
            this.vx += Math.random() * 0.1 - 0.05;
            this.vy += Math.random() * 0.1 - 0.05;
            this.vrt += Math.random() * 0.02 - 0.01;
            this.x += this.vx;
            this.y += this.vy;
            this.rt += this.vrt;

            var dx = cx - this.x;
            var dy = cy - this.y;
            var d = Math.sqrt(dx * dx + dy * dy);

            this.h = dx / d * 360;

            if (this.x < 0) {
                this.x = 0;
                this.vx *= -1;
            }
            if (this.x > w) {
                this.x = w;
                this.vx *= -1;
            }
            if (this.y < 0) {
                this.y = 0;
                this.vy *= -1;
            }
            if (this.y > h) {
                this.y = h;
                this.vy *= -1;
            }
        },
        render: function(ctx) {
            ctx.save();
            ctx.strokeStyle = 'black';
            ctx.fillStyle = 'hsla(' + this.h + ', 100%, 50%, 2.5)';
            ctx.translate(this.x, this.y);
            ctx.rotate(this.rt);
            ctx.beginPath();
            ctx.arc(0, 0, this.r, this.sa, this.ea);
            ctx.fill();
            ctx.stroke();
            ctx.restore();
        }
    };

    var ps = [];
    var p;
    var ctr = 200;

    for (var i = 0; i < ctr; i++) {
        p = new P(Math.random() * w, Math.random() * h);
        ps.push(p);
    }

    requestAnimationFrame(function loop() {
        requestAnimationFrame(loop);
        ctx.clearRect(0, 0, w, h);
        for (var i = 0; i < ctr; i++) {
            p = ps[i];
            p.update();
            p.render(ctx);
        }
        for (var i = 0; i < ctr; i++) {
            var p1 = ps[i];
            for (var j = i + 1; j < ctr; j++) {
                var p2 = ps[j];
                var dx = p1.x - p2.x;
                var dy = p1.y - p2.y;
                var d = Math.sqrt(dx * dx + dy * dy);
                if (d < 50) {
                    ctx.strokeStyle = 'rgba(0, 0, 0, 2.5)';
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        }
    });

})();