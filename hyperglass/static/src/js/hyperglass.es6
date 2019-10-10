// Module Imports
import format from '../node_modules/string-format';
import jQuery from '../node_modules/jquery';
import ClipboardJS from '../node_modules/clipboard';

// Project Imports
import {
  footerPopoverTemplate,
  feedbackInvalid,
  supportedBtn,
  vrfSelect,
  vrfOption,
} from './components.es6';
import { InputInvalid, FrontEndError } from './errors.es6';
import {
  swapSpacing, resetResults, reloadPage, findIntersection,
} from './util.es6';
import { queryApp } from './query.es6';

// JSON Config Import
import hgConf from './frontend.json';

// string-format config
format.extend(String.prototype, {});

const $ = jQuery;

const lgForm = $('#lgForm');
const vrfContainer = $('#hg-container-vrf');
const queryLocation = $('#location');
const queryType = $('#query_type');
const queryTargetAppend = $('#hg-target-append');
const submitIcon = $('#hg-submit-icon');

/* Removed liveSearch until bootstrap-select merges the fix for the mobile keyboard opening issue.
   Basically, any time an option is selected on a mobile device, the keyboard pops open which is
   super annoying. */
queryLocation.selectpicker({
  iconBase: '',
  liveSearch: false,
  selectedTextFormat: 'count > 2',
  style: '',
  styleBase: 'form-control',
  tickIcon: 'remixicon-check-line',
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

$('#hg-footer-terms-btn').popover({
  html: true,
  trigger: 'manual',
  template: footerPopoverTemplate(),
  placement: 'top',
  content: $('#hg-footer-terms-html').html(),
}).on('click', (e) => {
  $(e.currentTarget).popover('toggle');
}).on('focusout', (e) => {
  $(e.currentTarget).popover('hide');
});

$('#hg-footer-help-btn').popover({
  html: true,
  trigger: 'manual',
  placement: 'top',
  template: footerPopoverTemplate(),
  content: $('#hg-footer-help-html').html(),
}).on('click', (e) => {
  $(e.currentTarget).popover('toggle');
}).on('focusout', (e) => {
  $(e.currentTarget).popover('hide');
});

$('#hg-footer-credit-btn').popover({
  html: true,
  trigger: 'manual',
  placement: 'top',
  title: $('#hg-footer-credit-title').html(),
  content: $('#hg-footer-credit-content').html(),
  template: footerPopoverTemplate(),
}).on('click', (e) => {
  $(e.currentTarget).popover('toggle');
}).on('focusout', (e) => {
  $(e.currentTarget).popover('hide');
});

$(document).ready(() => {
  reloadPage();
  $('#hg-results').hide();
  $('#hg-ratelimit-query').modal('hide');
  if (location.pathname === '/') {
    $('.animsition').animsition({
      inClass: 'fade-in',
      outClass: 'fade-out',
      inDuration: 400,
      outDuration: 400,
      transition: (url) => { window.location.href = url; },
    });
    $('#hg-form').animsition('in');
  }
});

queryType.on('changed.bs.select', (e) => {
  const field = $(e.currentTarget);
  const queryTypeId = field.val();
  const queryTypeBtn = $('.hg-info-btn');

  if (field.next('button').hasClass('is-invalid')) {
    field.next('button').removeClass('is-invalid');
    field.nextAll('.invalid-feedback').remove();
  }
  if ((queryTypeId === 'bgp_community') || (queryTypeId === 'bgp_aspath')) {
    queryTypeBtn.remove();
    queryTargetAppend.prepend(supportedBtn(queryTypeId));
  } else {
    queryTypeBtn.remove();
  }
});

queryLocation.on('changed.bs.select', (e, clickedIndex, isSelected, previousValue) => {
  const field = $(e.currentTarget);
  if (field.next('button').hasClass('is-invalid')) {
    field.next('button').removeClass('is-invalid');
    field.nextAll('.invalid-feedback').remove();
  }
  vrfContainer.empty().removeClass('col');
  const queryLocationIds = field.val();
  if (Array.isArray(queryLocationIds) && (queryLocationIds.length)) {
    const queryLocationNet = field[0][clickedIndex].dataset.netname;
    const selectedVrfs = () => {
      const allVrfs = [];
      $.each(queryLocationIds, (i, loc) => {
        const locVrfs = hgConf.networks[queryLocationNet][loc].vrfs;
        allVrfs.push(new Set(locVrfs));
      });
      return allVrfs;
    };
    const intersectingVrfs = Array.from(findIntersection(...selectedVrfs()));
    // Add the VRF select element
    if (vrfContainer.find('#query_vrf').length === 0) {
      vrfContainer.addClass('col').html(vrfSelect(hgConf.config.branding.text.vrf));
    }
    // Build the select options for each VRF in array
    const vrfHtmlList = [];
    $.each(intersectingVrfs, (i, vrf) => {
      vrfHtmlList.push(vrfOption(vrf));
    });
    // Add the options to the VRF select element, enable it, initialize Bootstrap Select
    vrfContainer.find('#query_vrf').html(vrfHtmlList.join('')).removeAttr('disabled').selectpicker({
      iconBase: '',
      liveSearch: false,
      style: '',
      styleBase: 'form-control',
    });
    if (intersectingVrfs.length === 0) {
      vrfContainer.find('#query_vrf').selectpicker('destroy');
      vrfContainer.find('#query_vrf').prop('title', hgConf.config.messages.no_matching_vrfs).prop('disabled', true);
      vrfContainer.find('#query_vrf').selectpicker({
        iconBase: '',
        liveSearch: false,
        style: '',
        styleBase: 'form-control',
      });
    }
  }
});

queryTargetAppend.on('click', '.hg-info-btn', () => {
  const queryTypeId = $('.hg-info-btn').data('hg-type');
  $(`#hg-info-${queryTypeId}`).modal('show');
});

$('#hg-row-2').find('#query_vrf').on('hidden.bs.select', (e) => {
  $(e.currentTarget).nextAll('.form-control.dropdown-toggle').blur();
});

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
lgForm.on('submit', (e) => {
  e.preventDefault();
  submitIcon.empty().html('<i class="remixicon-loader-4-line"></i>').addClass('hg-loading');
  const queryType = $('#query_type').val() || '';
  const queryTarget = $('#query_target').val() || '';
  const queryVrf = $('#query_vrf').val() || hgConf.networks.default_vrf.display_name;
  let queryLocation = $('#location').val() || [];
  if (!Array.isArray(queryLocation)) {
    queryLocation = new Array(queryLocation);
  }

  try {
    /*
      InvalidInput event positional arguments:
        1: error message to display
        2: thing to circle in red
        3: place to put error message
    */
    if (!queryTarget) {
      const msgVars = { field: hgConf.config.branding.text.query_target };
      throw new InputInvalid(
        hgConf.config.messages.no_input.format(msgVars),
        $('#query_target'),
        $('#query_target').parent(),
      );
    }
    if (!queryType) {
      const msgVars = { field: hgConf.config.branding.text.query_type };
      throw new InputInvalid(
        hgConf.config.messages.no_input.format(msgVars),
        $('#query_type').next('.dropdown-toggle'),
        $('#query_type').next('.dropdown-toggle').parent(),
      );
    }
    if (queryLocation === undefined || queryLocation.length === 0) {
      const msgVars = { field: hgConf.config.branding.text.query_location };
      throw new InputInvalid(
        hgConf.config.messages.no_input.format(msgVars),
        $('#location').next('.dropdown-toggle'),
        $('#location').next('.dropdown-toggle').parent(),
      );
    }
  } catch (err) {
    $(err.field).addClass('is-invalid');
    $(err.container).find('.invalid-feedback').remove();
    $(err.container).append(feedbackInvalid(err.message));
    submitIcon.empty().removeClass('hg-loading').html('<i class="remixicon-search-line"></i>');
    $(document).trigger('InvalidInputEvent', err.field);
    return false;
  }
  const queryTypeTitle = $(`#${queryType}`).data('display-name');
  try {
    try {
      queryApp(
        queryType,
        queryTypeTitle,
        queryLocation,
        queryTarget,
        queryVrf,
      );
    } catch (err) {
      console.log(err);
      throw new FrontEndError(
        hgConf.config.messages.general,
        lgForm,
      );
    }
  } catch (err) {
    err.container.append(err.alert);
    submitIcon.empty().removeClass('hg-loading').html('<i class="remixicon-search-line"></i>');
    return false;
  }
  $('#hg-form').animsition('out', $('#hg-results'), '#');
  $('#hg-form').hide();
  swapSpacing('results');
  $('#hg-results').show();
  $('#hg-results').animsition('in');
  $('#hg-submit-spinner').remove();
  $('#hg-back-btn').removeClass('d-none');
  $('#hg-back-btn').animsition('in');
});

$('#hg-title-col').on('click', (e) => {
  window.location = $(e.currentTarget).data('href');
  return false;
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

/*
.hg-done is the class added to the ${loc}-status-btn button component, once the
content has finished loading.
*/

// On hover, change icon to show that the content can be refreshed
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

// On click, refresh the content
$('#hg-accordion').on('click', '.hg-done', (e) => {
  const refreshQueryType = $('#query_type').val() || '';
  const refreshQueryLocation = $('#location').val() || '';
  const refreshQueryTarget = $('#query_target').val() || '';
  const refreshQueryVrf = $('#query_vrf').val() || '';
  const refreshQueryTypeTitle = $(`#${refreshQueryType}`).data('display-name');
  queryApp(
    refreshQueryType,
    refreshQueryTypeTitle,
    refreshQueryLocation,
    refreshQueryTarget,
    refreshQueryVrf,
  );
});

$('#hg-ratelimit-query').on('shown.bs.modal', () => {
  $('#hg-ratelimit-query').trigger('focus');
});

$('#hg-ratelimit-query').find('btn').on('click', () => {
  $('#hg-ratelimit-query').modal('hide');
});
