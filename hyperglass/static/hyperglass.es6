// Module Imports
global.jQuery = require('jquery');
const $ = jQuery;
const Popper = require('popper.js');
const bootstrap = require('bootstrap');
const selectpicker = require('bootstrap-select');
const animsition = require('animsition');
const ClipboardJS = require('clipboard');

const status_refresh = '<i class="remixicon-refresh-line hg-menu-icon"></i>';

$('#location').selectpicker({
  liveSearchNormalize: true,
  style: '',
  styleBase: 'form-control',
  iconBase: '',
  tickIcon: 'remixicon-check-line',
});

$('#query_type').selectpicker({
  liveSearchNormalize: true,
  style: '',
  styleBase: 'form-control',
  iconBase: '',
  tickIcon: 'remixicon-check-line',
});

$(document).ready(() => {
  $('#hg-results').hide();
  $('.animsition').animsition({
    inClass: 'fade-in',
    outClass: 'fade-out',
    inDuration: 800,
    outDuration: 800,
    transition: (url) => { window.location.href = url; },
  });

  $('#hg-form').animsition('in');
});

$('#hg-back').click(() => {
  $('.hg-select').selectpicker('deselectAll');
  $('#hg-results').animsition('out', $('#hg-form'), '#');
  $('#hg-results').hide();
  $('#hg-form').show();
  $('#hg-form').animsition('in');
  $('#hg-accordion').empty();
});

const queryApp = (queryType, queryTypeName, locationList, target) => {
  let results_title = `${queryTypeName} Query for ${target}`;

  $('#hg-results-title').html(results_title);

  $('#hg-submit-icon').empty().removeClass('hg-loading').html('<i class="remixicon-search-line"></i>');

  $.each(locationList, (n, loc) => {
    let location_name = $(`#${loc}`).data('display-name');
    let network_name = $(`#${loc}`).data('netname');

    let contentHtml = `
    <div class="card" id="${loc}-output">
      <div class="card-header bg-light text-dark" id="${loc}-heading">
        <div class="float-right hg-status-container" id="${loc}-status-container">
          <button type="button" class="float-right btn btn-light btn-lg hg-menu-btn hg-status-btn" 
            data-location="${loc}" id="${loc}-status-btn" disabled>
          </button>
        </div>
        <button type="button" class="float-right btn btn-light btn-lg hg-menu-btn hg-copy-btn" 
          data-clipboard-target="#${loc}-text" id="${loc}-copy-btn" disabled>
          <i class="remixicon-file-copy-line hg-menu-icon hg-copy hg-copy-icon"></i>
        </button>
        <h2 class="mb-0" id="${loc}-heading-container">
          <button class="btn btn-link text-secondary" type="button" data-toggle="collapse" 
            data-target="#${loc}-content" aria-expanded="true" aria-controls="${loc}-content"
            id="${loc}-heading-text">
          </button>
        </h2>
      </div>
      <div class="collapse" id="${loc}-content" aria-labelledby="${loc}-heading" data-parent="#hg-accordion">
        <div class="card-body" id="${loc}-text">
        </div>
      </div>
    </div>
    `;

    if ($(`#${loc}-output`).length) {
      $(`#${loc}-output`).replaceWith(contentHtml);
    } else {
      $('#hg-accordion').append(contentHtml);
    }
    // let status_container = `<div class="float-left hg-status-container" id="${loc}-status-container"></div>`
    let status_loading = `<i id="${loc}-spinner" class="hg-menu-icon hg-status-icon remixicon-loader-4-line text-secondary"></i>`;

    // $(`#${loc}-heading-container`).prepend(status_container);
    $(`#${loc}-heading-text`).text(location_name);
    $(`#${loc}-status-container`)
      .addClass('hg-loading')
      .find('.hg-status-btn')
      .empty()
      .html(status_loading);

    const generateError = (errorClass, loc, text) => {
      let status_error = '<i class="hg-menu-icon hg-status-icon remixicon-alert-line"></i>';
      $(`#${loc}-heading`).removeClass('text-secondary bg-light').addClass(`bg-${errorClass}`);
      $(`#${loc}-heading-text`).removeClass('text-secondary');
      $(`#${loc}-heading`).find('.hg-menu-btn').removeClass('btn-light').addClass(`btn-${errorClass}`);
      $(`#${loc}-status-container`)
        .removeClass('hg-loading')
        .find('.hg-status-btn')
        .empty()
        .html(status_error);
      $(`#${loc}-text`).html(text);
    }

    $.ajax({
      url: '/lg',
      type: 'POST',
      data: JSON.stringify({
        location: loc,
        query_type: queryType,
        target: target,
      }),
      contentType: 'application/json; charset=utf-8',
      context: document.body,
      async: true,
      timeout: 15000,
    })
      .done((data, textStatus, jqXHR) => {
        let response_pre = `<pre>${jqXHR.responseText}</pre>`;
        let status_success = '<i class="hg-menu-icon hg-status-icon remixicon-check-line"></i>';
        $(`#${loc}-heading`).removeClass('text-secondary bg-light').addClass('bg-primary');
        $(`#${loc}-heading-text`).removeClass('text-secondary');
        $(`#${loc}-heading`).find('.hg-menu-btn').removeClass('btn-light').addClass('btn-primary');
        $(`#${loc}-status-container`)
          .removeClass('hg-loading')
          .find('.hg-status-btn')
          .empty()
          .html(status_success);
        $(`#${loc}-text`).empty().html(response_pre);
      })
      .fail((jqXHR, textStatus, errorThrown) => {
        let codes_danger = [401, 415, 500, 501, 503];
        let codes_warning = [405];
        if (textStatus === 'timeout') {
          let text = 'Request timed out.';
          let response_html = `<div class="alert alert-warning" role="alert">${text}</div>`;
          let tab_timeout = '<i class="remixicon-time-line"></i>';

          $(`#${loc}-heading`).removeClass('text-secondary bg-light').addClass('bg-warning');
          $(`#${loc}-heading-text`).removeClass('text-secondary');
          $(`#${loc}-status-container`).empty().removeClass('hg-loading').html(tab_timeout);
          $(`#${loc}-heading`).find('.hg-menu-btn').removeClass('btn-light').addClass('btn-warning');
          $(`#${loc}-text`).html(response_html);
        } else if (codes_danger.includes(jqXHR.status)) {
          generateError('danger', loc, jqXHR.responseText);
        } else if (codes_warning.includes(jqXHR.status)) {
          generateError('warning', loc, jqXHR.responseText);
        }
      })
      .always(() => {
        $(`#${loc}-status-btn`).removeAttr('disabled');
        $(`#${loc}-copy-btn`).removeAttr('disabled');
      });
    $(`#${locationList[0]}-content`).collapse('show');
  });
};

// Submit Form Action
$('#lgForm').submit((event) => {
  event.preventDefault();
  $('#hg-submit-icon').empty().html('<i class="remixicon-loader-4-line"></i>').addClass('hg-loading');
  let query_type = $("#query_type").val();
  let query_type_title = $(`#${query_type}`).data('display-name');
  let location = $('#location').val();
  let target = $('#target').val();
  queryApp(query_type, query_type_title, location, target);
  $('#hg-form').animsition('out', $('#hg-results'), '#');
  $('#hg-form').hide();
  $('#hg-results').show();
  $('#hg-results').animsition('in');
  $('#hg-submit-spinner').remove();
});

const clipboard = new ClipboardJS('.hg-copy-btn');
clipboard.on('success', (e) => {
  $(e.trigger).find('.hg-copy-icon').removeClass('remixicon-file-copy-line').addClass('remixicon-task-line');
  e.clearSelection();
  setTimeout(() => {
    $(e.trigger).find('.hg-copy-icon').removeClass('remixicon-task-line').addClass('remixicon-file-copy-line');
  }, 800);
});
clipboard.on('error', (e) => {
  console.log(e);
});

$('#hg-accordion').on('mouseenter', '.hg-status-btn', (e) => {
  $(e.currentTarget)
    .find('.hg-status-icon')
    .addClass('remixicon-repeat-line');
});

$('#hg-accordion').on('mouseleave', '.hg-status-btn', (e) => {
  $(e.currentTarget)
    .find('.hg-status-icon')
    .removeClass('remixicon-repeat-line');
});

$('#hg-accordion').on('click', '.hg-status-btn', (e) => {
  let loc_id = $(e.currentTarget).data('location');
  console.log(`Refreshing ${loc_id}`);
  let query_type = $('#query_type').val();
  let query_type_title = $(`#${query_type}`).data('display-name');
  let target = $('#target').val();
  queryApp(query_type, query_type_title, [loc_id,], target);
});
