var slideIndex = 1;

function plusSlides(n) {
    showSlides(slideIndex += n);
}

function currentSlide(n) {
    showSlides(slideIndex = n);
}

function showSlides(n) {
    var i;
    var slides = document.getElementsByClassName("mySlides");
    var dots = document.getElementsByClassName("demo");
    if (n > slides.length) {
        slideIndex = 1
    }
    if (n < 1) {
        slideIndex = slides.length
    }
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }
    slides[slideIndex - 1].style.display = "block";
    dots[slideIndex - 1].className += " active";
}

(function ($) {
    $(document).ready(function () {
        $("[id^=lot-images]").click(function () {
            var lot = $(this).attr('id').split('_')[1];
            $.ajax({
                type: 'POST',
                url: '/ajax_getimages/',
                data: {lot: lot},
                success: function (data) {
                    console.log(data);
                    set_parameters_to_modal(data);
                }
            });
            $(".lot-images").show(1000);
        });

        // close sign in popup window
        $("#lot_images_close").click(function () {
            $(".lot-images").hide(1000);
        });

        function set_parameters_to_modal(data) {
            slideIndex = 1;
            $('#lot_images_title').text(data.lot_name);
            $('#lot_images_lot').text('LOT # ' + data.lot);
            var target = $('#vehicle-images');
            target.empty();
            var len = data.images.length;
            for (var i = 0; i < len; i ++) {
                target.append('<div class="mySlides" style="display: ' + (i ? 'none' : 'block') + '">\n' +
                    '               <div class="numbertext">' + (i + 1).toString()  + ' / ' +  len + '</div>\n' +
                    '               <img src="' + data.images[i] + '" style="width:100%">\n' +
                    '           </div>');
            }
            target.append('<a class="prev" onclick="plusSlides(-1)">❮</a>\n' +
                '          <a class="next" onclick="plusSlides(1)">❯</a>');
            var thumb_div = $('<div class="row small-images">');
            len = data.thumb_images.length;
            for (i = 0; i < len; i ++) {
                thumb_div.append('<div class="column">\n' +
                    '                  <img class="demo cursor' + (i ? '' : ' active') + '" src="' + data.thumb_images[i] + '" style="width:100%" onclick="currentSlide(' + (i + 1).toString() + ')">\n' +
                    '              </div>');
            }
            target.append(thumb_div);
        }
    });
})(django.jQuery);