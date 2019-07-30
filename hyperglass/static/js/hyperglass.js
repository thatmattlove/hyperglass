// Get the list of locations for the selected Network

var progress = $("#progress");
var resultsbox = $("#resultsbox");
var target_error = $("#target_error");
var target_input = $("#target");
// adjustDropdowns();
clearPage();

$(".selection.dropdown").dropdown({
  fullTextSearch: true,
  match: "both",
  allowCategorySelection: true,
  ignoreCare: true
});

$("#type_bgp_route").popup({
  hoverable: true,
  variation: "wide",
  position: "right center",
  html: $("#bgpr_help_content").html()
});

$("#type_bgp_community").popup({
  hoverable: true,
  variation: "wide",
  position: "right center",
  html: $("#bgpc_help_content").html()
});

$("#type_bgp_aspath").popup({
  hoverable: true,
  variation: "wide",
  position: "right center",
  html: $("#bgpa_help_content").html()
});

$("#type_ping").popup({
  hoverable: true,
  variation: "wide",
  position: "right center",
  html: $("#ping_help_content").html()
});

$("#type_traceroute").popup({
  hoverable: true,
  variation: "wide",
  position: "right center",
  html: $("#traceroute_help_content").html()
});

// ClipboardJS Elements
var clip_button = document.getElementById("clip-button");
var clipboard = new ClipboardJS(clip_button);
clipboard.on("success", function (e) {
  $("#clip-button")
    .removeClass("copy link icon")
    .addClass("green check icon");
  e.clearSelection();
  setTimeout(function () {
    $("#clip-button")
      .removeClass("green check icon")
      .addClass("copy link icon");
  }, 800);
});
clipboard.on("error", function (e) {
  console.log(e);
});

function clearErrors() {
  $("#lgForm").removeClass("error");
  $("#lgForm").removeClass("warning");
  $("#lgForm > div.ui.message").html("").removeClass("error").addClass("hidden");
  $("#field-target").removeClass("error");
  $(".ui.fluid.icon.input").removeClass("loading");
}

function clearPage() {
  $(".ui.fluid.icon.input").removeClass("loading");
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

$(document).ready(function () {
  $('#lg-results').hide();
  $(".animsition").animsition({
    inClass: 'fade-in',
    outClass: 'fade-out',
    inDuration: 800,
    outDuration: 800,
    transition: function (url) { window.location.href = url; }
  });

  $('#lg-form').animsition('in');
});

$("#results_back").on("click", function () {
  $('#lg-results').animsition('out', $('#lg-form'), '#');
  $('#lg-results').hide();
  $('#lg-form').show();
  $('#lg-form').animsition('in');
})

// Submit Form Action
$("#lgForm").form().submit(function (event) {
  event.preventDefault();
  clearErrors();
  submitForm();
});

$("#submit_button").on("click", function () {
  clearErrors();
  submitForm();
})

function buildError(msgClass, msg) {
  var msgHtml = [
    '<div class="ui ',
    msgClass,
    ' message transition hidden>',
    '<i class="close icon"></i>',
    '<p>',
    msg,
    '</p>',
    '</div>'
  ].join("");
  return msgHtml;
}

function submitForm() {
  clearErrors();
  var query_type = $("#query_type").dropdown("get value");
  var query_type_title = $("#query_type").dropdown("get text");
  var location = $("#location").dropdown("get value");
  var location_name = $("#location").dropdown("get text");
  var target = $("#target").val();
  console.log(query_type);
  console.log(location);
  console.log(target);

  network = $("#" + location).val();

  var tags = [
    '<div class="ui label">',
    network,
    '<div class="detail">',
    location_name,
    "</div>",
    "</div>",
    '<div class="ui label">',
    query_type_title,
    '<div class="detail">',
    target,
    "</div>",
    "</div>"
  ].join("");

  $("#results_detail").html(tags);
  $(".ui.fluid.icon.input").addClass("loading");

  $.ajax({
    url: "/lg",
    type: "POST",
    data: JSON.stringify({
      location: location,
      query_type: query_type,
      target: target
    }),
    contentType: "application/json; charset=utf-8",
    context: document.body,
    statusCode: {
      200: function (response, code) {
        $('#lg-form').animsition('out', $('#lg-results'), '#');
        $('#lg-results').show();
        $('#lg-results').animsition('in');
        response_html = [
          '<pre>',
          response,
          "</pre>"
        ].join("");
        $(".ui.fluid.icon.input").removeClass("loading");
        $("#lg-results-segment").html(response_html);
      },
      401: function (response, code) {
        $("#lgForm").addClass("error");
        $("#lgForm > div.ui.hidden.message").html(response.responseText).addClass("error").removeClass("hidden");
        $("#field-target").addClass("error");
        $(".ui.fluid.icon.input").removeClass("loading");
      },
      405: function (response, code) {
        $("#lgForm").addClass("error");
        $("#lgForm > div.ui.hidden.message").html(response.responseText).addClass("error").removeClass("hidden");
        $("#field-target").addClass("error");
        $(".ui.fluid.icon.input").removeClass("loading");
      },
      415: function (response, code) {
        $("#lgForm").addClass("warning");
        $("#lgForm > div.ui.hidden.message").html(response.responseText).addClass("warning").removeClass("hidden");
        $(".ui.fluid.icon.input").removeClass("loading");
      },
      429: function (response, code) {
        $("#ratelimit").modal("show");
      },
      504: function (response, code) {
        $("#lgForm").addClass("error");
        $("#lgForm > div.ui.hidden.message").html(response.responseText).addClass("error").removeClass("hidden");
        $("#field-target").addClass("error");
        $(".ui.fluid.icon.input").removeClass("loading");
      }
    }
  });
};