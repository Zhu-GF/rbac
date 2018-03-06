
$(function () {
    $('.menu-header').click(function () {
        $(this).next().removeClass('hide').parent().siblings('.menu-body').addClass('hide')
    })
})
