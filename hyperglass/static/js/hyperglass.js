// Get the list of locations for the selected Network

var progress = ($('#progress'));
var resultsbox = ($('#resultsbox'));
var target_error = ($('#target_error'));
var target_input = ($('#target'));
adjustDropdowns();
clearPage();

// Bulma Toggable Dropdown - help text
let dropdown = document.querySelector('#help-dropdown');
dropdown.addEventListener('click', function(event) {
  event.stopPropagation();
  dropdown.classList.toggle('is-active');
});

var btn_copy = document.getElementById('btn-copy');
var clipboard = new ClipboardJS(btn_copy);
clipboard.on('success', function(e) {
    console.log(e);
    $('#btn-copy').addClass('is-success').addClass('is-outlined');
    $('#copy-icon').removeClass('icofont-ui-copy').addClass('icofont-check');
    setTimeout(function(){
      $('#btn-copy').removeClass('is-success').removeClass('is-outlined');
      $('#copy-icon').removeClass('icofont-check').addClass('icofont-ui-copy');
    }, 1000)
});
clipboard.on('error', function(e) {
    console.log(e);
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
    $('#location').css('width', actual_width * 0.85);
  }
}

function clearErrors() {
  progress.hide();
  target_error.hide();
  if (target_input.hasClass("is-warning")) {
    target_input.removeClass("is-warning");
  };
  if (target_input.hasClass("is-danger")) {
    target_input.removeClass("is-danger");
  };
}

function clearPage() {
  progress.hide();
  resultsbox.hide();
  target_error.hide();
  if (target_input.hasClass("is-warning")) {
    target_input.removeClass("is-warning");
  };
  if (target_input.hasClass("is-danger")) {
    target_input.removeClass("is-danger");
  };
}

function prepResults() {
  progress.show();
  resultsbox.show();
}

$(document).ready(function() {
  var defaultasn = $("#network").val();
  $.ajax({
    url: `/locations/${defaultasn}`,
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
  $('#location').children(":not(#text_location)").remove();
  $.ajax({
    url: `/locations/${asn}`,
    type: 'get',
    success: function(data) {
      clearPage();
      updateRouters(JSON.parse(data));
    },
    error: function(err) {
      console.log(err)
    }
  })
})

function updateRouters(locations) {
  locations.forEach(function(r) {
    $('#location').append($("<option>").attr('value', r.location).text(r.display_name))
  })
}

// Submit Form Action
$('#lgForm').on('submit', function() {
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

  $('#output').text("");
  $('#queryInfo').text("");
  $('#queryInfo').html(`
    <div class="field is-grouped is-grouped-multiline">
      <div class="control">
        <div class="tags has-addons">
          <span class="tag lg-tag-loc-title">AS${network}</span>
          <span class="tag lg-tag-loc">${location_name}</span>
        </div>
      </div>
      <div class="control">
        <div class="tags has-addons">
          <span class="tag lg-tag-type-title">${type_title}</span>
          <span class="tag lg-tag-type">${target}</span>
        </div>
      </div>
    </div>
`);

  $.ajax({
    url: `/lg`,
    type: 'POST',
    data: JSON.stringify({
      location: location,
      type: type,
      target: target
    }),
    contentType: "application/json; charset=utf-8",
    context: document.body,
    readyState: prepResults(),
    statusCode: {
      200: function(response, code) {
        progress.hide();
        $('#output').html(`<br><div class="content"><p class="query-output" id="output">${response}</p></div>`);
      },
      401: function(response, code) {
        clearPage();
        target_error.show()
        target_input.addClass('is-danger');
        target_error.html(`
          <br>
          <article class="message is-danger is-small" style="display: block;">
            <div class="message-header" style="display: block;">
              Authentication Error
            </div>
            <div id="error" style="display: block;" class="message-body">
              ${response.responseText}
            </div>
          </article>
          `);
        },
      405: function(response, code) {
        clearPage();
        target_error.show()
        target_input.addClass('is-warning');
        target_error.html(`
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
        target_error.show()
        target_input.addClass('is-danger');
        target_error.html(`
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
