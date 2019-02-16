/*global jQuery */

var oscar = (function (o, $) {

    o.getCsrfToken = function () {
        // Extract CSRF token from cookies
        var cookies = document.cookie.split(';');
        var csrf_token = null;
        $.each(cookies, function (index, cookie) {
            var cookieParts = $.trim(cookie).split('=');
            if (cookieParts[0] == 'csrftoken') {
                csrf_token = cookieParts[1];
            }
        });
        // Extract from cookies fails for HTML-Only cookies
        if (!csrf_token) {
            csrf_token = $(document.forms.valueOf()).find('[name="csrfmiddlewaretoken"]')[0].value;
        }
        return csrf_token;
    };

    let provinces = '', districts = '', subdistricts = '', villages = '';
    o.personalCourier = {
        init: function (personalCourier_data) {
            if(!$('#id_is_range').prop('checked')){
                $('#id_basket_amount, #id_amount_in_range_shipping_cost').hide().prop('required',false);
                $('label[for="id_basket_amount"], label[for="id_amount_in_range_shipping_cost"]').hide();
            }

            $('#id_is_range').on("change", function() {
                if($('#id_is_range').prop('checked')) {
                    $('#id_basket_amount, #id_amount_in_range_shipping_cost').show().prop('required', true);
                    $('label[for="id_basket_amount"], label[for="id_amount_in_range_shipping_cost"]').show();
                }else{
                    $('#id_basket_amount, #id_amount_in_range_shipping_cost').hide().prop('required',false);
                    $('label[for="id_basket_amount"], label[for="id_amount_in_range_shipping_cost"]').hide();
                }
            });

            provinces = personalCourier_data.provinces;
            districts = personalCourier_data.districts;
            subdistricts = personalCourier_data.subdistricts;
        },
        getDestination: function (el) {
            const value = $(el).val();
            let arrayId = $(el).prop('id').split('-');
            const elIdNum = arrayId[1];

            if (value === 'state')
                $('#id_form-' + elIdNum + '-destination_name').html(provinces).select2();
            else if (value === 'district')
                $('#id_form-' + elIdNum + '-destination_name').html(districts).select2();
            else if (value === 'subdistrict')
                $('#id_form-' + elIdNum + '-destination_name').html(subdistricts).select2();
            else if (value === 'allarea')
                $('#id_form-' + elIdNum + '-destination_name').html(allarea).select2();
            else
                $('#id_form-' + elIdNum + '-destination_name').html('').select2();
        },
        getDestinationId: function (el) {
            const value = parseInt($(el).val().replace(/\./g,''));
            let arrayId = $(el).prop('id').split('-');
            const elIdNum = arrayId[1];

            $('#id_form-' + elIdNum + '-destination').val(value);
        }
    };

    o.destinationRange = {
        init: function (destinationRange_data) {
            const destination_id = $('#id_destination_id'),
                destination_name = $('#id_destination_name'),
                destination_type = $('#id_destination_type'),
                label_destination_id = $('label[for="id_destination_id"]'),
                label_destination_name = $('label[for="id_destination_name"]');


            if(destination_type.val() == 'allarea') {
                destination_name.prop('required', false);
                destination_id.prop('required', false);
                label_destination_name.hide();
                label_destination_name.siblings().hide();
            }else{
                destination_name.prop('required', true);
                destination_id.prop('required', true);
                label_destination_name.show();
                label_destination_name.siblings().show();
            }

            provinces = destinationRange_data.provinces;
            districts = destinationRange_data.districts;
            subdistricts = destinationRange_data.subdistricts;
            form_update = destinationRange_data.form_update;

            destination_id.hide();
            label_destination_id.hide();

            destination_name.change(function(){
                value = $(this).val();
                if(value !== 'allarea') {
                    destination_id.val(parseInt(destination_name.val().replace(/\./g, '')));
                }else{
                    destination_id.val(0);
                }
            });

            if(form_update){
                destination_type.trigger('change');
                destination_name.val(destinationRange_data.destinationId).trigger('change');
            }
        },
        getDestination: function (el) {
            const destination_name = $('#id_destination_name'), destination_id = $('#id_destination_id'),
                value = $(el).val(), label_destination_name = $('label[for="id_destination_name"]');

            if (value === 'state') {
                destination_name.html(provinces).select2().trigger('change');
            }else if (value === 'district'){
                destination_name.html(districts).select2().trigger('change');
            }else if (value === 'subdistrict') {
                destination_name.html(subdistricts).select2().trigger('change');
            }else if (value === 'allarea') {
                    destination_name.html('<option value="0"></option>').select2().trigger('change');
                    destination_name.val('0')
            }else {
                destination_name.html('').select2().trigger('change');
            }

            if(value === 'allarea') {
                destination_name.prop('required', false);
                destination_id.prop('required', false);
                label_destination_name.hide();
                label_destination_name.siblings().hide();

            }else{
                destination_name.prop('required', true);
                destination_id.prop('required', true);
                label_destination_name.show();
                label_destination_name.siblings().show();
            }
        }
    };

    o.voucher = {
        init: function () {
            const destination_range_id = $('#id_destination_range'),
                destination_range = destination_range_id.parent().children().eq(1),
                label_destination_range = $('label[for="id_destination_range"]'),
                benefit_type = $('#id_benefit_type');

            destination_range.hide();
            label_destination_range.hide();

            benefit_type.change(function(){
                value = $(this).val();
                if(value === 'Shipping percentage'
                    || value === 'Shipping absolute'
                    || value === 'Shipping fixed price'){
                    destination_range.show();
                    label_destination_range.show();
                    destination_range_id.prop('required', true);
                }else{
                    destination_range.hide();
                    label_destination_range.hide();
                    destination_range_id.prop('required', false);
                }
            });

            $(document).ready(function(){
                benefit_type.trigger('change');
            })
        },
    };

    o.dashboard = {

        init: function (options) {
            // Run initialisation that should take place on every page of the dashboard.
            var defaults = {
                'languageCode': 'en',
                'dateFormat': 'yy-mm-dd',
                'timeFormat': 'hh:ii',
                'datetimeFormat': 'yy-mm-dd hh:ii',
                'stepMinute': 15,
                'initialDate': new Date(new Date().setSeconds(0)),
                'tinyConfig': {
                    entity_encoding: 'raw',
                    statusbar: false,
                    menubar: true,
                    style_formats: [
                        {title: 'Text', block: 'p'},
                        {title: 'Heading', block: 'h2'},
                        {title: 'Subheading', block: 'h3'}
                    ],
                    paste_data_images: true,
                    plugins: 'print preview fullpage searchreplace autolink visualblocks visualchars fullscreen image link media template codesample table charmap hr pagebreak nonbreaking anchor toc insertdatetime advlist lists textcolor wordcount imagetools contextmenu colorpicker textpattern',
                    toolbar1: 'formatselect | bold italic strikethrough forecolor backcolor | link | alignleft aligncenter alignright alignjustify  | numlist bullist outdent indent  | removeformat',
                }
            };
            o.dashboard.options = $.extend(true, defaults, options);

            o.dashboard.initWidgets(window.document);
            o.dashboard.initForms();

            $(".category-select ul").prev('a').on('click', function () {
                var $this = $(this),
                    plus = $this.hasClass('ico_expand');
                if (plus) {
                    $this.removeClass('ico_expand').addClass('ico_contract');
                } else {
                    $this.removeClass('ico_contract').addClass('ico_expand');
                }
                return false;
            });

            // Adds error icon if there are errors in the product update form
            $('[data-behaviour="affix-nav-errors"] .tab-pane').each(function () {
                var productErrorListener = $(this).find('[class*="error"]:not(:empty)').closest('.tab-pane').attr('id');
                $('[data-spy="affix"] a[href="#' + productErrorListener + '"]').append('<i class="icon-info-sign pull-right"></i>');
            });

            o.dashboard.filereader.init();
        },
        initWidgets: function (el) {
            /** Attach widgets to form input.
             *
             * This function is called once for the whole page. In that case el is window.document.
             *
             * It is also called when input elements have been dynamically added. In that case el
             * contains the newly added elements.
             *
             * If the element selector refers to elements that may be outside of newly added
             * elements, don't limit to elements within el. Then the operation will be performed
             * twice for these elements. Make sure that that is harmless.
             */
            o.dashboard.initDatePickers(el);
            o.dashboard.initMasks(el);
            o.dashboard.initWYSIWYG(el);
            o.dashboard.initSelects(el);
        },
        initMasks: function (el) {
            $(el).find(':input').inputmask();
        },
        initSelects: function (el) {
            // Adds type/search for select fields
            var $selects = $(el).find('select').not('.no-widget-init select').not('.no-widget-init');
            $selects.filter('.form-stacked select').css('width', '95%');
            $selects.filter('.form-inline select').css('width', '300px');
            $selects.select2({width: 'resolve'});
            $(el).find('select.select2').each(function (i, e) {
                var opts = {};
                if ($(e).data('ajax-url')) {
                    opts = {
                        ajax: {
                            url: $(e).data('ajax-url'),
                            dataType: 'json',
                            data: function (params) {
                                return {
                                    q: params.term,
                                    page: params.page || 1
                                };
                            }
                        },
                        multiple: $(e).data('multiple')
                    };
                }
                $(e).select2(opts);
            });
        },
        initDatePickers: function (el) {
            if ($.fn.datetimepicker) {
                var defaultDatepickerConfig = {
                    'format': o.dashboard.options.dateFormat,
                    'autoclose': true,
                    'language': o.dashboard.options.languageCode,
                    'minView': 2
                };
                var $dates = $(el).find('[data-oscarWidget="date"]').not('.no-widget-init').not('.no-widget-init *');
                $dates.each(function (ind, ele) {
                    var $ele = $(ele),
                        config = $.extend({}, defaultDatepickerConfig, {
                            'format': $ele.data('dateformat')
                        });
                    $ele.datetimepicker(config);
                });

                var defaultDatetimepickerConfig = {
                    'format': o.dashboard.options.datetimeFormat,
                    'minuteStep': o.dashboard.options.stepMinute,
                    'autoclose': true,
                    'language': o.dashboard.options.languageCode,
                    'initialDate': o.dashboard.options.initialDate
                };
                var $datetimes = $(el).find('[data-oscarWidget="datetime"]').not('.no-widget-init').not('.no-widget-init *');
                $datetimes.each(function (ind, ele) {
                    var $ele = $(ele),
                        config = $.extend({}, defaultDatetimepickerConfig, {
                            'format': $ele.data('datetimeformat'),
                            'minuteStep': $ele.data('stepminute')
                        });
                    $ele.datetimepicker(config);
                });

                var defaultTimepickerConfig = {
                    'format': o.dashboard.options.timeFormat,
                    'minuteStep': o.dashboard.options.stepMinute,
                    'autoclose': true,
                    'language': o.dashboard.options.languageCode,
                    'initialDate': o.dashboard.options.initialDate
                };
                var $times = $(el).find('[data-oscarWidget="time"]').not('.no-widget-init').not('.no-widget-init *');
                $times.each(function (ind, ele) {
                    var $ele = $(ele),
                        config = $.extend({}, defaultTimepickerConfig, {
                            'format': $ele.data('timeformat'),
                            'minuteStep': $ele.data('stepminute'),
                            'startView': 1,
                            'maxView': 1,
                            'formatViewType': 'time'
                        });
                    $ele.datetimepicker(config);
                });
            }
        },
        initWYSIWYG: function (el) {
            // Use TinyMCE by default
            var $textareas = $(el).find('textarea').not('.no-widget-init textarea').not('.no-widget-init');
            $textareas.filter('form.wysiwyg textarea').tinymce(o.dashboard.options.tinyConfig);
            $textareas.filter('.wysiwyg').tinymce(o.dashboard.options.tinyConfig);
        },
        initForms: function () {
            // Disable buttons when they are clicked and show a "loading" message taken from the
            // data-loading-text attribute (http://getbootstrap.com/2.3.2/javascript.html#buttons).
            // Do not disable if button is inside a form with invalid fields.
            // This uses a delegated event so that it keeps working for forms that are reloaded
            // via AJAX: https://api.jquery.com/on/#direct-and-delegated-events
            $(document.body).on('click', '[data-loading-text]', function () {
                var form = $(this).parents("form");
                if (!form || $(":invalid", form).length == 0)
                    $(this).button('loading');
            });
        },
        offers: {
            init: function () {
                oscar.dashboard.offers.adjustBenefitForm();
                $('#id_type').change(function () {
                    oscar.dashboard.offers.adjustBenefitForm();
                });
            },
            adjustBenefitForm: function () {
                var type = $('#id_type').val(),
                    $valueContainer = $('#id_value').parents('.control-group');
                if (type == 'Multibuy') {
                    $('#id_value').val('');
                    $valueContainer.hide();
                } else {
                    $valueContainer.show();
                }
            }
        },
        product_attributes: {
            init: function () {
                var type_selects = $("select[name$=type]");

                type_selects.each(function () {
                    o.dashboard.product_attributes.toggleOptionGroup($(this));
                });

                type_selects.change(function () {
                    o.dashboard.product_attributes.toggleOptionGroup($(this));
                });
            },

            toggleOptionGroup: function (type_select) {
                var option_group_select = $('#' + type_select.attr('id').replace('type', 'option_group'));
                var v = type_select.val();
                option_group_select.parent().parent().toggle(v === 'option' || v === 'multi_option');
            }
        },
        ranges: {
            init: function () {
                $('[data-behaviours~="remove"]').click(function () {
                    var $this = $(this);
                    $this.parents('table').find('input').prop('checked', false);
                    $this.parents('tr').find('input').prop('checked', true);
                    $this.parents('form').submit();
                });
            }
        },
        orders: {
            initTabs: function () {
                if (location.hash) {
                    $('.nav-tabs a[href=' + location.hash + ']').tab('show');
                }
            },
            initTable: function () {
                var table = $('form table'),
                    input = $('<input type="checkbox" />').css({
                        'margin-right': '5px',
                        'vertical-align': 'top'
                    });
                $('th:first', table).prepend(input);
                $(input).change(function () {
                    $('tr', table).each(function () {
                        $('td:first input', this).prop("checked", $(input).is(':checked'));
                    });
                });
            }
        },
        reordering: (function () {
            var options = {
                    handle: '.btn-handle',
                    submit_url: '#'
                },
                saveOrder = function (data) {
                    // Get the csrf token, otherwise django will not accept the
                    // POST request.
                    var csrf = o.getCsrfToken();
                    $.ajax({
                        type: 'POST',
                        data: $.param(data),
                        dataType: "json",
                        url: options.submit_url,
                        beforeSend: function (xhr) {
                            xhr.setRequestHeader("X-CSRFToken", csrf);
                        }
                    });
                },
                init = function (user_options) {
                    options = $.extend(options, user_options);
                    var group = $(options.wrapper).sortable({
                        group: 'serialization',
                        containerSelector: 'tbody',
                        itemSelector: 'tr',
                        handle: options.handle,
                        vertical: true,
                        onDrop: function ($item, container, _super) {
                            var data = group.sortable("serialize");
                            saveOrder(data);
                            _super($item, container);
                        },
                        placeholder: '<tr class="placeholder"/>',
                        serialize: function (parent, children, isContainer) {
                            if (isContainer) {
                                return children;
                            }
                            else {
                                var parts = parent.attr('id').split('_');
                                return {'name': parts[0], 'value': parts[1]};
                            }
                        }
                    });
                };

            return {
                init: init,
                saveOrder: saveOrder
            };
        }()),
        search: {
            init: function () {
                var searchForm = $(".orders_search"),
                    searchLink = $('.pull_out'),
                    doc = $('document');
                searchForm.each(function () {
                    doc.css('height', doc.height());
                });
                searchLink.on('click', function () {
                        searchForm.parent()
                            .find('.pull-left')
                            .toggleClass('no-float')
                            .end().end()
                            .slideToggle("fast");
                    }
                );
            }
        },
        filereader: {
            init: function () {
                // Add local file loader to update image files on change in
                // dashboard. This will provide a preview to the selected
                // image without uploading it. Upload only occures when
                // submitting the form.
                if (window.FileReader) {
                    $('input[type="file"]').change(function (evt) {
                        var reader = new FileReader();
                        var imgId = evt.target.id + "-image";
                        reader.onload = (function () {
                            return function (e) {
                                var imgDiv = $("#" + imgId);
                                imgDiv.children('img').attr('src', e.target.result);
                            };
                        })();
                        reader.readAsDataURL(evt.target.files[0]);
                    });
                }
            }
        },
        product_lists: {
            init: function () {
                var imageModal = $("#product-image-modal"),
                    thumbnails = $('.sub-image');
                thumbnails.click(function (e) {
                    e.preventDefault();
                    var a = $(this);
                    imageModal.find('h4').text(a.find('img').attr('alt'));
                    imageModal.find('img').attr('src', a.data('original'));
                    imageModal.modal();
                });
            }
        },
    };

    return o;

})(oscar || {}, jQuery);
