// Module Imports
global.jQuery = require('jquery');
const $ = jQuery;
const Popper = require('popper.js');
const bootstrap = require('bootstrap');
const selectpicker = require('bootstrap-select');
const animsition = require('animsition');
const ClipboardJS = require('clipboard');
const frontEndConfig = require('./frontend.json');

const cfgGeneral = frontEndConfig.general;
const inputMessages = frontEndConfig.messages;
const pageContainer = $('#hg-page-container');
const formContainer = $('#hg-form');
const titleColumn = $('#hg-title-col');
const queryLocation = $('#location');
const queryType = $('#query_type');
const queryTarget = $('#query_target');
const queryTargetAppend = $('#hg-target-append');
const submitIcon = $('#hg-submit-icon');
const resultsContainer = $('#hg-results');
const resultsAccordion = $('#hg-accordion');
const resultsColumn = resultsAccordion.parent();
const backButton = $('#hg-back-btn');
const footerHelpBtn = $('#hg-footer-help-btn');
const footerTermsBtn = $('#hg-footer-terms-btn');
const footerCreditBtn = $('#hg-footer-credit-btn');
const footerPopoverTemplate = '<div class="popover mw-sm-75 mw-md-50 mw-lg-25" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>';

let bsBlurState = false;

class InputInvalid extends Error {
  constructor(validationMsg, invalidField, fieldContainer) {
    super(validationMsg, invalidField, fieldContainer);
    this.name = this.constructor.name;
    this.message = validationMsg;
    this.field = invalidField;
    this.container = fieldContainer;
  }
}

const swapSpacing = (goTo) => {
  if (goTo === 'form') {
    pageContainer.removeClass('px-0 px-md-3');
    resultsColumn.removeClass('px-0');
    titleColumn.removeClass('text-center');
  } else if (goTo === 'results') {
    pageContainer.addClass('px-0 px-md-3');
    resultsColumn.addClass('px-0');
    titleColumn.addClass('text-left');
  }
};

const resetResults = () => {
  queryLocation.selectpicker('deselectAll');
  queryLocation.selectpicker('val', '');
  queryType.selectpicker('val', '');
  queryTarget.val('');
  resultsContainer.animsition('out', formContainer, '#');
  resultsContainer.hide();
  $('.hg-info-btn').remove();
  swapSpacing('form');
  formContainer.show();
  formContainer.animsition('in');
  backButton.addClass('d-none');
  resultsAccordion.empty();
};

const reloadPage = () => {
  queryLocation.selectpicker('deselectAll');
  queryLocation.selectpicker('val', '');
  queryType.selectpicker('val', '');
  queryTarget.val('');
  resultsAccordion.empty();
};

/* Removed liveSearch until bootstrap-select mergest the fix for the mobile keyboard opening issue.
   Basically, any time an option is selected on a mobile device, the keyboard pops open which is
   super annoying. */
queryLocation.selectpicker({
  iconBase: '',
  liveSearch: false,
  selectedTextFormat: 'count > 2',
  style: '',
  styleBase: 'form-control',
  tickIcon: 'remixicon-check-line',
}).nextAll('.dropdown-menu.show').on('focus', '.bs-searchbox input', (e) => {
  $(e.currentTarget).blur();
  bsBlurState = true;
}).on('hidden.bs.select', (e) => {
  $(e.currentTarget).nextAll('.dropdown-menu.show').find('input').blur();
});

queryType.selectpicker({
  iconBase: '',
  liveSearch: false,
  style: '',
  styleBase: 'form-control',
}).on('hidden.bs.select', (e) => {
  $(e.currentTarget).nextAll('.form-control.dropdown-toggle').blur();
});

footerTermsBtn.popover({
  html: true,
  trigger: 'manual',
  template: footerPopoverTemplate,
  placement: 'top',
  content: $('#hg-footer-terms-html').html(),
}).on('click', (e) => {
  $(e.currentTarget).popover('toggle');
}).on('focusout', (e) => {
  $(e.currentTarget).popover('hide');
});

footerHelpBtn.popover({
  html: true,
  trigger: 'manual',
  placement: 'top',
  template: footerPopoverTemplate,
  content: $('#hg-footer-help-html').html(),
}).on('click', (e) => {
  $(e.currentTarget).popover('toggle');
}).on('focusout', (e) => {
  $(e.currentTarget).popover('hide');
});

footerCreditBtn.popover({
  html: true,
  trigger: 'manual',
  placement: 'top',
  title: $('#hg-footer-credit-title').html(),
  content: $('#hg-footer-credit-content').html(),
  template: footerPopoverTemplate,
}).on('click', (e) => {
  $(e.currentTarget).popover('toggle');
}).on('focusout', (e) => {
  $(e.currentTarget).popover('hide');
});

titleColumn.on('click', (e) => {
  window.location = $(e.currentTarget).data('href');
  return false;
});

$(document).ready(() => {
  reloadPage();
  resultsContainer.hide();
  $('#hg-ratelimit-query').modal('hide');
  $('.animsition').animsition({
    inClass: 'fade-in',
    outClass: 'fade-out',
    inDuration: 400,
    outDuration: 400,
    transition: (url) => { window.location.href = url; },
  });
  formContainer.animsition('in');
});

const supportedBtn = qt => `<button class="btn btn-secondary hg-info-btn" id="hg-info-btn-${qt}" data-hg-type="${qt}" type="button"><div id="hg-info-icon-${qt}"><i class="remixicon-information-line"></i></div></button>`;

queryType.on('changed.bs.select', () => {
  const queryTypeId = queryType.val();
  const queryTypeBtn = $('.hg-info-btn');
  if ((queryTypeId === 'bgp_community') || (queryTypeId === 'bgp_aspath')) {
    queryTypeBtn.remove();
    queryTargetAppend.prepend(supportedBtn(queryTypeId));
  } else {
    queryTypeBtn.remove();
  }
});

queryTargetAppend.on('click', '.hg-info-btn', () => {
  const queryTypeId = $('.hg-info-btn').data('hg-type');
  $(`#hg-info-${queryTypeId}`).modal('show');
});

const queryApp = (queryType, queryTypeName, locationList, queryTarget) => {
  const resultsTitle = `${queryTypeName} Query for ${queryTarget}`;

  $('#hg-results-title').html(resultsTitle);

  submitIcon.empty().removeClass('hg-loading').html('<i class="remixicon-search-line"></i>');

  $.each(locationList, (n, loc) => {
    const locationName = $(`#${loc}`).data('display-name');
    const networkName = $(`#${loc}`).data('netname');

    const contentHtml = `
    <div class="card" id="${loc}-output">
      <div class="card-header bg-overlay" id="${loc}-heading">
        <div class="float-right hg-status-container" id="${loc}-status-container">
          <button type="button" class="float-right btn btn-loading btn-lg hg-menu-btn hg-status-btn" 
            data-location="${loc}" id="${loc}-status-btn" disabled>
          </button>
        </div>
        <button type="button" class="float-right btn btn-loading btn-lg hg-menu-btn hg-copy-btn" 
          data-clipboard-target="#${loc}-text" id="${loc}-copy-btn" disabled>
          <i class="remixicon-checkbox-multiple-blank-line hg-menu-icon hg-copy hg-copy-icon"></i>
        </button>
        <h2 class="mb-0" id="${loc}-heading-container">
          <button class="btn btn-link" type="button" data-toggle="collapse" 
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
    const iconLoading = `<i id="${loc}-spinner" class="hg-menu-icon hg-status-icon remixicon-loader-4-line text-secondary"></i>`;

    $(`#${loc}-heading-text`).text(locationName);
    $(`#${loc}-status-container`)
      .addClass('hg-loading')
      .find('.hg-status-btn')
      .empty()
      .html(iconLoading);

    const generateError = (errorClass, locError, text) => {
      const iconError = '<i class="hg-menu-icon hg-status-icon remixicon-alert-line"></i>';
      $(`#${locError}-heading`).removeClass('bg-overlay').addClass(`bg-${errorClass}`);
      $(`#${locError}-heading`).find('.hg-menu-btn').removeClass('btn-loading').addClass(`btn-${errorClass}`);
      $(`#${locError}-status-container`)
        .removeClass('hg-loading')
        .find('.hg-status-btn')
        .empty()
        .html(iconError)
        .addClass('hg-done');
      $(`#${locError}-text`).html(text);
    };

    const timeoutError = (locError, text) => {
      const iconTimeout = '<i class="remixicon-time-line"></i>';
      $(`#${locError}-heading`).removeClass('bg-overlay').addClass('bg-warning');
      $(`#${locError}-heading`).find('.hg-menu-btn').removeClass('btn-loading').addClass('btn-warning');
      $(`#${locError}-status-container`).removeClass('hg-loading').find('.hg-status-btn').empty().html(iconTimeout).addClass('hg-done');
      $(`#${locError}-text`).empty().html(text);
    };

    $.ajax({
      url: '/query',
      method: 'POST',
      data: JSON.stringify({
        location: loc,
        query_type: queryType,
        target: queryTarget,
        response_format: 'html',
      }),
      contentType: 'application/json; charset=utf-8',
      context: document.body,
      async: true,
      timeout: cfgGeneral.request_timeout * 1000,
    })
      .done((data, textStatus, jqXHR) => {
        const displayHtml = `<pre>${data.output}</pre>`;
        const iconSuccess = '<i class="hg-menu-icon hg-status-icon remixicon-check-line"></i>';
        $(`#${loc}-heading`).removeClass('bg-overlay').addClass('bg-primary');
        $(`#${loc}-heading`).find('.hg-menu-btn').removeClass('btn-loading').addClass('btn-primary');
        $(`#${loc}-status-container`)
          .removeClass('hg-loading')
          .find('.hg-status-btn')
          .empty()
          .html(iconSuccess)
          .addClass('hg-done');
        $(`#${loc}-text`).empty().html(displayHtml);
      })
      .fail((jqXHR, textStatus, errorThrown) => {
        const codesDanger = [401, 415, 501, 503, 504];
        const codesWarning = [405];
        if (textStatus === 'timeout') {
          timeoutError(loc, inputMessages.request_timeout);
        } else if (jqXHR.status === 500 && textStatus !== 'timeout') {
          timeoutError(loc, inputMessages.request_timeout);
        } else if (codesDanger.includes(jqXHR.status)) {
          generateError('danger', loc, jqXHR.responseJSON.output);
        } else if (codesWarning.includes(jqXHR.status)) {
          generateError('warning', loc, jqXHR.responseJSON.output);
        } else if (jqXHR.status === 429) {
          resetResults();
          $('#hg-ratelimit-query').modal('show');
        }
      })
      .always(() => {
        $(`#${loc}-status-btn`).removeAttr('disabled');
        $(`#${loc}-copy-btn`).removeAttr('disabled');
      });
    $(`#${locationList[0]}-content`).collapse('show');
  });
};

$(document).on('InvalidInputEvent', (e, domField) => {
  const errorField = $(domField);
  if (errorField.hasClass('is-invalid')) {
    errorField.on('keyup', () => {
      errorField.removeClass('is-invalid');
      errorField.nextAll('.invalid-feedback').remove();
    });
  }
});


// Submit Form Action
$('#lgForm').on('submit', (e) => {
  e.preventDefault();
  submitIcon.empty().html('<i class="remixicon-loader-4-line"></i>').addClass('hg-loading');
  const queryType = $('#query_type').val();
  const queryLocation = $('#location').val();
  const queryTarget = $('#query_target').val();

  try {
    // message, thing to circle in red, place to put error text
    if (!queryTarget) {
      const queryTargetContainer = $('#query_target');
      throw new InputInvalid(inputMessages.no_input, queryTargetContainer, queryTargetContainer.parent());
    }
    if (!queryType) {
      const queryTypeContainer = $('#query_type').next('.dropdown-toggle');
      throw new InputInvalid(inputMessages.no_query_type, queryTypeContainer, queryTypeContainer.parent());
    }
    if (queryLocation === undefined || queryLocation.length === 0) {
      const queryLocationContainer = $('#location').next('.dropdown-toggle');
      throw new InputInvalid(inputMessages.no_location, queryLocationContainer, queryLocationContainer.parent());
    }
  } catch (err) {
    err.field.addClass('is-invalid');
    err.container.append(`<div class="invalid-feedback px-1">${err.message}</div>`);
    submitIcon.empty().removeClass('hg-loading').html('<i class="remixicon-search-line"></i>');
    $(document).trigger('InvalidInputEvent', err.field);
    return false;
  }
  const queryTypeTitle = $(`#${queryType}`).data('display-name');
  queryApp(queryType, queryTypeTitle, queryLocation, queryTarget);
  $('#hg-form').animsition('out', $('#hg-results'), '#');
  $('#hg-form').hide();
  swapSpacing('results');
  $('#hg-results').show();
  $('#hg-results').animsition('in');
  $('#hg-submit-spinner').remove();
  $('#hg-back-btn').removeClass('d-none');
  $('#hg-back-btn').animsition('in');
});

$('#hg-back-btn').click(() => {
  resetResults();
});

const clipboard = new ClipboardJS('.hg-copy-btn');
clipboard.on('success', (e) => {
  const copyIcon = $(e.trigger).find('.hg-copy-icon');
  copyIcon.removeClass('remixicon-checkbox-multiple-blank-line').addClass('remixicon-checkbox-multiple-line');
  e.clearSelection();
  setTimeout(() => {
    copyIcon.removeClass('remixicon-checkbox-multiple-line').addClass('remixicon-checkbox-multiple-blank-line');
  }, 800);
});
clipboard.on('error', (e) => {
  console.log(e);
});

$('#hg-accordion').on('mouseenter', '.hg-done', (e) => {
  $(e.currentTarget)
    .find('.hg-status-icon')
    .addClass('remixicon-repeat-line');
});

$('#hg-accordion').on('mouseleave', '.hg-done', (e) => {
  $(e.currentTarget)
    .find('.hg-status-icon')
    .removeClass('remixicon-repeat-line');
});

$('#hg-accordion').on('click', '.hg-done', (e) => {
  const thisLocation = $(e.currentTarget).data('location');
  console.log(`Refreshing ${thisLocation}`);
  const queryType = $('#query_type').val();
  const queryTypeTitle = $(`#${queryType}`).data('display-name');
  const queryTarget = $('#query_target').val();


  queryApp(queryType, queryTypeTitle, [thisLocation,], queryTarget);
});

$('#hg-ratelimit-query').on('shown.bs.modal', () => {
  $('#hg-ratelimit-query').trigger('focus');
});

$('#hg-ratelimit-query').find('btn').on('click', () => {
  $('#hg-ratelimit-query').modal('hide');
});

// Cheap hack for mobile keyboard popping up on a multiple select with live search - see bootstrap-select #1511
// $('.bs-searchbox.form-control').on('focus', () => {
//   if (!bsBlurState) {
//     console.log('matched cheap hack');
//     $(this).blur();
//     bsBlurState = true;
//   }
// });
