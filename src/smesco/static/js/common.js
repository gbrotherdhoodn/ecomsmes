$(document).ready(function () {

    // if ($("body").find(".scroll-menu").length !== 0) {
    //     if (!$(".scroll-menu > ul > li:first-child, .scroll-menu > ul > li:nth-child(1)").hasClass("active")) {
    //         const scrollMenu = $('.scroll-menu').offset().left + $('.scroll-menu > ul > li.active').outerWidth(true) / 2
    //         $('.scroll-menu').scrollLeft(scrollMenu);
    //     }
    // }

    // if (
    //     window.location.pathname === "/accounts/login/" &&
    //     getParameterByName("register") === "true"
    // ) {
    //     $("#gdn-form-register").css("display", "block");
    //     $("body").addClass("gdn-no-scroll");
    // } else {
    //     $("#gdn-form-register").css("display", "none");
    //     $("body").removeClass("gdn-no-scroll");
    // }
    //
    // function getParameterByName(name, url) {
    //     if (!url) url = window.location.href;
    //     name = name.replace(/[\[\]]/g, "\\$&");
    //     var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
    //         results = regex.exec(url);
    //     if (!results) return null;
    //     if (!results[2]) return "";
    //     return decodeURIComponent(results[2].replace(/\+/g, " "));
    // }

    // $("#frm-search").submit(function () {
    //     if ($("input").val() === "") {
    //         return false;
    //     } else {
    //         return true;
    //     }
    // });
    // $(".DateInput").mask("0000-00-00");
});
let currentYear = new Date().getFullYear();

$(".DateInput").datetimepicker({
    changeMonth: true,
    changeYear: true,
    timepicker: false,
    format: "Y-m-d",
    yearStart: currentYear - 90,
    yearEnd: currentYear - 5,
    startDate: "1987/01/05"
});


$(document).on("click", function (event) {

    // function onEventTargetCloset($class) {
    //     let data = $(event.target).closest($class).length;
    //     return data;
    // }

    // if (
    //     !onEventTargetCloset(".gdn-dropdown-menu-content") &&
    //     !onEventTargetCloset(".gdn-dropdown-menu")
    // ) {
    //     if ($(".gdn-dropdown-menu-content").hasClass("active")) {
    //         $(".gdn-dropdown-menu-content")
    //             .removeClass("active")
    //             .hide();
    //     }
    // }
    //
    // if (
    //     !onEventTargetCloset(".account-menu-mobile.home > ul > li") &&
    //     !onEventTargetCloset("a.open-account-mobile.home") && $('.account-menu-mobile.home').hasClass('active')
    // ) {
    //     event.preventDefault();
    //     const sortElement = $(".account-menu-mobile.home");
    //     const sortElementUl = $(".account-menu-mobile.home > ul");
    //     $('body').removeClass("overflow-no-scroll");
    //     sortElementUl.css({'opacity': 0, 'bottom': '0'}).animate({'opacity': '1', 'bottom': "-50%"}, 100);
    //     sortElement.removeClass("active");
    //     sortElement.hide()
    // }
    // if (
    //     !onEventTargetCloset(".account-menu-mobile.un-home > ul > li") &&
    //     !onEventTargetCloset("a.open-account-mobile.un-home") && $('.account-menu-mobile.un-home').hasClass('active')
    // ) {
    //     event.preventDefault();
    //     const sortElement = $(".account-menu-mobile.un-home");
    //     const sortElementUl = $(".account-menu-mobile.un-home > ul");
    //     $('body').addClass("overflow-no-scroll");
    //     sortElementUl.css({'opacity': 0, 'bottom': '0'}).animate({'opacity': '1', 'bottom': "-50%"}, 100);
    //     sortElement.removeClass("active");
    //     sortElement.hide()
    // }
    //
    // if (
    //     !onEventTargetCloset(".gdn-modal-content") &&
    //     !onEventTargetCloset(".open-modal")
    // ) {
    //     if ($(".gdn-modal").hasClass("open")) {
    //         $(".gdn-modal")
    //             .removeClass("open")
    //             .hide();
    //         $('body').removeClass("overflow-no-scroll")
    //     }
    // }
});

const lengthCategoryList = $('.gdn-category-list.parent-category > ul > li').length;
const sideCategory = $('.side_categories > dl');
sideCategory.each(function (index, element) {
    if ($(element).find("dd").length > 4) {
        if ($(window).width() > 760) {
            $(element).find("dd").slice(4, $(element).find("dd").length).hide();
            $(element).find(".all-read-more-button-category.show-category").show();
        }
    }
});

$(".all-read-more-button-category.show-category").click(function (e) {
    e.preventDefault();
    $(this).hide();
    $(this).parent().find("dd").show();
    $(this).siblings('.hide-category').show()
});

$(".all-read-more-button-category.hide-category").click(function (e) {
    e.preventDefault();
    const lengthElement = $(this).parent().find("dd").length;
    $(this).hide();
    $(this).parent().find("dd").slice(4, lengthElement).hide();
    $(this).siblings('.show-category').show();
});

if (lengthCategoryList > 4) {
    if ($(window).width() > 760) {
        $('.gdn-category-list.parent-category > ul > li').slice(4, lengthCategoryList).hide();
        $(".read-more-button-category.show-category").show();
        $(".read-more-button-category.hide-category").hide()
    }
}

$(".read-more-button-category").click(function (e) {
    e.preventDefault();
    if ($(this).data('name') === "show") {
        $(this).hide();
        $('.gdn-category-list.parent-category > ul > li').slice(4, lengthCategoryList).show();
        $(".read-more-button-category.hide-category").show()

    } else {
        $(this).hide();
        $('.gdn-category-list.parent-category > ul > li').slice(4, lengthCategoryList).hide();
        $(".read-more-button-category.show-category").show()

    }
});

// $(".open-modal").click(function (e) {
//     e.preventDefault();
//     const idContent = "#" + $(this).data("modal");
//     const bodyContent = $(this).data("content");
//     const href = $(this).data("href");
//     const action = $(this).data("action") || false;
//     let gdnModal = $(".gdn-modal");
//     let bodyModal = $(idContent + " .gdn-modal-body");
//     let formModal = $(idContent + " .gdn-modal-form") || false;
//     if (gdnModal.hasClass("open")) {
//         $('body').removeClass("overflow-no-scroll")
//         gdnModal.removeClass("open");
//         $(idContent).hide();
//         if (bodyContent) {
//             bodyModal.empty();
//         }
//         if (action) {
//             formModal.attr("action", "");
//             $(".modal-href").attr("href", "");
//         }
//     } else {
//         $('body').addClass("overflow-no-scroll");
//         gdnModal.addClass("open");
//         $(idContent).show();
//         if (bodyContent) {
//             bodyModal.text(bodyContent);
//         }
//         if (action) {
//             formModal.attr("action", action);
//         }
//         if (href) {
//             $(".modal-href-link").attr("href", href);
//             $(".modal-href").attr("onclick", `deleteWishlist("${href}")`);
//         }
//     }
// });
$(".open-modal").click(function (e) {
    e.preventDefault();
    const idContent = "#" + $(this).data("modal");
    const bodyContent = $(this).data("content");
    const idOpen = $(this).data("open") || false;
    const href = $(this).data("href");
    const action = $(this).data("action") || false;
    let gdnModal = $(".gdn-modal");
    let bodyModal = $(idContent + " .gdn-modal-body");
    let formModal = $(idContent + " .gdn-modal-form") || false;
    if (gdnModal.hasClass("open")) {
        $('body').removeClass("overflow-no-scroll");
        gdnModal.removeClass("open");
        $(idContent).hide();
        if (bodyContent) {
            bodyModal.empty();
        }
        if (action) {
            formModal.attr("action", "");
            $(".modal-href").attr("href", "");
        }
        if (idOpen) {
            $('body').addClass("overflow-no-scroll");
            $("#" + idOpen).css("z-index", 35).addClass("open");
            $("#" + idOpen).show();
            // if (bodyContent) {
            //     bodyModal.text(bodyContent);
            // }
        }
    } else {
        $('body').addClass("overflow-no-scroll");
        gdnModal.addClass("open");
        $(idContent).show();
        if (bodyContent) {
            bodyModal.text(bodyContent);
        }
        if (action) {
            formModal.attr("action", action);
        }
        if (href) {
            $(".modal-href-link").attr("href", href);
            $(".modal-href").attr("onclick", `deleteWishlist("${href}")`);
        }
    }
});

// $(".gdn-dropdown-menu").click(function (e) {
//     e.preventDefault();
//     const idContent = "#" + $(this).data("id");
//     if ($(".gdn-dropdown-menu-content").hasClass("active")) {
//         $(".gdn-dropdown-menu-content").removeClass("active");
//         $(idContent).hide();
//     } else {
//         $(".gdn-dropdown-menu-content").addClass("active");
//         $(idContent).show();
//     }
// });

$(".gdn-tab>ul>li>a").click(function (e) {
    e.preventDefault();
    const tabClass = $("#" + $(this).data("id"));
    const elementContent = $(".desc-tab-content")
    $(".gdn-tab>ul>li>a").removeClass("active");

    $(this).addClass("active");
    $(".gdn-tab-content>.desc").removeClass("active");
    elementContent.animate({height: 100}, 200);
    elementContent.removeClass("active");
    $(".tab-read-more").text("Selengkapnya...");
    tabClass.addClass("active");
    if (tabClass.height() >= 128) {
        tabClass.children(".desc-tab-content").css({height: "100px"});
    } else {
        tabClass.children(".gdn-tab-read-more").hide()
    }
});
if ($(window).width() < 760) {
    $(".gdn-category-header").click(function (e) {
        e.preventDefault();
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
            $(".gdn-category-list").hide();
        } else {
            $(this).addClass('active');
            $(".gdn-category-list").show();
        }
    });
    $(".side_categories dl > dt.nav-header ").click(function (e) {
        e.preventDefault();
        if ($(this).parent().hasClass('active')) {
            $(this).parent().removeClass('active');
            $(this).parent().find('*').hide();
            $("dt.nav-header, dt.nav-header > span, dt.nav-header > i").show();
        } else {
            $(this).parent().addClass('active');
            $(this).parent().find('*').show();
            $("button.all-read-more-button-category").hide();
        }

    })
}

$("ul.accordian>li a.gdn-text-subtitle").click(function (e) {
    e.preventDefault();
    if ($(window).width() <= 760) {
        if (!$(this).hasClass("bank")) {
            if (
                $(this)
                    .siblings()
                    .hasClass("active")
            ) {
                $(".gdn-text-subtitle").removeClass("active");
                $(this)
                    .siblings()
                    .removeClass("active")
                    .slideUp(100);
            } else {
                $(".gdn-text-subtitle").removeClass("active");
                $(".gdn-footer-bottom-child")
                    .removeClass("active")
                    .slideUp(100);
                $(this).addClass("active");
                $(this)
                    .siblings()
                    .addClass("active")
                    .slideDown(100);
            }
        } else {
            const idCheck = "#" + $(this).data("id");
            if (
                $(this)
                    .siblings()
                    .hasClass("active")
            ) {
                $(".gdn-text-subtitle").removeClass("active");
                $(idCheck)
                    .removeClass("active")
                    .slideUp(100);
                $(this)
                    .siblings()
                    .removeClass("active")
                    .slideUp(100);
            } else {
                $(".gdn-text-subtitle").removeClass("active");
                $(this).addClass("active");
                $(".gdn-footer-bottom-child")
                    .removeClass("active")
                    .slideUp(100);
                $(idCheck)
                    .addClass("active")
                    .slideDown(100);
            }
        }
    }
});

$(".on-show-hide-password").click(function (e) {
    e.preventDefault();
    const element = "#" + $(this).data("id") || false;
    if ($(this).hasClass("fa-eye-slash")) {
        $(element).attr("type", "text");
        $(this)
            .removeClass("fa-eye-slash")
            .addClass("fa-eye");
    } else {
        $(element).attr("type", "password");
        $(this)
            .removeClass("fa-eye")
            .addClass("fa-eye-slash");
    }
});

$(".gdn-show-hide").click(function (e) {
    e.preventDefault();
    const show = "#" + $(this).data("show") || false;
    const hide = "#" + $(this).data("hide") || false;
    const jqueryElement = $(show);
    if (show && hide) {
        $(show).show();
        $(hide).hide();
    } else {
        if (jqueryElement.hasClass("active")) {
            jqueryElement.removeClass("active");
            jqueryElement.hide();
        } else {
            jqueryElement.addClass("active");
            jqueryElement.show();
        }
    }
});

$(".search-button").on("click", function () {
    let elementRemove = false;
    if ($(this).data("clear")) {
        elementRemove = "." + $(this).data("clear");
    }
    const close = $(".search-button > i.fa-close");
    const minify = $(".search-button > i.fa-search");
    if (close.hasClass("active")) {
        if (elementRemove) {
            $(elementRemove).val("");
            const childrenClose = $(this).children("i.fa-close");
            const childrenMinify = $(this).children("i.fa-search");
            childrenMinify.show();
            childrenClose.hide();
            childrenMinify.addClass("active");
            childrenClose.removeClass("active");
        } else {
            $(".form-search-input").val("");
            minify.show();
            close.hide();
            minify.addClass("active");
            close.removeClass("active");
        }
    }
});

$('.scroll-to-top').on("click", function (e) {
    e.preventDefault();
    $('html,body').animate({scrollTop: 0}, 0);
});

// $(".gdn-type-input").on('keyup', function () {
//     const my_txt = $(this).val();
//     const type = $(this).data("type");
//     switch (type) {
//         case "length":
//             const len = my_txt.length;
//             const action = "." + $(this).data("action");
//             const change = "." + $(this).data("change");
//             if (len > 3) {
//                 $(action).show();
//                 $(action).addClass('active');
//                 $(change).removeClass('active');
//                 $(change).hide();
//             } else {
//                 $(action).hide();
//                 $(action).removeClass('active');
//                 $(change).addClass('active');
//                 $(change).show();
//             }
//             break;
//         default:
//             break;
//     }
// });

$("a.open-filter-mobile").click(function (e) {
    e.preventDefault();
    const sortElement = $(".gdn-product-list-left");
    const sortElementUl = $(".gdn-product-list-left > ul");
    $('body').addClass("overflow-no-scroll");
    sortElement.show();
    sortElement.addClass("active");
    sortElementUl.css({'opacity': 0, 'top': '50%'}).animate({'opacity': '1', 'top': 0}, 100);
});

$(".close-filter-mobile").click(function (e) {
    e.preventDefault();
    const sortElement = $(".gdn-product-list-left");
    const sortElementUl = $(".gdn-product-list-left > ul");
    sortElement.hide()
    $('body').removeClass("overflow-no-scroll")
    sortElement.removeClass("active")
    sortElementUl.css({'opacity': 0, 'top': 0}).animate({'opacity': '1', 'top': "50%"}, 100);
});

$("a.open-account-mobile").click(function (e) {
    e.preventDefault();
    if (!$('.account-menu-mobile.home').hasClass('active')) {
        const sortElement = $(".account-menu-mobile.home");
        const sortElementUl = $(".account-menu-mobile.home > ul");
        sortElement.show()
        $('body').addClass("overflow-no-scroll");
        sortElement.addClass("active");
        sortElementUl.css({'opacity': 0, 'bottom': '-50%'}).animate({'opacity': '1', 'bottom': "0"}, 100);
    } else {
        const sortElement = $(".account-menu-mobile.home");
        const sortElementUl = $(".account-menu-mobile.home > ul");
        $('body').removeClass("overflow-no-scroll");
        sortElementUl.css({'opacity': 0, 'bottom': '0'}).animate({'opacity': '1', 'bottom': "-50%"}, 100);
        sortElement.removeClass("active");
        sortElement.hide()
    }
});
$("a.open-account-mobile.un-home").click(function (e) {
    e.preventDefault();
    if (!$('.account-menu-mobile.un-home').hasClass('active')) {
        const sortElement = $(".account-menu-mobile.un-home");
        const sortElementUl = $(".account-menu-mobile.un-home > ul");
        sortElement.show()
        $('body').addClass("overflow-no-scroll");
        sortElement.addClass("active");
        sortElementUl.css({'opacity': 0, 'bottom': '-50%'}).animate({'opacity': '1', 'bottom': "0"}, 100);
    } else {
        const sortElement = $(".account-menu-mobile.un-home");
        const sortElementUl = $(".account-menu-mobile.un-home > ul");
        $('body').addClass("overflow-no-scroll");
        sortElementUl.css({'opacity': 0, 'bottom': '0'}).animate({'opacity': '1', 'bottom': "-50%"}, 100);
        sortElement.removeClass("active");
        sortElement.hide()
    }
});

$("a.open-sort-mobile").click(function (e) {
    e.preventDefault();
    const sortElement = $(".sort-product-list-mobile");
    const sortElementUl = $(".sort-product-list-mobile > ul");
    sortElement.show()
    $('body').addClass("overflow-no-scroll");
    sortElement.addClass("active");
    sortElementUl.css({'opacity': 0, 'bottom': '-50%'}).animate({'opacity': '1', 'bottom': 0}, 100);

});

$(".sort-product-list-mobile").click(function (e) {
    const elementDetect = event.target.nodeName;
    if (elementDetect === "A" || elementDetect === "SPAN") {

    } else {
        e.preventDefault();
        const sortElement = $(".sort-product-list-mobile");
        const sortElementUl = $(".sort-product-list-mobile > ul");
        sortElement.removeClass("active");
        sortElement.hide();
        $('body').removeClass("overflow-no-scroll")
        sortElementUl.css({'opacity': 1, 'bottom': 0}).animate({'opacity': '0', 'bottom': "-50%"}, 100);
    }
});


$(".gdn-accordian label.gdn-accordian-btn, .gdn-accordian a.gdn-accordian-btn").click(function (e) {
    e.preventDefault();
    const content = "." + $(this).data("content");
    const inputStatus = $(this).data("input") || false;

    if ($(this).hasClass("active")) {
        $(this).removeClass("active");
        $(".gdn-accordian a.gdn-accordian-btn, .gdn-accordian label.gdn-accordian-btn").removeClass("active");
        $(content).removeClass("active");
        if (inputStatus === true) {
            $(".check-accordian").prop('checked', false);
            $("input.check-accordian").prop('checked', false);
            $('button#place-order[type="submit"]').prop('disabled', true);
            $("select.method-payment-chooose").prop('disabled', true);
            if ($(this).attr('id') !== "credit-card") {
                $(this).siblings().find("select.method-payment-chooose").val("");
            }
        }
        $(this)
            .siblings()
            .removeClass("active")
            .slideUp(200);
    } else {
        $('button#place-order[type="submit"]').prop('disabled', true);
        $(".gdn-accordian a.gdn-accordian-btn, .gdn-accordian label.gdn-accordian-btn").removeClass("active");
        if (inputStatus === true) {
            if ($(this).attr('id') !== "credit-card") {
                $(this).siblings().find("select.method-payment-chooose").val("");
            }
            if ($(this).attr('id') === "credit-card") {
                $('button#place-order[type="submit"]').prop('disabled', false);
            }
            $(".check-accordian").prop('checked', false);
            $("select.method-payment-chooose").prop('disabled', true);
            $(this).siblings().find("select.method-payment-chooose").prop('disabled', false);
            $(this).children("input").prop('checked', true);
        }
        $(this).addClass("active");
        $(content)
            .removeClass("active")
            .slideUp(100);
        $(this)
            .siblings()
            .addClass("active")
            .slideDown(200);
    }
});
$(".gdn-category-accordian i.fa").click(function (e) {
    e.preventDefault();
    if (
        $(this)
            .parents()
            .closest("li")
            .hasClass("active-category")
    ) {
        if (
            $(this)
                .parents()
                .closest("li")
                .find("ul")
                .hasClass("gdn-category-list-sub")
        ) {
            if (
                $(this)
                    .parent()
                    .parent()
                    .hasClass("active-category")
            ) {
                $(this)
                    .parent()
                    .parent()
                    .removeClass("active-category");
            } else {
                $(".gdn-category-list-sub > li.active-category").removeClass(
                    "active-category"
                );
                $(this)
                    .parent()
                    .parent()
                    .addClass("active-category");
            }
        } else {
            $(this)
                .parents()
                .closest("li")
                .removeClass("active-category");
            $(".gdn-category-list-sub > li").removeClass("active-category");
        }
    } else {
        $(".gdn-category-accordian li").removeClass("active-category");
        $(this)
            .parents()
            .closest("li")
            .addClass("active-category");
    }
});

var updateQueryStringParam = function (key, value) {
    var baseUrl = [
            location.protocol,
            "//",
            location.host,
            location.pathname
        ].join(""),
        urlQueryString = document.location.search,
        newParam = key + "=" + value,
        params = "?" + newParam;
    // If the "search" string exists, then build params from it
    if (urlQueryString) {
        var updateRegex = new RegExp("([?&])" + key + "[^&]*");
        if (urlQueryString.match(updateRegex) !== null) {
            // If param exists already, update it
            params = urlQueryString.replace(updateRegex, "$1" + newParam);
        }
    }
    // no parameter was set so we don't need the question mark
    params = params === "?" ? "" : params;
    window.history.pushState({}, "", baseUrl + params);
    location.reload();
};
$(".selvar").on("click", function () {
    var paramkey = $(this).data("attr_type"),
        paramval = $(this).data("attr_val");
    $(this).attr("disabled", "true");
    updateQueryStringParam(paramkey, paramval);
});
$('#add-my-review').on('click', function () {
    $('#add_review_form').show();
    $(this).hide();
    $('#parent-add-review').hide();
    $('#addreview').focus();
});
$('#cancel-review').on('click', function () {
    $('#add_review_form').hide();
    $('#parent-add-review, #add-my-review').show();
});

var parser = document.createElement('a');
parser.href = window.location.href;
if (parser.hash && parser.hash === "#open-review") {

    $('#add_review_form').show();
    $('html, body').animate({
        scrollTop: $("#add_review_form").offset().top - 150
    }, 1000);
    $(this).hide();
    $('#parent-add-review').hide();
    $('#addreview').focus();
}


function deleteWishlist(url) {
    $.ajaxSetup({
        data: {csrfmiddlewaretoken: '{{ csrf_token }}'},
    });

    $.ajax({
        url: url, // the endpoint
        type: "GET", // http method
        // handle a successful response
        success: function (json) {
            console.log(json); // log the returned json to the console

            if (json.status == "success") {
                // {#                  console.log('mantep')#}
                location.reload();
            } else {
                // {#                  console.log('gagal')#}
            }
        },

        // handle a non-successful response
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    }); // end of ajax
}

$("#click-append").on("click", function (event) {
    event.preventDefault();
    let text = $("#voucher-input").val();
    if (text && text.length > 1) {
        $("input#id_code").val(text);
        $('button#click-append[type="button"]').prop('disabled', true);
        $("#voucher_form").submit()
    }
});

$(".remove-voucher").on("click", function (e) {
    e.preventDefault()
    if ($(this).data('action')) {
        $("form#form-delete-voucher").attr("action", $(this).data('action'));
        $("form#form-delete-voucher").submit()
    }
    console.log($(this).data('action'));
    console.log("masuk sini")
});
$("#voucher-input").keyup(function (e) {
    if ($(event.target).val().length > 1) {
        $('button#click-append').prop('disabled', false);
        let code = e.which;
        if (code == 13) {
            e.preventDefault();
            let text = $("#voucher-input").val();
            if (text && text.length > 1) {
                $("input#id_code").val(text);
                $('button#click-append[type="button"]').prop('disabled', true);
                $("#voucher_form").submit()
            }
        }
    }

});


$(".btn-nav-static").on('click', function (e) {
    console.log()
    const element = "#" + $(this).data("dropdown")
    console.log(element)
    if ($(element).hasClass("active")) {
        $(element).hide().removeClass("active")

    } else {
        $(element).show().addClass("active")

    }

});
