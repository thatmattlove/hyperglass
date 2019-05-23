// Get the list of routers for the selected Network

var progress = ($('#progress'));
var resultsbox = ($('#resultsbox'));
resultsbox.hide();
progress.hide();
adjustDropdowns();

// Bulma Toggable Dropdown - help text
let dropdown = document.querySelector('#help-dropdown');
dropdown.addEventListener('click', function(event) {
  event.stopPropagation();
  dropdown.classList.toggle('is-active');
});

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
      updateRouters(JSON.parse(data));

    },
    error: function(err) {
      console.log(err)
    }
  })
})

function updateRouters(routers) {
  routers.forEach(function(r) {
    $('#router').append($("<option>").attr('value', r.location).attr('type', r.type).text(r.display_name))
  })
}

// Submit Form Action
$('#lgForm').on('submit', function() {

  // Regex to match any IPv4 host address or CIDR prefix
  var ipv4_any = new RegExp('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(/(3[0-2]|2[0-9]|1[0-9]|[0-9]))?$');
  // Regex to match any IPv6 host address or CIDR prefix
  var ipv6_any = new RegExp('^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(\/((1(1[0-9]|2[0-8]))|([0-9][0-9])|([0-9])))?$');
  // Regex to match an IPv4 CIDR prefix only (excludes a host address)
  var ipv4_cidr = new RegExp('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(3[0-2]|2[0-9]|1[0-9]|[0-9])?$');
  // Regex to match an IPv6 CIDR prefix only (excludes a host address)
  var ipv6_cidr = new RegExp('^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\/((1(1[0-9]|2[0-8]))|([0-9][0-9])|([0-9]))?$');
  var ipv6_host = new RegExp('^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))?$')
  var cmd = $('#cmd option:selected').val();
  var routerType = $('#router option:selected').attr('type');
  var ipprefix = $('#ipprefix').val();
  var router = $('#router option:selected').val();
  // Filters selectedRouters JSON object to only the selected router, returns all attributes passed from Flask's `get_routers`
  var routersJson = selectedRouters.filter(r => r.location === router);
  // Filters above to value of `requiresIP6Cidr` as passed from Flask's `get_routers`
  var requiresIP6Cidr = routersJson[0].requiresIP6Cidr

  // If BGP lookup, and lookup is an IPv6 address *without* CIDR prefix (e.g. 2001:db8::1, NOT 2001:db8::/48), and requiresIP6Cidr
  // is true, show an error.
  $('#ipprefix_error').hide()
  $('#ipprefix').removeClass('is-danger')
  if (cmd == 'bgp_route' && ipv6_host.test(ipprefix) == true && requiresIP6Cidr == true) {
    console.log('matched requires ipv6 cidr')
    $('#ipprefix_error').show()
    $('#ipprefix').addClass('is-danger')
    $('#ipprefix_error').html(`
      <br>
      <article class="message is-danger is-small" style="display: block;">
        <div class="message-header" style="display: block;">
          Invalid Input
        </div>
        <div id="error" style="display: block;" class="message-body">
          This router requires IPv6 BGP lookups to be and exact match in CIDR notation.
        </div>
      </article>
      `);
  }
  // If ping, and lookup is an IPv4 address *with* CIDR prefix (e.g. 192.0.2.0/24, NOT 192.0.2.1), show an error.
  else if (ipv4_cidr.test(ipprefix) == true && cmd == 'ping') {
    $('#ipprefix_error').show()
    $('#ipprefix').addClass('is-danger')
    $('#ipprefix_error').html(`
      <br>
      <article class="message is-danger is-small" style="display: block;">
        <div class="message-header" style="display: block;">
          Invalid Input
        </div>
        <div id="error" style="display: block;" class="message-body">
          <code>ping</code> does not allow network masks.
        </div>
      </article>
      `);
  }
  // If traceroute, and lookup is an IPv4 address *with* CIDR prefix (e.g. 192.0.2.0/24, NOT 192.0.2.1), show an error.
  else if (ipv4_cidr.test(ipprefix) == true && cmd == 'traceroute') {
    $('#ipprefix_error').show()
    $('#ipprefix').addClass('is-danger')
    $('#ipprefix_error').html(`
      <br>
      <article class="message is-danger is-small" style="display: block;">
        <div class="message-header" style="display: block;">
          Invalid Input
        </div>
        <div id="error" style="display: block;" class="message-body">
          <code>traceroute</code> does not allow network masks.
        </div>
      </article>
      `);
  }
  // If ping, and lookup is an IPv6 address *with* CIDR prefix (e.g. 2001:db8::/48, NOT 2001:db8::1), show an error.
  else if (ipv6_cidr.test(ipprefix) == true && cmd == 'ping') {
    $('#ipprefix_error').show()
    $('#ipprefix').addClass('is-danger')
    $('#ipprefix_error').html(`
      <br>
      <article class="message is-danger is-small" style="display: block;">
        <div class="message-header" style="display: block;">
          Invalid Input
        </div>
        <div id="error" style="display: block;" class="message-body">
          <code>ping</code> does not allow network masks.
        </div>
      </article>
      `);
  }
  // If traceroute, and lookup is an IPv6 address *with* CIDR prefix (e.g. 2001:db8::/48, NOT 2001:db8::1), show an error.
  else if (ipv6_cidr.test(ipprefix) == true && cmd == 'traceroute') {
    $('#ipprefix_error').show()
    $('#ipprefix').addClass('is-danger')
    $('#ipprefix_error').html(`
      <br>
      <article class="message is-danger is-small" style="display: block;">
        <div class="message-header" style="display: block;">
          Invalid Input
        </div>
        <div id="error" style="display: block;" class="message-body">
          <code>traceroute</code> does not allow network masks.
        </div>
      </article>
      `);
  } else submitForm();
});

var submitForm = function() {
  progress.hide();
  var cmd = $('#cmd option:selected').val();
  var cmdtitle = cmd.replace('_', ': ');
  var network = $('#network option:selected').val();
  var router = $('#router option:selected').val();
  var routername = $('#router option:selected').text();
  var ipprefix = $('#ipprefix').val();
  var routerType = $('#router option:selected').attr('type');

  $('#output').text("")
  $('#queryInfo').text("")

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
`)

  /////////////////////////////////////////////////////////////

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
    readyState: resultsbox.show() && progress.show(),
    statusCode: {
      200: function(response, code) {
        progress.hide();
        $('#output').html(`<br><div class="content"><p class="query-output" id="output">${response}</p></div>`);
      },
      405: function(response, code) {
        progress.hide();
        $('#ipprefix').addClass('is-warning');
        $('#output').html(`<br><div class="notification is-warning" id="output">${response.responseText}</div>`);
      },
      415: function(response, code) {
        progress.hide();
        $('#ipprefix').addClass('is-danger');
        $('#output').html(`<br><div class="notification is-danger" id="output">${response.responseText}</div>`);
      },
      429: function(response, code) {
        progress.hide();
        $("#ratelimit").addClass("is-active");
      }
    }
  })
}
