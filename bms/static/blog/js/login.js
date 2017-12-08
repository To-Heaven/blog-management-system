var handlerPopup = function (captchaObj) {
    $("#popup-submit").click(function () {
        captchaObj.show();
    });

    // 验证码验证成功之后的回调函数
    captchaObj.onSuccess(function () {
        var validate = captchaObj.getValidate();

        // 发送Ajax请求
        $.ajax({
            url: "/login/",
            type: "post",
            dataType: "json",
            data: {
                username: $('#id_username').val(),
                password: $('#id_password').val(),
                "csrfmiddlewaretoken": $("input:hidden").val(),
                geetest_challenge: validate.geetest_challenge,
                geetest_validate: validate.geetest_validate,
                geetest_seccode: validate.geetest_seccode
            },
            success: function (data) {

                // 用户登陆成功
                if (data["success"]) {
                    var redirect = localStorage.getItem("redirect");                // 从localStorage中获取路径
                    if (localStorage.getItem("target_url") && redirect==='OK'){
                        window.location.href = localStorage.getItem("target_url");  // 登陆后跳转到登陆前的页面
                        localStorage.setItem("redirect", "NO")                      // 跳转之后再次设置为NO，相当于一个"开关"
                    }else {
                        window.location.href = "/home/";                            // 跳转至博客系统主页
                    }
                }

                // 用户登陆失败，渲染错误信息
                if (data["form_errors"]) {
                    for (var key in data["form_errors"]) {
                        $("#" + key).text(data["form_errors"][key]);
                        $("#" + key).parent().parent().addClass('has-error');
                    }
                }
            }
        })
    });
    captchaObj.appendTo("#popup-captcha");
};


// 一下为滑动验证部分，一般不需要修改
// 将验证码加到id为captcha的元素里
// 验证开始需要向网站主后台获取id，challenge，success（是否启用failback）
$.ajax({
    url: "/pc-geetest/register?t=" + (new Date()).getTime(), // 加随机数防止缓存
    type: "get",
    dataType: "json",
    success: function (data) {
        // 使用initGeetest接口
        // 参数1：配置参数
        // 参数2：回调，回调的第一个参数验证码对象，之后可以使用它做appendTo之类的事件
        initGeetest({
            gt: data.gt,
            challenge: data.challenge,
            product: "popup", // 产品形式，包括：float，embed，popup。注意只对PC版验证码有效
            offline: !data.success // 表示用户后台检测极验服务器是否宕机，一般不需要关注
        }, handlerPopup);
    }
});


// 以下为login页面背景部分
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