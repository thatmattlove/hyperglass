// Module Imports
import jQuery from '../node_modules/jquery';

const $ = jQuery;

const pageContainer = $('#hg-page-container');
const formContainer = $('#hg-form');
const titleColumn = $('#hg-title-col');
const queryLocation = $('#location');
const queryType = $('#query_type');
const queryTarget = $('#query_target');
const queryVrf = $('#query_vrf');
const resultsContainer = $('#hg-results');
const resultsAccordion = $('#hg-accordion');
const resultsColumn = resultsAccordion.parent();
const backButton = $('#hg-back-btn');

function swapSpacing(goTo) {
  if (goTo === 'form') {
    pageContainer.removeClass('px-0 px-md-3');
    resultsColumn.removeClass('px-0');
    titleColumn.removeClass('text-center');
  } else if (goTo === 'results') {
    pageContainer.addClass('px-0 px-md-3');
    resultsColumn.addClass('px-0');
    titleColumn.addClass('text-left');
  }
}

function resetResults() {
  queryLocation.selectpicker('deselectAll');
  queryLocation.selectpicker('val', '');
  queryType.selectpicker('val', '');
  queryTarget.val('');
  queryVrf.val('');
  resultsContainer.animsition('out', formContainer, '#');
  resultsContainer.hide();
  $('.hg-info-btn').remove();
  swapSpacing('form');
  formContainer.show();
  formContainer.animsition('in');
  backButton.addClass('d-none');
  resultsAccordion.empty();
}

function reloadPage() {
  queryLocation.selectpicker('deselectAll');
  queryLocation.selectpicker('val', []);
  queryType.selectpicker('val', '');
  queryTarget.val('');
  queryVrf.val('');
  resultsAccordion.empty();
}

function findIntersection(firstSet, ...sets) {
  const count = sets.length;
  const result = new Set(firstSet);
  firstSet.forEach((item) => {
    let i = count;
    let allHave = true;
    while (i--) {
      allHave = sets[i].has(item);
      if (!allHave) { break; }
    }
    if (!allHave) {
      result.delete(item);
    }
  });
  return result;
}
module.exports = {
  swapSpacing,
  resetResults,
  reloadPage,
  findIntersection,
};
