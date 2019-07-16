// Get the list of locations for the selected Network

var progress = ($('#progress'));
var resultsbox = ($('#resultsbox'));
var target_error = ($('#target_error'));
var target_input = ($('#target'));
adjustDropdowns();
clearPage();

// Bulma Toggable Dropdown - help text
$('#help-dropdown').click(
    function (event) {
        event.stopPropagation();
        $(this).toggleClass('is-active');
    }
);

// ClipboardJS Elements
var btn_copy = document.getElementById('btn-copy');
var clipboard = new ClipboardJS(btn_copy);
clipboard.on('success', function (e) {
    console.log(e);
    $('#btn-copy').addClass('is-success').addClass('is-outlined');
    $('#copy-icon').removeClass('icofont-ui-copy').addClass('icofont-check');
    setTimeout(function () {
        $('#btn-copy').removeClass('is-success').removeClass('is-outlined');
        $('#copy-icon').removeClass('icofont-check').addClass('icofont-ui-copy');
    }, 1000);
});
clipboard.on('error', function (e) {
    console.log(e);
});

$('.modal-background, .modal-close').click(
    function (event) {
        event.stopPropagation();
        $('.modal').removeClass("is-active");
    }
);

// Adjust behavior of help text dropdown based on device screen size
$('#help-dropdown-button').click(
    function (event) {
        if (window.innerWidth < 1024) {
            $('#help-dropdown').removeClass('is-right');
            $('.lg-help').addClass('lg-help-mobile').removeClass('lg-help');
        }
    }
);

function adjustDropdowns() {
    var actual_width = window.innerWidth;
    if (actual_width < 1024) {
        $('#lg-netlocdropdown').removeClass('has-addons').removeClass('has-addons-centered').addClass('is-grouped').addClass('is-grouped-centered').addClass('is-grouped-multiline');
        $('#network').css('width', actual_width * 0.85);
        $('#location').css('width', actual_width * 0.85);
    }
}

function clearErrors() {
    progress.hide();
    target_error.hide();
    if (target_input.hasClass("is-warning")) {
        target_input.removeClass("is-warning");
    }
    if (target_input.hasClass("is-danger")) {
        target_input.removeClass("is-danger");
    }
}

function clearPage() {
    progress.hide();
    resultsbox.hide();
    target_error.hide();
    if (target_input.hasClass("is-warning")) {
        target_input.removeClass("is-warning");
    }
    if (target_input.hasClass("is-danger")) {
        target_input.removeClass("is-danger");
    }
}

function prepResults() {
    progress.show();
    resultsbox.show();
}

$(document).ready(function () {
    var defaultasn = $("#network").val();
    $.ajax({
        url: '/locations/' + defaultasn,
        context: document.body,
        type: 'get',
        success: function (data) {
            selectedRouters = data;
            console.log(selectedRouters);
            updateRouters(selectedRouters);
        },
        error: function (err) {
            console.log(err);
        }
    });
});

$('#network').on('change', (function (event) {
    var asn = $("select[id=network").val();
    $('#location').children(":not(#text_location)").remove();
    $.ajax({
        url: '/locations/' + asn,
        type: 'get',
        success: function (data) {
            clearPage();
            updateRouters(JSON.parse(data));
        },
        error: function (err) {
            console.log(err);
        }
    });
}));

function updateRouters(locations) {
    locations.forEach(function (r) {
        $('#location').append($("<option>").attr('value', r.hostname).text(r.display_name));
    });
}

$('#helplink_bgpc').click(function (event) {
    $('#help_bgp_community').addClass("is-active");
});

$('#helplink_bgpa').click(function (event) {
    $('#help_bgp_aspath').addClass("is-active");
});

// Submit Form Action
$('#lgForm').on('submit', function () {
    submitForm();
});

function submitForm() {
    clearErrors();
    var type = $('#type option:selected').val();
    var type_title = $('#type option:selected').text();
    var network = $('#network option:selected').val();
    var location = $('#location option:selected').val();
    var location_name = $('#location option:selected').text();
    var target = $('#target').val();

    var tags = [
        '<div class="field is-grouped is-grouped-multiline">',
        '<div class="control">',
        '<div class="tags has-addons">',
        '<span class="tag lg-tag-loc-title">AS',
        network,
        '</span>',
        '<span class="tag lg-tag-loc">',
        location_name,
        '</span>',
        '</div>',
        '</div>',
        '<div class="control">',
        '<div class="tags has-addons">',
        '<span class="tag lg-tag-type-title">',
        type_title,
        '</span>',
        '<span class="tag lg-tag-type">',
        target,
        '</span>',
        '</div>',
        '</div>',
        '</div>'
    ].join('');

    $('#output').text("");
    $('#queryInfo').text("");
    $('#queryInfo').html(tags);

    $.ajax(
        {
            url: '/lg',
            type: 'POST',
            data: JSON.stringify(
                {
                    location: location,
                    type: type,
                    target: target
                }
            ),
            contentType: "application/json; charset=utf-8",
            context: document.body,
            readyState: prepResults(),
            statusCode: {
                200: function (response, code) {
                    response_html = [
                        '<br>',
                        '<div class="content">',
                        '<p class="query-output" id="output">',
                        response,
                        '</p>',
                        '</div>',
                    ];
                    progress.hide();
                    $('#output').html(response_html);
                },
                401: function (response, code) {
                    response_html = [
                        '<br>',
                        '<div class="notification is-danger">',
                        response.responseText,
                        '</div>',
                    ].join('');
                    clearPage();
                    target_error.show();
                    target_input.addClass('is-danger');
                    target_error.html(response_html);
                },
                405: function (response, code) {
                    response_html = [
                        '<br>',
                        '<div class="notification is-warning">',
                        response.responseText,
                        '</div>',
                    ].join('');
                    clearPage();
                    target_error.show();
                    target_input.addClass('is-warning');
                    target_error.html(response_html);
                },
                415: function (response, code) {
                    response_html = [
                        '<br>',
                        '<div class="notification is-danger">',
                        response.responseText,
                        '</div>',
                    ].join('');
                    clearPage();
                    target_error.show();
                    target_input.addClass('is-danger');
                    target_error.html(response_html);
                },
                429: function (response, code) {
                    clearPage();
                    $("#ratelimit").addClass("is-active");
                },
                504: function (response, code) {
                    response_html = [
                        '<br>',
                        '<div class="notification is-danger">',
                        response.responseText,
                        '</div>',
                    ].join('');
                    clearPage();
                    target_error.show();
                    target_error.html(response_html);
                }
            }
        }
    );
}
