/*global jQuery */

var oscar = (function (o, $) {
    // Replicate Django's flash messages so they can be used by AJAX callbacks.
    o.messages = {
        addMessage: function (tag, msg) {
            var msgHTML =
                '<div class="alert fade in alert-' +
                tag +
                '">' +
                '<a href="#" class="close" data-dismiss="alert">&times;</a>' +
                msg +
                "</div>";
            $("#messages").append($(msgHTML));

        },
        debug: function (msg) {
            o.messages.addMessage("debug", msg);
        },
        info: function (msg) {
            o.messages.addMessage("info", msg);
        },
        success: function (msg) {
            o.messages.addMessage("success", msg);
        },
        warning: function (msg) {
            o.messages.addMessage("warning", msg);
        },
        error: function (msg) {
            o.messages.addMessage("danger", msg);
        },
        clear: function () {
            $("#messages").html("");
        },
        scrollTo: function () {
            $("html").animate({scrollTop: $("#messages").offset().top});
        }
    };

    o.addressEvent = {
        init: function (address_data) {

            $(document).ready(function () {
                o.addressEvent.load_address(address_data)
            });
            $(".add-address").click(function () {
                o.addressEvent.load_address(address_data)
            });

        },
        load_address: function (address_data) {
            let {state, district, subDistrict, village, postCode, primaryKey} = address_data;
            let regency = '#id_regency_district' + primaryKey;
            let subdistrict = '#id_subdistrict' + primaryKey;
            let vilage = '#id_village' + primaryKey;
            let province = '#id_province' + primaryKey;
            let country = '#id_country' + primaryKey;
            let postcode = '#id_postcode' + primaryKey;
            let ajaxRequest = function (type, url, param, element) {
                $.ajax({
                    url: url,
                    data: {'param': param},
                    success: function (data) {
                        responseEvent(type, data, element)
                    }
                })
            };

            let responseEvent = function (type, data, element) {
                if (type !== 'postcode') {
                    $(element).html(data).prop('disabled', false);
                } else {
                    $(`${postcode}`).val(data);
                }
            };
            const default_value_option = "<option value=''>---------</option>";
            if (!primaryKey) {
                $(`${regency}, ${subdistrict}, ${vilage}`).prop('disabled', true);
            }

            $(`${province}, ${regency}, ${subdistrict}, ${vilage}`).select2({width: 'resolve'});
            $('.select2').css('font-size', '18px');
            $('.select2 > .selection').css('width', '100%');
            $('.select2-container--default .select2-selection--single').css("border-radius", "0");
            $('.select2-selection__rendered').css('color', '#828282');
            $('.select2-selection__arrow').css('top', '5px');
            $('.select2-selection').css('height', '40px').css('padding-top', '5px').css('border', 'solid 1px #828282');
            $(`${postcode}`).prop('readonly', true);
            if (!primaryKey) {
                ajaxRequest("province", state, $(`${country}`).val(), `${province}`);
            }

            $(`${province}`).change(function () {
                $(`${regency}, ${subdistrict}, ${vilage}`).html(default_value_option).prop('disabled', true);
                $(`${postcode}`).val("");
                ajaxRequest("district", district, $(`${province}`).val(), `${regency}`);
            });

            $(`${regency}`).change(function () {
                $(`${subdistrict}, ${vilage}`).html(default_value_option).prop('disabled', true);
                $(`${postcode}`).val("");
                ajaxRequest("subdistrict", subDistrict, $(`${regency}`).val(), `${subdistrict}`);
            });

            $(`${subdistrict}`).change(function () {
                $(`${vilage}`).html(default_value_option).prop('disabled', true);
                $(`${postcode}`).val("");
                ajaxRequest("village", village, $(`${subdistrict}`).val(), `${vilage}`);
            });

            $(`${vilage}`).change(function () {
                $(`${postcode}`).val("");
                ajaxRequest("postcode", postCode, $(`${vilage}`).val(), `${postcode}`);
            });
        }
    };
    o.search = {
        init: function (price_search_data) {
            o.search.initSortWidget();
            o.search.initFacetWidgets();
            o.search.initFacetPriceWidgets(price_search_data);
        },
        initSortWidget: function () {
            // Auto-submit (hidden) search form when selecting a new sort-by option
            $("#id_sort_by").on("change", function () {
                sort_product($(this).val());
                // $(this)
                //         .closest("form")
                //         .submit();
            });

            $('.sort_by_mobile').on('click', function () {
                sort_product($(this).data('value-choice'));
            });

            var sort_product = function (new_value) {

                var current_url = window.location.href,
                    newVal = new_value,
                    qd = o.search.urlParamToArray(),
                    base_url_part = 'sort_by=';

                if ('sort_by' in qd) {
                    new_url = current_url.replace(base_url_part + qd['sort_by'][0], base_url_part + newVal);
                    $(location).attr('href', new_url);
                } else if (!('sort_by' in qd) && (('selected_facets' in qd) || ('q' in qd) || 'page' in qd)) {
                    current_url += '&' + base_url_part + newVal;
                    $(location).attr('href', current_url);
                } else {
                    current_url += '?' + base_url_part + newVal;
                    $(location).attr('href', current_url);
                }
            }
        },
        urlParamToArray: function () {
            var qd = {};
            if (location.search) location.search.substr(1).split("&").forEach(function (item) {
                var s = item.split("="),
                    k = s[0],
                    v = s[1] && decodeURIComponent(s[1]); //  null-coalescing / short-circuit
                //(k in qd) ? qd[k].push(v) : qd[k] = [v]
                (qd[k] = qd[k] || []).push(v) // null-coalescing / short-circuit
            });

            return qd;
        },
        initFacetWidgets: function () {
            // Bind events to facet checkboxes
            $(".facet_checkbox").on("change", function () {
                window.location.href = $(this)
                    .nextAll(".facet_url")
                    .val();
            });
        },
        initFacetPriceWidgets: function (price_search_data) {
            var {min_category_price, max_category_price, dynamic_query_fields} = price_search_data,
                current_url = window.location.href,
                min_filtered_price = 0,
                max_filtered_price = 0,
                min_val_input = $('input.sliderValue[data-index="0"]'),
                max_val_input = $('input.sliderValue[data-index="1"]'),
                slider = $('#slider');
            $(document).ready(function () {
                var valMax = max_val_input.val().replace(/\./g, '');
                var valMin = min_val_input.val().replace(/\./g, '');
                if (valMax && valMin) {
                    $(".button-filter-price > button").hide();
                    $(".button-filter-price > a").show();
                    $(".button-filter-price > a").removeClass("hidden");
                } else {
                    $(".button-filter-price > button").show();
                    $(".button-filter-price > a").hide();
                }

                max_val_input.val(numberWithCommas(valMax));
                min_val_input.val(numberWithCommas(valMin));

            });


            min_val_input.keyup(function (e) {
                e.preventDefault();
                let getOnlyNumber = $(this).val().replace(/[^0-9\.]+/g, '');
                let maxVal = Number(max_val_input.val().replace(/\./g, ''));
                getOnlyNumber = getOnlyNumber.replace(/\./g, '');
                if (maxVal > Number(getOnlyNumber) && maxVal && Number(getOnlyNumber)) {
                    $(".button-filter-price > button").hide();
                    $(".button-filter-price > a").show();
                    $(".button-filter-price > a").removeClass("hidden");

                } else {
                    $(".button-filter-price > button").show();
                    $(".button-filter-price > a").hide();
                }
                $(this).val(numberWithCommas(getOnlyNumber));
            });
            max_val_input.keyup(function (e) {
                e.preventDefault();
                let getOnlyNumber = $(this).val().replace(/[^0-9\.]+/g, '');
                let minVal = Number(min_val_input.val().replace(/\./g, ''));
                getOnlyNumber = getOnlyNumber.replace(/\./g, '');
                if (minVal < Number(getOnlyNumber) && minVal) {
                    $(".button-filter-price > button").hide();
                    $(".button-filter-price > a").show();
                    $(".button-filter-price > a").removeClass("hidden");

                } else {
                    $(".button-filter-price > button").show();
                    $(".button-filter-price > a").hide();
                }
                $(this).val(numberWithCommas(getOnlyNumber));
            });

            function numberWithCommas(x) {
                x = x.replace(/\./g, '');
                x = x === "" ? x : parseInt(x);
                return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
            }

            function handleUrl(use_globals_filtered_prices) {

                var qd = o.search.urlParamToArray(),
                    sort_after = (qd['sort_by'] && !(current_url.indexOf('/?sort_by') !== -1)) ? '&sort_by=' + qd['sort_by'] : '',
                    category_url = qd['q'] ? current_url.split('/?q')[0] :
                        ((current_url.indexOf('/?sort_by') !== -1) ? current_url.split('/?sort_by')[0] : current_url.split('/?selected_facets')[0]),
                    base_url_part = 'selected_facets=',
                    rebuilt_url = qd['q'] || (current_url.indexOf('/?sort_by') !== -1) ? '&' : '?';

                var facets = qd['selected_facets'],
                    price_changed = false;

                for (var i in facets) {
                    var kv = facets[i],
                        k = kv.split(':')[0],  // price_exact
                        v = kv.split(':')[1];  // [8732+TO+54432]

                    if (dynamic_query_fields.indexOf(k) >= 0) {

                        // Replace existing price range in URL. Used when price range is changed
                        if (use_globals_filtered_prices) {
                            kv = k + ':' + '[' + min_filtered_price + '+TO+' + max_filtered_price + ']';
                            price_changed = true;
                        } else {
                            min_filtered_price = v.substring(v.lastIndexOf("[") + 1, v.lastIndexOf("+TO"));
                            max_filtered_price = v.substring(v.lastIndexOf("+TO+") + 4, v.lastIndexOf("]"));

                            min_val_input.val(min_filtered_price);
                            max_val_input.val(max_filtered_price);

                            // 0 and 1 are field indexes
                            slider.slider("values", 0, min_filtered_price);
                            slider.slider("values", 1, max_filtered_price);
                        }
                    }

                    rebuilt_url += base_url_part + kv + '&';
                }

                // When we set price range at the first time, i.e when there is no previous version of price range facet.
                if (use_globals_filtered_prices && !price_changed) {
                    kv = base_url_part + 'price_exact' + ':' + '[' + min_filtered_price + '+TO+' + max_filtered_price + ']';
                    rebuilt_url += kv;
                }

                if (rebuilt_url.slice(-1) === '&') {
                    rebuilt_url = rebuilt_url.slice(0, -1);
                }

                // If facets not selected
                if (rebuilt_url !== '?') {
                    var base_search = qd['q'] ? '/?q=' + qd['q'] :
                        ((current_url.indexOf('/?sort_by') !== -1) ? '/?sort_by=' + qd['sort_by'] : '');
                    var full_url = category_url + base_search + encodeURI(rebuilt_url).replace(/:\s*/g, "%3A") + sort_after;
                    $("#submit_price").attr("href", full_url);
                }
            }

            // SLIDER
            slider.slider({
                min: min_category_price,
                max: max_category_price,
                step: 100,
                range: true,
                values: [min_category_price, max_category_price],

                // After sliders are moved, change Input Field Values
                slide: function (event, ui) {
                    for (var i = 0; i < ui.values.length; ++i) {
                        $("input.sliderValue[data-index=" + i + "]").val(ui.values[i]);

                        if (i === 0) {
                            min_filtered_price = ui.values[i];
                        } else {
                            max_filtered_price = ui.values[i]
                        }

                        handleUrl(true);
                    }
                }
            });

            // INPUT FIELDS
            $("input.sliderValue").keyup(function () {

                var $this = $(this),
                    changed_field = $this.data("index"),
                    changed_price = $this.val().replace(/\./g, '');

                slider.slider("values", changed_field, changed_price);

                if (changed_field === 0) {
                    min_filtered_price = changed_price;

                    //Fix "0" max range URL price when just min range is changed
                    if (max_filtered_price === 0) {
                        max_filtered_price = max_category_price;
                    }

                } else {
                    //Fix "0" min range URL price when just max range is changed
                    if (min_filtered_price === 0) {
                        min_filtered_price = min_category_price;
                    }

                    max_filtered_price = changed_price;
                }

                handleUrl(true);
            });

            // # Executes once the page is loaded
            handleUrl(false);
        }
    };

    // This block may need removing after reworking of promotions app
    o.promotions = {
        init: function () {
        }
    };

    // Notifications inbox within 'my account' section.
    o.notifications = {
        init: function () {
            $('a[data-behaviours~="archive"]').click(function () {
                o.notifications.checkAndSubmit($(this), "archive");
            });
            $('a[data-behaviours~="delete"]').click(function () {
                o.notifications.checkAndSubmit($(this), "delete");
            });
        },
        checkAndSubmit: function ($ele, btn_val) {
            $ele.closest("tr")
                .find("input")
                .attr("checked", "checked");
            $ele.closest("form")
                .find('button[value="' + btn_val + '"]')
                .click();
            return false;
        }
    };

    // Site-wide forms events
    o.forms = {
        init: function () {
            // Forms with this behaviour are 'locked' once they are submitted to
            // prevent multiple submissions
            $('form[data-behaviours~="lock"]').submit(
                o.forms.submitIfNotLocked
            );

            // Disable buttons when they are clicked and show a "loading" message taken from the
            // data-loading-text attribute (http://getbootstrap.com/2.3.2/javascript.html#buttons).
            // Do not disable if button is inside a form with invalid fields.
            // This uses a delegated event so that it keeps working for forms that are reloaded
            // via AJAX: https://api.jquery.com/on/#direct-and-delegated-events
            $(document.body).on("submit", "form", function () {
                var form = $(this);
                if ($(":invalid", form).length == 0) {
                    $(this)
                        .find("button[data-loading-text]")
                        .button("loading");
                    if (
                        $(this)
                            .find("button[data-loading-love]")
                            .hasClass("love")
                    ) {
                        form.children(".love")
                            .children()
                            .removeClass("fa-heart-o");
                        form.children(".love")
                            .children()
                            .addClass("fa-heart animation-love");
                    }
                }
            });
            // stuff for star rating on review page
            // show clickable stars instead of a select dropdown for product rating
            var ratings = $(".reviewrating");
            if (ratings.length) {
                ratings
                    .find(".star-rating i")
                    .on("click", o.forms.reviewRatingClick);
            }
        },
        submitIfNotLocked: function () {
            var $form = $(this);
            if ($form.data("locked")) {
                return false;
            }
            $form.data("locked", true);
        },
        reviewRatingClick: function () {

            $("#id_score").closest('.form-group').removeClass('has-error');
            $("#id_score-error").remove();
            var ratings = ["One", "Two", "Three", "Four", "Five"]; //possible classes for display state
            $(this)
                .parent()
                .removeClass("One Two Three Four Five")
                .addClass(ratings[$(this).index()]);
            $(this)
                .closest(".controls")
                .find("select")
                .val($(this).index() + 1); //select is hidden, set value
        }
    };

    o.page = {
        init: function () {
            // Scroll to sections
            $(".top_page a").click(function (e) {
                var href = $(this).attr("href");
                $("html, body").animate(
                    {
                        scrollTop: $(href).offset().top
                    },
                    500
                );
                e.preventDefault();
            });
            // Tooltips
            $('[rel="tooltip"]').tooltip();
        }
    };
    o.love = {
        init: function (options) {
            const {url, token} = options
            $.ajaxSetup({
                data: {
                    csrfmiddlewaretoken: token
                },
            });

            $(".heart").on("click", function () {
                $(this).toggleClass("is-active");
                $.ajax({
                    url: url, // the endpoint
                    type: "GET", // http method
                    // handle a successful response
                    success: function (json) {
                        if (json.status == "success") {

                        } else {

                        }
                    },

                    // handle a non-successful response
                    error: function (xhr, errmsg, err) {
                    }
                }); // end of ajax
            });
        }
    }
    o.review = {
        init: function (options) {
            o.review.reviewFirst(options)
            o.review.onValidation()
            o.review.onOpenForm()
        },
        onOpenForm: function () {
            $(".add-review").on('click', function (e) {
                e.preventDefault();
                $("#add-review").show()
                $("#list-review").hide()
            })
            $(".cancel-review").on('click', function (e) {
                e.preventDefault();
                $("#add-review").hide()
                $("#list-review").show()
            })
        },
        onValidation: function () {
            // add the rule here
            $.validator.addMethod("notEqualTo", function (value, element, param) {
                return value !== "0";
            }, 'this Field is Required');
            $('button#review-button').on('click', function (e) {
                e.preventDefault();
                $("form#add_review_form").valid();
            });
            $.validator.setDefaults({
                success: "valid"
            });

            $("form#add_review_form").validate({
                rules: {
                    score: {
                        required: true,
                        notEqualTo: function () {
                            return $('#id_score').val()
                        }

                    },
                    title: "required",
                    body: {
                        required: true,
                        minlength: 15,
                        maxlength: 250
                    }
                },

                messages: {
                    score: {
                        notEqualTo: "Rating harus di pilih"
                    },
                    title: "Judul tidak boleh kosong",
                    body: "Kolam Komentar Tidak boleh kosong minamal 15 maximal 250",
                },
                // Make sure the form is submitted to the destination defined
                // in the "action" attribute of the form when valid
                highlight: function (element) {
                    $(element).closest('.form-group').addClass('has-error');

                },
                unhighlight: function (element) {
                    $(element).closest('.form-group').removeClass('has-error');
                },
                errorElement: 'span',
                errorClass: 'help-block',
                errorPlacement: function (error, element) {
                    if (element.parent('.input-group').length) {
                        error.insertAfter(element.parent());
                    } else {
                        error.insertAfter(element);
                    }
                },
                submitHandler: function (form) {
                    form.submit();
                }
            });
        },
        reviewFirst: function (options) {
            const {url, token, ratingStar, ratingCalculate} = options;
            $.ajaxSetup({
                data: {
                    csrfmiddlewaretoken: token
                },
            });


            let page = 1
            $('#review_list').html('');
            $.ajax({
                url: url, // the endpoint
                type: "GET", // http method
                data: {
                    "page": page
                },
                // handle a successful response
                success: function (json) {
                    if (json.status == "success") {
                        const star = '<div class="review-star-header review-star review-' + Number(ratingStar.toString().split(",")[0]) + '"><i class="fa fa-star"></i><i class="fa fa-star"></i><i class="fa fa-star"></i><i class="fa fa-star"></i><i class="fa fa-star"></i></div>'
                        $('#review-navbar').html(`
                            <div class="review-header d-block">
                                <div
                                    class="row between-lg between-xs between-sm middle-xs without-margin">
                                    <div class="review-arrow">
                                        <a class=${json.previous_page ? `review-arrow-slide` : `review-arrow-slide-disabled`} onclick=${json.previous_page ? ` (${json.previous_page})` : ``}>
                                            <i class="ion-ios-arrow-back"></i>
                                        </a>
                                    </div>
                                    <div class="col-lg-8">
                                        <div class="row middle-xs center-xs">
                                                                            <span class="text-title-1"
                                                                                  style="margin-right:20px">${ratingCalculate}</span>
                                            ${star}
                                        </div>
                                    </div>
                                    <div class="review-arrow">
                                        <a class=${json.previous_page ? `review-arrow-slide` : `review-arrow-slide-disabled`}
                                                onclick=${json.next ? `load_review_list(${json.next})` : ``}>
                                            <i
                                                class="ion-ios-arrow-forward"></i>
                                        </a>
                                    </div>
                                </div>
                            </div>`);

                        data = JSON.parse(json.data)
                        data.forEach(function (review) {
                            var date = new Date(review.fields.date_created),
                                yr = date.getFullYear(),
                                month = date.getMonth() < 10 ? '0' + (Number(date.getMonth()) + 1) : date.getMonth(),
                                day = date.getDate() < 10 ? '0' + date.getDate() : date.getDate(),
                                newDate = day + '/' + month + '/' + yr;
                            var star = '<div class="review-star review-' + review.fields.score + '"><i class="fa fa-star "></i><i class="fa fa-star "></i><i class="fa fa-star "></i><i class="fa fa-star "></i><i class="fa fa-star "></i></div>';
                            var row = `
                                <article class="review-loop">
                                    <div class="row middle-lg">
                                        <div class="col-lg-4 col-xs-12 col-sm-12">
                                            <div class="review-left">
                                                ${star}
                                            </div>
                                        </div>
                                        <div class="col-lg-8 col-xs-12 col-sm-12">
                                            <div class="row start-sm end-lg start-xs without-margin-left">
                                                <div class="review-name">
                                                    <span
                                                        class="d-block text-body-1 text-grey text-right ellipsis-desktop">
                                                        ${review.fields.name || "Anonymous"}
                                                    </span>
                                                </div>
                                                <div class="review-date">
                                                        <span
                                                            class="d-block text-body-1 text-grey text-right">
                                                        ${newDate}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row with-margin-bottom">
                                            <div class="col-lg-12 col-xs-12 col-sm-12">
                                                <div class="review-content">
                                                    <p class="d-block text-black text-body-1">${review.fields.body}</p>
                                                </div>
                                            </div>
                                        </div>
                                </article>
                                `;
                            $('#review-list-data-list').append(row)
                        })

                    } else {
                    }
                },

                // handle a non-successful response
                error: function (xhr, errmsg, err) {
                    // console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
                }
            }); // end of ajax
        }
    };
    o.responsive = {
        init: function () {
            if (o.responsive.isDesktop()) {
                o.responsive.initNav();
            }
        },
        isDesktop: function () {
            return document.body.clientWidth > 767;
        },
        initNav: function () {
            // Initial navigation for desktop
            var $sidebar = $("aside.col-sm-3"),
                $browse = $('[data-navigation="dropdown-menu"]'),
                $browseOpen = $browse.parent().find("> a[data-toggle]");
            // Set width of nav dropdown to be same as sidebar
            $browse.css("width", $sidebar.outerWidth());
            // Remove click on browse button if menu is currently open
            if (!$browseOpen.length) {
                $browse
                    .parent()
                    .find("> a")
                    .off("click");
                // Set margin top of aside allow space for open navigation
                $sidebar.css({marginTop: $browse.outerHeight()});
            }
        },
        initSlider: function () {
            $(".carousel").carousel({
                interval: 20000
            });
        }
    };

    // IE compabibility hacks
    o.compatibility = {
        init: function () {
            if (!o.compatibility.isIE()) return;
            // Set the width of a select in an overflow hidden container.
            // This is for add-to-basket forms within browing pages
            $(".product_pod select").on({
                mousedown: function () {
                    $(this).addClass("select-open");
                },
                change: function () {
                    $(this).removeClass("select-open");
                }
            });
        },
        isIE: function () {
            return navigator.userAgent.toLowerCase().indexOf("msie") > -1;
        }
    };

    o.basket = {
        is_form_being_submitted: false,
        init: function (options) {
            if (typeof options == "undefined") {
                options = {basketURL: document.URL};
            }
            o.basket.url = options.basketURL || document.URL;
            $("#content_inner").on(
                "click",
                '#basket_formset a[data-behaviours~="remove"]',
                function (event) {
                    o.uiAnimate.loading("show");
                    o.basket.checkAndSubmit($(this), "form", "DELETE");
                    event.preventDefault();
                }
            );
            $("#content_inner").on(
                "click",
                '#basket_formset a[data-behaviours~="save"]',
                function (event) {
                    o.basket.checkAndSubmit($(this), "form", "save_for_later");
                    event.preventDefault();
                }
            );
            $("#content_inner").on(
                "click",
                '#saved_basket_formset a[data-behaviours~="move"]',
                function () {
                    o.basket.checkAndSubmit($(this), "saved", "move_to_basket");
                }
            );
            $("#content_inner").on(
                "click",
                '#saved_basket_formset a[data-behaviours~="remove"]',
                function (event) {
                    o.basket.checkAndSubmit($(this), "saved", "DELETE");
                    event.preventDefault();
                }
            );
            $("#content_inner").on("click", "#voucher_form_link a", function (
                event
            ) {
                o.basket.showVoucherForm();
                event.preventDefault();
            });
            $("#content_inner").on("click", "#voucher_form_cancel", function (
                event
            ) {
                o.basket.hideVoucherForm();
                event.preventDefault();
            });
            $("#content_inner").on(
                "submit",
                "#basket_formset",
                o.basket.submitBasketForm
            );

            $("#content_inner").on("change", ".input-quantity", function (
                event
            ) {
                let element = $(this);
                let value = +element.val();
                let max = +element.attr("max");
                value = value <= 0 ? 1 : value;
                if (value <= max) {
                    o.uiAnimate.loading('show');
                    element.val(value);
                    o.basket.submitBasketForm(event);
                } else {
                    o.uiAnimate.loading('show');
                    element.val(max);
                    o.basket.submitBasketForm(event);
                }
            });

            $("#content_inner").on("click", "button.qty-button", function (
                event
            ) {
                const typeButton = $(this).data("id");
                if (typeButton === "plus") {
                    let max = $(this)
                        .prev()
                        .children()
                        .attr("max");
                    let value = +$(this)
                        .prev()
                        .children()
                        .val();
                    if (value < max) {
                        o.uiAnimate.loading('show');
                        $(this)
                            .prev()
                            .children()
                            .val(value + 1);
                        o.basket.submitBasketForm(event);
                    } else {
                        const elementTooltip = $(this)
                            .parents(".qty-form-parent").children('.gdn-tooltip');
                        o.uiAnimate.tooltip(elementTooltip, 1500)
                    }
                } else {
                    if (
                        $(this)
                            .next()
                            .children()
                            .val() > 1
                    ) {
                        o.uiAnimate.loading('show');
                        $(this)
                            .next()
                            .children()
                            .val(
                                Number(
                                    $(this)
                                        .next()
                                        .children()
                                        .val()
                                ) - 1
                            );
                        o.basket.submitBasketForm(event);
                    }
                }
            });
            if (window.location.hash == "#voucher") {
                o.basket.showVoucherForm();
            }
        },
        submitBasketForm: function (event) {
            $("#messages").html("");
            var payload = $("#basket_formset").serializeArray();
            $.post(o.basket.url, payload, o.basket.submitFormSuccess, "json");
            if (event) {
                event.preventDefault();
            }
        },
        submitFormSuccess: function (data) {
            $("#content_inner").html(data.content_html);
            var sum = 0;
            $("#basket_formset .input-quantity").each(function () {
                sum += Number($(this).val());
            });
            if (sum > 0) {
                if (!$("#total-quantity-on-cart").hasClass("header-cart-circle")) {
                    $("#total-quantity-on-cart").addClass("header-cart-circle");
                }
                $("#total-quantity-on-cart").text(sum);
            } else {
                $("#total-quantity-on-cart").text("");
                $("#total-quantity-on-cart").removeClass("header-cart-circle");
            }

            o.messages.clear();
            for (var level in data.messages) {
                for (var i = 0; i < data.messages[level].length; i++) {
                    o.messages[level](data.messages[level][i]);
                }
            }
            o.uiAnimate.loading("hide");
            o.basket.is_form_being_submitted = false;
        },
        showVoucherForm: function () {
            $("#voucher_form_container").show();
            $("#voucher_form_link").hide();
            $("#id_code").focus();
        },
        hideVoucherForm: function () {
            $("#voucher_form_container").hide();
            $("#voucher_form_link").show();
        },
        checkAndSubmit: function ($ele, formPrefix, idSuffix) {
            if (o.basket.is_form_being_submitted) {
                return;
            }
            var formID = $ele.attr("data-id");
            var inputID = "#id_" + formPrefix + "-" + formID + "-" + idSuffix;
            $(inputID).attr("checked", "checked");
            $ele.closest("form").submit();
            o.basket.is_form_being_submitted = true;
        }
    };

    o.checkout = {
        gateway: {
            init: function () {
                var radioWidgets = $("form input[name=options]");
                var selectedRadioWidget = $("form input[name=options]:checked");
                o.checkout.gateway.handleRadioSelection(
                    selectedRadioWidget.val()
                );
                radioWidgets.change(o.checkout.gateway.handleRadioChange);
                $("#id_username").focus();
            },
            handleRadioChange: function () {
                o.checkout.gateway.handleRadioSelection($(this).val());
            },
            handleRadioSelection: function (value) {
                var pwInput = $("#id_password");
                if (value == "anonymous" || value == "new") {
                    pwInput.attr("disabled", "disabled");
                } else {
                    pwInput.removeAttr("disabled");
                }
            },
            handdleShipping: function () {
                // if ($(this).data("label")) {
                // $("#name-select").html($(this).data("label"));
                var element = $(".method-code");
                const price = element.data("price") || element.data("error");
                const estimation = element.data("estimation") || "-";
                let elementShipping = $("#shipping-price-payment");
                let elementEstimationShipping = $("#shipping-estimation");
                let elementEstimationContainer = $('.estimation-container');
                elementShipping.html(price);
                elementEstimationShipping.html(estimation)
                elementShipping.removeClass("text-alert");
                $("#next-button").empty();
                if (price === "Tidak Tersedia" || price === "Area Tidak Terjangkau") {
                    elementShipping.addClass("text-alert");
                    $("#next-button").append("<a href=\"/checkout/shipping-address/\"  class=\"btn btn-alert btn-block\">\n" +
                        "        Kembali\n" +
                        "    </a>");
                } else {
                    $("#next-button").append("<button class=\"btn btn-black btn-block\" type=\"submit\"\n" +
                        "                                    data-loading-text=\"Lanjut ...\">\n" +
                        "                                Lanjut Pembayaran\n" +
                        "                            </button>");
                }
                // }

                // o.uiAnimate.dropDownClose()
            }
        }
    };
    o.onValidationPaymentDetails = {
        init: function (options) {
            const urlParams = new URLSearchParams(window.location.search);
            const paymentMethod = urlParams.get('payment-method');
            const payments = urlParams.get('payments');
            if (paymentMethod && payments) {
                let paymentResult = o.onValidationPaymentDetails.checkPaymentAvailable(paymentMethod, payments, options);
                if (paymentResult) {
                    let resultElement = payments === "credit_card" ? "credit-card" : payments;
                    const elementPayment = $("#" + resultElement);
                    elementPayment.addClass('active');
                    elementPayment.siblings()
                        .addClass("active")
                        .slideDown(200);
                    elementPayment.children("input").prop('checked', true);
                    elementPayment.siblings().find("select.method-payment-chooose").prop('disabled', false);
                    elementPayment.siblings().find("select.method-payment-chooose").val(paymentMethod);
                    $('button#place-order[type="submit"]').prop('disabled', false);
                }
            }
            $('select.method-payment-chooose').on("change", function (event) {
                var value = $(this).val();
                if (value.length > 0) {
                    $('button#place-order[type="submit"]').prop('disabled', false);
                } else {
                    $('button#place-order[type="submit"]').prop('disabled', true);
                }
            });

            $('#form-payment-methods').submit(function () {
                let resultSubmit = false;
                if ($(this).find('.check-mark-method-container.active')) {
                    let elementSelector = $(this).find('.check-mark-method-container.active');
                    let idName = elementSelector.data('select');
                    let payment_method = $('select' + "#" + idName).val();
                    let payments = elementSelector.children().val();
                    resultSubmit = o.onValidationPaymentDetails.checkPaymentAvailable(payment_method, payments, options);
                    if (resultSubmit) {
                        $('button#place-order[type="submit"]').prop('disabled', true);
                    }
                }
                return resultSubmit;
            });
        },
        snapPayment() {
            var payButton = document.getElementById('pay-button');
            payButton.addEventListener('click', function () {
                $(this).prop('disabled', true);
                snap.pay('{{ token|escapejs }}', {
                        onSuccess: function (result) {
                            $('#place_order_form').submit();
                        },
                        onPending: function (result) {
                            $('#place_order_form').submit();
                        },
                        onError: function (result) {
                            // console.log(result);
                        },
                        onClose: function () {
                            $("#pay-button").prop('disabled', false);
                        }
                    }
                );
            });
        },
        checkPaymentAvailable(paymentMethod, payments, options) {
            let paymentMethodData = false;
            let paymentResult = false;
            let dataAvailable = false;
            if (options) {
                dataAvailable = JSON.parse(options.replace(/'/g, '"'));
            }
            payments = payments === "credit_card" ? "credit-card" : payments;
            if (paymentMethod && payments && dataAvailable) {
                $.each(dataAvailable, function (key, item) {
                    if (item.payment_method === payments) {
                        paymentMethodData = {
                            key: key,
                            method: item.payment_method,
                            available: item.available
                        };
                    }
                });
                if (paymentMethodData) {
                    $.each(paymentMethodData.available, function (key, item) {
                        if (item === paymentMethod) {
                            paymentResult = true
                        }
                    });
                }
            }
            return paymentResult;
        }
    };
    o.productDetail = {
        init: function () {
            o.productDetail.onLoadProductDetail()
        },
        onLoadProductDetail: function () {
            $(window).resize(function () {
                o.productDetail.onChangeElement()
            });

            $(document).ready(function () {
                o.productDetail.onChangeElement();
                if ($("#tab-read-more a.tab-button").hasClass('active')) {
                    const elementCheck = $("#" + $("#tab-read-more a.tab-button").data("id"))
                    if (elementCheck.height() >= 128) {
                        elementCheck.children(".desc-tab-content").css({height: "100px"});
                    } else {
                        elementCheck.children(".gdn-tab-read-more").hide()
                    }
                }

            });
        },
        onChangeElement: function () {
            if ($(window).width() < 980) {
                $("#sidebar").prependTo("#sidebar-mobile");
            } else {
                $("#sidebar").prependTo("#sidebar-desktop");
            }
        },
    };
    o.productList = {
        init: function () {
            $(".active-category")
                .parents()
                .closest("li")
                .addClass("active-category active-url");
        }
    }
    o.slider = {
        init: function () {
            o.slider.sliderProductHome()
            o.slider.homeBanner()
            o.slider.homeTesti()
        },

        productDetailSlide: function () {
            let galleryTop = new Swiper(".gdn-product-detail-gallery-image", {
                spaceBetween: 0,
                centeredSlides: true,
                slidesPerView: 1,
                direction: "horizontal",
                nextButton: ".gdn-slider-button-right",
                prevButton: ".gdn-slider-button-left",

                navigation: {
                    prevEl: ".gdn-slider-button-left",
                    nextEl: ".gdn-slider-button-right",
                    disabledClass: "gdn-slider-button-disabled",
                },
                pagination: {
                    el: ".gdn-slider-pagination",
                    type: "bullets",
                }
            });
            let galleryThumbs = new Swiper(".gdn-product-detail-gallery-thumb", {
                    spaceBetween: 10,
                    slidesPerView: 5,
                    touchRatio: 0.2,
                    centeredSlides: true,
                    slideToClickedSlide: true,
                    slideActiveClass: "active"
                }
            );
            galleryTop.controller.control = galleryThumbs;
            galleryThumbs.controller.control = galleryTop;

        },

        homeTesti: function () {
            o.slider.swiperCreate(
                {
                    className: ".slider-home-testi",
                    config: {
                        spaceBetween: 0,
                        centeredSlides: true,
                        slidesPerView: 1,
                        direction: "horizontal",
                        nextButton: ".gdn-slider-button-right",
                        prevButton: ".gdn-slider-button-left",

                        navigation: {
                            prevEl: ".gdn-slider-button-left",
                            nextEl: ".gdn-slider-button-right",
                            disabledClass: "gdn-slider-button-disabled",
                        },
                        pagination: {
                            el: ".gdn-slider-pagination",
                            type: "bullets",
                        }
                    }
                }
            )
        },
        homeBanner: function () {
            o.slider.swiperCreate(
                {
                    className: ".slider-home-banner",
                    config: {
                        spaceBetween: 0,
                        centeredSlides: true,
                        slidesPerView: 1,
                        direction: "horizontal",
                        nextButton: ".gdn-slider-button-right",
                        prevButton: ".gdn-slider-button-left",
                        navigation: {
                            prevEl: ".gdn-slider-button-left",
                            nextEl: ".gdn-slider-button-right",
                            disabledClass: "gdn-slider-button-disabled",
                        },
                        pagination: {
                            el: ".gdn-slider-pagination",
                        }
                    }
                }
            )
        },

        sliderProductHome: function () {
            o.slider.swiperCreate(
                {
                    className: ".slider-product",
                    config: {
                        spaceBetween: 15,
                        centeredSlides: false,
                        slidesPerView: 4,
                        direction: "horizontal",
                        nextButton: ".gdn-slider-button-right",
                        prevButton: ".gdn-slider-button-left",
                        navigation: {
                            prevEl: ".gdn-slider-button-left",
                            nextEl: ".gdn-slider-button-right",
                            disabledClass: "gdn-slider-button-disabled",
                        },
                        breakpoints: {
                            980: {
                                slidesPerView: 'auto',
                                spaceBetween: 15
                            }
                        }
                    }
                }
            )
        },

        swiperCreate: function (result) {
            new Swiper(result.className, result.config);
        }
    }
    o.uiAnimate = {
        init: function () {
            o.uiAnimate.documentScroll();
            o.uiAnimate.search();
            o.uiAnimate.dropDown();
            o.uiAnimate.documentClick();
            o.uiAnimate.floatButton();
            o.uiAnimate.onOpenCategory();
            o.uiAnimate.onCopy()
            if ($(window).width() < 980) {
                // o.uiAnimate.mobileCategory();
                o.uiAnimate.onFilterCategory();
                o.uiAnimate.onBackHeader();
            }
            setTimeout(function () {
                $("#messages").slideUp("slow");
                setTimeout(function () {
                    $("#messages").html("");
                    $("#messages").show();
                }, 1000);

            }, 3000);
        },
        onFilterCategory: function () {
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
            $(".side_categories dl > dt.nav-header").click(function (e) {
                e.preventDefault();
                if ($(this).parent().hasClass('active')) {
                    $(this).parent().removeClass('active');
                    $(this).parent().find('*').hide();
                    $("dt.nav-header, dt.nav-header > span, dt.nav-header > i").show();
                } else {
                    $(this).parent().addClass('active');
                    $(this).parent().find('*').show();
                    $(this).parent().find('button').hide();
                }

            })
        },

        onCopy: function () {
            $("#copy-data").on("click", function (e) {
                e.preventDefault();
                var copyText = document.getElementById("code-copy");
                copyText.select();
                document.execCommand("copy");
                alert("Copied the text: " + copyText.value);
            });
        },


        onBackHeader: function () {
            $(".header-logo a.btn").on("click", function (e) {
                e.preventDefault();
                const elementHeader = $(".header-logo a.btn");
                if (elementHeader.hasClass("filter-mobile-close")) {
                    const sortElement = $(".gdn-product-list-left");
                    const sortElementUl = $(".gdn-product-list-left > ul");
                    sortElement.hide();
                    $(".header-logo > a.btn").removeClass("filter-mobile-close");
                    $('body').removeClass("overflow-no-scroll");
                    sortElement.removeClass("active");
                    sortElementUl.css({'opacity': 0, 'top': 0}).animate({'opacity': '1', 'top': "50%"}, 100);
                    return false;
                }
                if (elementHeader.hasClass("filter-mobile-close")) {
                    const sortElement = $(".gdn-product-list-left");
                    const sortElementUl = $(".gdn-product-list-left > ul");
                    sortElement.hide();
                    $(".header-logo > a.btn").removeClass("filter-mobile-close");
                    $('body').removeClass("overflow-no-scroll");
                    sortElement.removeClass("active");
                    sortElementUl.css({'opacity': 0, 'top': 0}).animate({'opacity': '1', 'top': "50%"}, 100);
                }
                if (elementHeader.hasClass("back-home")) {
                    $("nav.header-menu").removeClass("active");
                    elementHeader.removeClass("active").removeClass("back-home");
                    $('nav.header-menu > ul > li > a').css("opacity", "0");
                    $("body").removeClass("overflow-no-scroll");
                } else {
                    window.history.go(-1);
                    return false;
                }

            })
        },

        onOpenCategory: function () {
            $(".open-category").on("click", function (e) {
                e.preventDefault();
                $("body").addClass("overflow-no-scroll")
                $(".header-logo a.btn").addClass("active").addClass("back-home");
                $("nav.header-menu").show().addClass("active");
                const lengthElement = $("nav.header-menu > ul > li").length;
                var i;
                for (i = 0; i < lengthElement; i++) {
                    $('nav.header-menu > ul > li:nth-child(' + (i + 1) + ') > a').fadeTo(200 * (i + 1), 1);
                }


            })
        },


        loading: function (status) {
            if (status === "show") {
                $('#loading-action').show();
            } else {
                $('#loading-action').hide();
            }
        },
        tooltip: function (element, timeOut) {
            if (!element.hasClass('active')) {
                element.addClass('active');
                element.show();
                setTimeout(function () {
                    element.hide();
                    element.removeClass('active');
                }, timeOut)
            }
        },
        showHide: function () {
            $('.show-hide').on("click", function (e) {
                e.preventDefault();
                $("input#id_code").val("");
                $("input#voucher-input").val("");
                const element = $(this).data('id');
                const elementRemove = $(this).data('remove');
                if (element) {
                    let elementClass = $("." + element);
                    let elementClassRemove = $('.' + elementRemove) || false;
                    if (elementClass.hasClass('active')) {
                        elementClass.removeClass('active');
                        elementClass.hide();
                        if (elementClassRemove) {
                            elementClassRemove.removeClass('active');
                            elementClassRemove.show();
                        }
                    } else {
                        elementClass.addClass('active');
                        elementClass.show();
                        if (elementClassRemove) {
                            elementClassRemove.addClass('active');
                            elementClassRemove.hide();
                        }
                    }
                }
            });
        },
        documentScroll: function () {
            if ($(document).scrollTop() < 400) {
                $(".floating-button").fadeOut()
            } else {
                $(".floating-button").fadeIn()
            }
            $(document).scroll(function () {
                if ($(window).width() > 760) {
                    o.uiAnimate.headerDesktop($(document).scrollTop());
                }
                if ($("html,body").scrollTop() < 400) {
                    $(".floating-button").fadeOut()
                } else {
                    $(".floating-button").fadeIn()

                }


            });
        },
        floatButton: function () {
            $(".scroll-top-top").on("click", function (e) {
                e.preventDefault();
                $("html, body").animate({scrollTop: 0}, "slow");
                return false;
            });

        },
        mobileCategory: function () {
            $(".has-children").on("click", function (e) {
                e.preventDefault();
                const element = $(this);
                const elementChild = element.siblings('.parent');
                const parentName = element.children('span').text();

                if (element.data("parent") === "None") {
                    localStorage.setItem("parentHref", element.attr('href'));
                    localStorage.setItem("parentName", parentName);
                    elementChild.prepend("<li class=\"has-children-first\" style=\"padding-left:0;\" ><a class=\"has-children-back\" style=\"display:flex; align-items:center;justify-content:flex-start;\" data-parent=\"back-to-first\" href=\"#\"><i style=\"margin-right:17px;\" class=\"fa fa-chevron-left\"></i><span>Kategori Utama</span></a></li><li class=\"parent-name\"><a style=\"font-weight: 500!important;\" href='" + element.attr('href') + "' >" + parentName + "</a></li>")
                } else {
                    elementChild.prepend("<li class=\"has-children-first\" style=\"padding-left:0;\" data-back=\"reset\" ><a class=\"has-children-back\" style=\"display:flex; align-items:center;justify-content:flex-start;\" data-parent=\"back-to-first\" href=\"#\"><i style=\"margin-right:17px;display:block;\" class=\"fa fa-chevron-left\"></i><span>Kategori Utama</span></a></li><li data-back=\"parent-two\" class=\"has-children-first\" style=\"padding-left:0;\" ><a class=\"has-children-back\" style=\"justify-content:flex-start;display:flex; align-items: center\"  data-parent=\"back-to-first\" href=\"#\"><i style=\"margin-right:17px;display:block;\" class=\"fa fa-chevron-left\"></i><span>" + element.data("parent") + "</span></a></li><li class=\"parent-name\"><a style=\"font-weight: 500!important;\" href='" + element.attr('href') + "'>" + parentName + "</a></li>")
                }
                elementChild.addClass('active');
                elementChild.show();
            });

            $('.parent').on('click', "li.has-children-first", function (e) {
                e.preventDefault();
                if ($(this).data('back') === "reset") {
                    if ($(".parent li").not(this).hasClass("has-children-first")) {
                        $(".parent li.parent-name").remove();
                        $(".parent li.has-children-first").remove();
                    }
                    $('.parent').hide();
                    $('.parent').removeClass('active');
                } else {
                    $(this).parent().removeClass('active');
                    $(this).parent().hide();
                    $(this).siblings('.parent-name').remove();
                    $(this).remove();
                    $(".parent li.has-children-first").remove();
                    if ($(this).data('back') === "parent-two") {
                        $(".parent li.parent-name").remove();
                        const parentName = $(this).children().text();
                        const hrefName = localStorage.getItem("parentHref");
                        $("ul.parent.active").prepend("<li class=\"has-children-first\" style=\"padding-left:0;\" ><a class=\"has-children-back\" style=\"display:flex; align-items:center;justify-content:flex-start;\" data-parent=\"back-to-first\" href=\"#\"><i style=\"margin-right:17px;\" class=\"fa fa-chevron-left\"></i><span>Kategori Utama</span></a></li><li class=\"parent-name\"><a style=\"font-weight: 500!important;\" href='" + hrefName + "'>" + parentName + "</li>")
                        localStorage.removeItem("parentHref");
                        localStorage.removeItem("parentName");
                    }
                }
            });

            $(".btn-category").on('click', function (e) {
                e.preventDefault();
                if ($(this).data('status') === "open") {
                    $(".gdn-header-bottom").show();
                    $("#gdn-top-mobile").addClass("open-menu")
                    $("body").addClass("overflow-no-scroll");
                } else {
                    $(".gdn-header-bottom").hide();
                    $("#gdn-top-mobile").removeClass("open-menu")
                    $("body").removeClass("overflow-no-scroll");
                }

            });
        },
        onEventTargetCloset: function ($class) {
            let data = $(event.target).closest($class).length;
            return data;
        },
        documentClick: function () {
            $(document).on("click", function (event) {
                // if (
                //     !o.uiAnimate.onEventTargetCloset(".drop-down-content") &&
                //     !o.uiAnimate.onEventTargetCloset(".gdn-dropdown-content") &&
                //     !o.uiAnimate.onEventTargetCloset(".gdn-dropdown-button") &&
                //     !o.uiAnimate.onEventTargetCloset(".drop-down-button")
                // ) {
                //     if ($(".gdn-dropdown-content, .gdn-dropdown-menu").hasClass("active")) {
                //         o.uiAnimate.dropDownClose()
                //     }
                // }
            });

        },
        dropDownClose: function () {
            $(".gdn-dropdown-content, .gdn-dropdown-menu")
                .removeClass("active")
                .slideUp();
        },
        dropDown: function () {
            $(".gdn-dropdown-button").click(function (e) {
                e.preventDefault();
                const dropdownContentElement = $("#" + $(this).data("id"));
                const activeElement = $(".gdn-dropdown-menu");
                if (dropdownContentElement.hasClass("active")) {
                    dropdownContentElement.removeClass("active");
                    dropdownContentElement.slideUp();
                } else {
                    if (activeElement.hasClass("active")) {
                        activeElement.slideUp();
                    }
                    dropdownContentElement.slideDown();
                    dropdownContentElement.addClass("active");

                }
                return false
            });
        },
        headerDesktop: function (scrollTop) {
            let headerElement = {
                header: $(".gdn-header-side-top"),
                headerSideTop: $(".gdn-header-side-top"),
                headerContent: $(".gdn-header-bottom-content"),
                navContent: $(
                    ".gdn-header-bottom-navbar > ul.gdn-list-none.navbar-header-ul > li.dropdown-menu-navbar"
                ),
                headerBottom: $(
                    ".gdn-header-bottom-content .logo, .gdn-header-bottom-content form"
                )
            };
            if (scrollTop > 250) {
                headerElement.header.addClass("active");
                headerElement.navContent.addClass("active");
                headerElement.headerSideTop.slideUp("fast");
                headerElement.headerContent.addClass("active");
                headerElement.headerBottom.show("fast");
            } else {
                headerElement.header.removeClass("active");
                headerElement.navContent.removeClass("active");
                headerElement.headerSideTop.slideDown("fast");
                headerElement.headerContent.removeClass("active");
                headerElement.headerBottom.hide("fast");
            }
        },
        quantity: function () {
            $("#quantity-form, #quantity-form-mobile").on("change", ".input-quantity", function (
                event
            ) {
                let element = $(this);
                let value = +element.val();
                let max = +element.attr("max");
                value = value <= 0 ? 1 : value;
                if (value <= max) {
                    element.val(value);
                } else {
                    element.val(max);
                }
                event.preventDefault();
            });
            $("#quantity-form, #quantity-form-mobile").on("click", "button.qty-button", function (
                event
            ) {
                const typeButton = $(this).data("id");
                if (typeButton === "plus") {
                    let max = +$(this)
                        .prev()
                        .attr("max");
                    let value = +$(this)
                        .prev()
                        .val();

                    if (value < max) {
                        $(this)
                            .prev()
                            .val(value + 1);
                    }
                } else {
                    if (
                        $(this)
                            .next()
                            .val() > 1
                    ) {
                        $(this)
                            .next()
                            .val(
                                Number(
                                    $(this)
                                        .next()
                                        .val()
                                ) - 1
                            );
                    }
                }
                event.preventDefault();
            });
        },
        read: function () {
            $(".tab-read-more").click(function (e) {
                e.preventDefault();
                const idContent = "#" + $(this).data("id");
                if ($(".desc-tab-content").hasClass("active")) {
                    $(idContent + ">.desc-tab-content").animate(
                        {height: 100},
                        200
                    );
                    $(idContent + ">.desc-tab-content").removeClass("active");
                    $(idContent + "-readmore").text("Selengkapnya...");
                } else {
                    $(idContent + ">.desc-tab-content").animate(
                        {height: "100%"},
                        200
                    );
                    $(idContent + ">.desc-tab-content").addClass("active");
                    $(idContent + "-readmore").text("Tutup");
                }
            });
        },
        search: function () {
            let type_input = $(".gdn-type-input");
            if (type_input.val()) {
                if (type_input.val().length > 3) {
                    const my_txt = type_input.val();
                    const type = type_input.data("type");
                    switch (type) {
                        case "length":
                            const len = my_txt.length;
                            const action = "." + type_input.data("action");
                            const change = "." + type_input.data("change");
                            if (len > 3) {
                                $(action).show();
                                $(action).addClass("active");
                                $(change).removeClass("active");
                                $(change).hide();
                            } else {
                                $(action).hide();
                                $(action).removeClass("active");
                                $(change).addClass("active");
                                $(change).show();
                            }
                            break;
                        default:
                            break;
                    }
                }
                type_input.on("keyup", function () {
                    const my_txt = $(this).val();
                    const type = $(this).data("type");
                    switch (type) {
                        case "length":
                            const len = my_txt.length;
                            const action = "." + $(this).data("action");
                            const change = "." + $(this).data("change");
                            if (len > 3) {
                                $(action).show();
                                $(action).addClass("active");
                                $(change).removeClass("active");
                                $(change).hide();
                            } else {
                                $(action).hide();
                                $(action).removeClass("active");
                                $(change).addClass("active");
                                $(change).show();
                            }
                            break;
                        default:
                            break;
                    }
                });
            }
        }
    };
    o.searchBox = {
        init: function () {
            o.searchBox.onClickSearch();
            o.searchBox.onClickSearchMobile();
        },
        onClickSearch: function () {
            var windowsize = $(window).width();
            if (windowsize > 980) {
                $("#input-search").focus(function (e) {
                    $(".header-logo").addClass("header-logo-focus");
                    $(".header-menu").addClass("header-menu-focus");
                    $("#input-search").css('width', '680px');
                })
                $("#input-search").focusout(function (e) {
                    $(".header-logo").removeClass("header-logo-focus");
                    $("#input-search").css('width', '280px');
                    setTimeout(function () {
                        $(".header-menu").removeClass("header-menu-focus");
                    }, 300);
                })
            }

        },
        onClickSearchMobile() {
            $(".search-button-mobile").on('click', function (e) {
                e.preventDefault();
                $(".header-cart").hide();
                $('.search-box').focus();
                $(".search-box").show();
                $(".header-right").addClass("active");
                $(".search-icon").removeClass("ion-ios-search-strong").addClass("ion-ios-close-empty");
            });

            $(".search-button").on('click', function (e) {
                e.preventDefault();
                $(".header-cart").show();
                $(".search-box").hide();
                $(".header-right").removeClass("active");
                $(".search-icon").removeClass("ion-ios-close-empty").addClass("ion-ios-search-strong");
            });
        }
    };


    o.datetimepickers = {
        init: function () {
            o.datetimepickers.initDatePickers(window.document);
        },
        options: {
            languageCode: "en",
            dateFormat: "yy-mm-dd",
            timeFormat: "hh:ii",
            datetimeFormat: "yy-mm-dd hh:ii",
            stepMinute: 15
        },
        initDatePickers: function (el) {
            if ($.fn.datetimepicker) {
                var defaultDatepickerConfig = {
                    format: o.datetimepickers.options.dateFormat,
                    autoclose: true,
                    language: o.datetimepickers.options.languageCode,
                    minView: 2
                };
                var $dates = $(el)
                    .find('[data-oscarWidget="date"]')
                    .not(".no-widget-init")
                    .not(".no-widget-init *");
                $dates.each(function (ind, ele) {
                    var $ele = $(ele),
                        config = $.extend({}, defaultDatepickerConfig, {
                            format: $ele.data("dateformat")
                        });
                    $ele.datetimepicker(config);
                });

                var defaultDatetimepickerConfig = {
                    format: o.datetimepickers.options.datetimeFormat,
                    minuteStep: o.datetimepickers.options.stepMinute,
                    autoclose: true,
                    language: o.datetimepickers.options.languageCode
                };
                var $datetimes = $(el)
                    .find('[data-oscarWidget="datetime"]')
                    .not(".no-widget-init")
                    .not(".no-widget-init *");
                $datetimes.each(function (ind, ele) {
                    var $ele = $(ele),
                        config = $.extend({}, defaultDatetimepickerConfig, {
                            format: $ele.data("datetimeformat"),
                            minuteStep: $ele.data("stepminute")
                        });
                    $ele.datetimepicker(config);
                });

                var defaultTimepickerConfig = {
                    format: o.datetimepickers.options.timeFormat,
                    minuteStep: o.datetimepickers.options.stepMinute,
                    autoclose: true,
                    language: o.datetimepickers.options.languageCode
                };
                var $times = $(el)
                    .find('[data-oscarWidget="time"]')
                    .not(".no-widget-init")
                    .not(".no-widget-init *");
                $times.each(function (ind, ele) {
                    var $ele = $(ele),
                        config = $.extend({}, defaultTimepickerConfig, {
                            format: $ele.data("timeformat"),
                            minuteStep: $ele.data("stepminute"),
                            startView: 1,
                            maxView: 1,
                            formatViewType: "time"
                        });
                    $ele.datetimepicker(config);
                });
            }
        }
    };

    o.onScroll = {
        init: function () {
            $(window).scroll(function () {
                let scrollTop = $(window).scrollTop();
                o.onScroll.header(scrollTop)
            });
        },
        header: function (scrollTop) {
            var windowsize = $(window).width();
            if (windowsize > 980) {
                if (scrollTop > 10) {
                    $(".header-top").addClass("header-scroll");
                    $(".header-top").fadeOut();
                    $(".gdn-page").addClass("scroll");
                } else {
                    $(".header-top").removeClass("header-scroll");
                    $(".header-top").fadeIn();
                    $(".gdn-page").removeClass("scroll");
                }
            }
        }
    };

    o.loading = {
        init: function () {
            o.loading.firstLoading()
        },

        firstLoading: function () { // call first loading
            let loadBar = o.loading.loadBarCreate(); // call function for load bar logic
            document.addEventListener('DOMContentLoaded', loadBar, false);
        },

        getElementLoading: function (elementId) {
            return document.getElementById(elementId);
        },

        loadBarCreate: function () {
            // get element overlay progress and progstat
            var ovrl = o.loading.getElementLoading("overlay"),
                prog = o.loading.getElementLoading("progress"),
                stat = o.loading.getElementLoading("progstat"),
                img = document.images,
                c = 0;
            totalImage = img.length; // get all total image from document images

            function imgLoaded() {
                c += 1;
                var perc = ((100 / totalImage * c) << 0) + "%"; // create percentage loading
                prog.style.width = perc;
                stat.innerHTML = "Loading " + perc;
                if (c === totalImage) return doneLoading();
            }

            function doneLoading() { // if loading done show display none the loading
                ovrl.style.opacity = 0;
                setTimeout(function () {
                    ovrl.style.display = "none";
                }, 1200);
            }

            for (var i = 0; i < totalImage; i++) {
                var tImg = new Image();
                tImg.onload = imgLoaded;
                tImg.onerror = imgLoaded;
                tImg.src = img[i].src;
            }
        },
    };

    o.init = function () {
        o.forms.init();
        o.loading.init();
        o.uiAnimate.init();
        o.onScroll.init();
        o.searchBox.init();
        // o.datetimepickers.init();
        // o.page.init();
        // o.responsive.init();
        // o.responsive.initSlider();
        o.compatibility.init();
        o.slider.init();
    };


    return o;
})(oscar || {}, jQuery);
