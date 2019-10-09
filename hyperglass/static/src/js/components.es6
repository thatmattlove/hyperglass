function footerPopoverTemplate() {
  const element = `
        <div class="popover mw-sm-75 mw-md-50 mw-lg-25" role="tooltip">
            <div class="arrow"></div>
            <h3 class="popover-header"></h3>
            <div class="popover-body"></div>
        </div>`;
  return element;
}
function feedbackInvalid(msg) {
  return `<div class="invalid-feedback px-1">${msg}</div>`;
}
function iconLoading(loc) {
  const element = `
    <i id="${loc}-spinner" class="hg-menu-icon hg-status-icon remixicon-loader-4-line text-secondary"></i>`;
  return element;
}
function iconError() {
  const element = '<i class="hg-menu-icon hg-status-icon remixicon-alert-line"></i>';
  return element;
}
function iconTimeout() {
  const element = '<i class="remixicon-time-line"></i>';
  return element;
}
function iconSuccess() {
  const element = '<i class="hg-menu-icon hg-status-icon remixicon-check-line"></i>';
  return element;
}
function supportedBtn(queryType) {
  const element = `
        <button class="btn btn-secondary hg-info-btn" id="hg-info-btn-${queryType}" data-hg-type="${queryType}" type="button">
            <div id="hg-info-icon-${queryType}">
                <i class="remixicon-information-line"></i>
            </div>
        </button>`;
  return element;
}
function vrfSelect(title) {
  const element = `<select class="form-control form-control-lg hg-select" id="query_vrf" title="${title}" disabled></select>`;
  return element;
}
function frontEndAlert(msg) {
  const element = `<div class="alert alert-danger text-center" id="hg-frontend-alert" role="alert">${msg}</div>`;
  return element;
}
function vrfOption(txt) {
  const element = `<option value="${txt}">${txt}</option>`;
  return element;
}
function tagGroup(label, value) {
  const element = `
        <div class="input-group mb-3">
            <div class="input-group-prepend">
                ${label}
            </div>
            <div class="input-group-append">
                ${value}
            </div>
        </div>`;
  return element;
}
function tagLabel(color, id, text) {
  const element = `
        <span class="input-group-text hg-tag bg-${color}" id="hg-tag-${id}">
            ${text}
        </span>`;
  return element;
}

function resultsTitle(target, type, vrf, vrfText) {
  const element = `
  <div class="card-group flex-fill">
    <div class="card">
      <div class="card-body p-1 text-center">
        <h5 class="card-title mb-1">${target}</h6>
        <p class="card-text text-muted">${type}</p>
      </div>
    </div>
    <div class="card">
      <div class="card-body p-1 text-center">
        <h5 class="card-title mb-1">${vrf}</h6>
        <p class="card-text text-muted">${vrfText}</p>
      </div>
    </div>
  </div>`;
  return element;
}

function outputBlock(loc) {
  const element = `
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
    </div>`;
  return element;
}

module.exports = {
  footerPopoverTemplate,
  feedbackInvalid,
  iconLoading,
  iconError,
  iconTimeout,
  iconSuccess,
  supportedBtn,
  vrfSelect,
  frontEndAlert,
  vrfOption,
  tagGroup,
  tagLabel,
  resultsTitle,
  outputBlock,
};
