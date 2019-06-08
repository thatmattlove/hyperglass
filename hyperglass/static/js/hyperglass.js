// Get the list of routers for the selected Network

var progress = ($('#progress'));
var resultsbox = ($('#resultsbox'));
var ipprefix_error = ($('#ipprefix_error'));
var ipprefix_input = ($('#ipprefix'));
adjustDropdowns();
clearPage();

// Bulma Toggable Dropdown - help text
let dropdown = document.querySelector('#help-dropdown');
dropdown.addEventListener('click', function(event) {
  event.stopPropagation();
  dropdown.classList.toggle('is-active');
});

function bgpHelpASPath() {
  $("#help_bgp_aspath").addClass("is-active");
}

function bgpHelpCommunity() {
  $("#help_bgp_community").addClass("is-active");
}

function closeModal() {
  $(".modal").removeClass("is-active");
}

// Adjust behavior of help text dropdown based on device screen size
function adjustHeight() {
  var actual_width = window.innerWidth;
  if (actual_width < 1024) {
    $('#help-dropdown').removeClass('is-right');
    $('.lg-help').addClass('lg-help-mobile').removeClass('lg-help');
  }
}

function adjustDropdowns() {
  var actual_width = window.innerWidth;
  if (actual_width < 1024) {
    $('#lg-netlocdropdown').removeClass('has-addons').removeClass('has-addons-centered').addClass('is-grouped').addClass('is-grouped-centered').addClass('is-grouped-multiline');
    $('#network').css('width', actual_width * 0.85);
    $('#router').css('width', actual_width * 0.85);
  }
}

function clearErrors() {
  progress.hide();
  ipprefix_error.hide();
  if (ipprefix_input.hasClass("is-warning")) {
    ipprefix_input.removeClass("is-warning");
  };
  if (ipprefix_input.hasClass("is-danger")) {
    ipprefix_input.removeClass("is-danger");
  };
}

function clearPage() {
  progress.hide();
  resultsbox.hide();
  ipprefix_error.hide();
  if (ipprefix_input.hasClass("is-warning")) {
    ipprefix_input.removeClass("is-warning");
  };
  if (ipprefix_input.hasClass("is-danger")) {
    ipprefix_input.removeClass("is-danger");
  };
}

function prepResults() {
  progress.show();
  resultsbox.show();
}

$(document).ready(function() {
  var defaultasn = $("#network").val();
  $.ajax({
    url: `/routers/${defaultasn}`,
    context: document.body,
    type: 'get',
    success: function(data) {
      selectedRouters = JSON.parse(data)
      console.log(selectedRouters)
      updateRouters(selectedRouters);
    },
    error: function(err) {
      console.log(err)
    }
  })
})

$('#network').on('change', () => {
  var asn = $("select[id=network").val()
  $('#router').children(":not(#text_location)").remove();
  $.ajax({
    url: `/routers/${asn}`,
    type: 'get',
    success: function(data) {
      cleanPage();
      updateRouters(JSON.parse(data));
    },
    error: function(err) {
      console.log(err)
    }
  })
})

function updateRouters(routers) {
  routers.forEach(function(r) {
    $('#router').append($("<option>").attr('value', r.location).text(r.display_name))
  })
}

// Submit Form Action
$('#lgForm').on('submit', function() {
  submitForm();
});

function submitForm() {
  clearErrors();
  // progress.hide();
  // ipprefix_error.hide();
  var cmd = $('#cmd option:selected').val();
  var cmdtitle = $('#cmd option:selected').text();
  var network = $('#network option:selected').val();
  var router = $('#router option:selected').val();
  var routername = $('#router option:selected').text();
  var ipprefix = $('#ipprefix').val();

  $('#output').text("");
  $('#queryInfo').text("");
  $('#queryInfo').html(`
    <div class="field is-grouped is-grouped-multiline">
      <div class="control">
        <div class="tags has-addons">
          <span class="tag lg-tag-loctitle">AS${network}</span>
          <span class="tag lg-tag-loc">${routername}</span>
        </div>
      </div>
      <div class="control">
        <div class="tags has-addons">
          <span class="tag lg-tag-cmdtitle">${cmdtitle}</span>
          <span class="tag lg-tag-cmd">${ipprefix}</span>
        </div>
      </div>
    </div>
`);

  $.ajax({
    url: `/lg`,
    type: 'POST',
    data: JSON.stringify({
      router: router,
      cmd: cmd,
      ipprefix: ipprefix
    }),
    contentType: "application/json; charset=utf-8",
    context: document.body,
    readyState: prepResults(),
    statusCode: {
      200: function(response, code) {
        progress.hide();
        $('#output').html(`<br><div class="content"><p class="query-output" id="output">${response}</p></div>`);
      },
      405: function(response, code) {
        clearPage();
        ipprefix_error.show()
        ipprefix_input.addClass('is-warning');
        ipprefix_error.html(`
          <br>
          <article class="message is-warning is-small" style="display: block;">
            <div class="message-header" style="display: block;">
              Input Not Allowed
            </div>
            <div id="error" style="display: block;" class="message-body">
              ${response.responseText}
            </div>
          </article>
          `);
      },
      415: function(response, code) {
        clearPage();
        ipprefix_error.show()
        ipprefix_input.addClass('is-danger');
        ipprefix_error.html(`
          <br>
          <article class="message is-danger is-small" style="display: block;">
            <div class="message-header" style="display: block;">
              Invalid Input
            </div>
            <div id="error" style="display: block;" class="message-body">
              ${response.responseText}
            </div>
          </article>
          `);
      },
      429: function(response, code) {
        clearPage();
        $("#ratelimit").addClass("is-active");
      }
    }
  })
}
