import {
  iconLoading, iconError, iconTimeout, iconSuccess, tagGroup, tagLabel, resultsTitle, outputBlock,
} from './components.es6';
import jQuery from '../node_modules/jquery';
import hgConf from './frontend.json';
import { resetResults } from './util.es6';

const $ = jQuery;

function queryApp(queryType, queryTypeName, locationList, queryTarget, queryVrf) {
  // $('#hg-results-title').html(
  //   tagGroup(
  //     tagLabel(
  //       'loading',
  //       'query-type',
  //       queryTypeName,
  //     ),
  //     tagLabel(
  //       'primary',
  //       'query-target',
  //       queryTarget,
  //     ),
  //   )
  //   + tagGroup(
  //     tagLabel(
  //       'loading',
  //       'query-vrf-loc',
  //       locationList.join(', '),
  //     ),
  //     tagLabel(
  //       'secondary',
  //       'query-target',
  //       queryVrf,
  //     ),
  //   ),
  // );

  $('#hg-results-title').html(
    resultsTitle(
      queryTarget,
      queryTypeName,
      queryVrf,
      hgConf.config.branding.text.vrf,
    ),
  );

  $('#hg-submit-icon').empty().removeClass('hg-loading').html('<i class="remixicon-search-line"></i>');

  $.each(locationList, (n, loc) => {
    const locationName = $(`#${loc}`).data('display-name');

    const contentHtml = outputBlock(loc);

    if ($(`#${loc}-output`).length) {
      $(`#${loc}-output`).replaceWith(contentHtml);
    } else {
      $('#hg-accordion').append(contentHtml);
    }

    $(`#${loc}-heading-text`).text(locationName);
    $(`#${loc}-status-container`)
      .addClass('hg-loading')
      .find('.hg-status-btn')
      .empty()
      .html(iconLoading(loc));

    const generateError = (errorClass, locError, text) => {
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
      $(`#${locError}-heading`).removeClass('bg-overlay').addClass('bg-warning');
      $(`#${locError}-heading`).find('.hg-menu-btn').removeClass('btn-loading').addClass('btn-warning');
      $(`#${locError}-status-container`).removeClass('hg-loading').find('.hg-status-btn').empty()
        .html(iconTimeout)
        .addClass('hg-done');
      $(`#${locError}-text`).empty().html(text);
    };

    $.ajax({
      url: '/query',
      method: 'POST',
      data: JSON.stringify({
        query_location: loc,
        query_type: queryType,
        query_target: queryTarget,
        query_vrf: queryVrf,
        response_format: 'html',
      }),
      contentType: 'application/json; charset=utf-8',
      context: document.body,
      async: true,
      timeout: hgConf.config.general.request_timeout * 1000,
    })
      .done((data, textStatus, jqXHR) => {
        const displayHtml = `<pre>${data.output}</pre>`;
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
        const statusCode = jqXHR.status;
        if (textStatus === 'timeout') {
          timeoutError(loc, hgConf.config.messages.request_timeout);
        } else if (jqXHR.status === 429) {
          resetResults();
          $('#hg-ratelimit-query').modal('show');
        } else if (statusCode === 500 && textStatus !== 'timeout') {
          timeoutError(loc, hgConf.config.messages.request_timeout);
        } else if ((jqXHR.responseJSON.alert === 'danger') || (jqXHR.responseJSON.alert === 'warning')) {
          generateError(jqXHR.responseJSON.alert, loc, jqXHR.responseJSON.output);
        }
      })
      .always(() => {
        $(`#${loc}-status-btn`).removeAttr('disabled');
        $(`#${loc}-copy-btn`).removeAttr('disabled');
      });
    $(`#${locationList[0]}-content`).collapse('show');
  });
}
module.exports = {
  queryApp,
};
