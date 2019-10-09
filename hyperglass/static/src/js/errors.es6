import { frontEndAlert } from './components.es6';

class InputInvalid extends Error {
  constructor(validationMsg, invalidField, fieldContainer) {
    super(validationMsg, invalidField, fieldContainer);
    this.name = this.constructor.name;
    this.message = validationMsg;
    this.field = invalidField;
    this.container = fieldContainer;
  }
}

class FrontEndError extends Error {
  constructor(errorMsg, msgContainer) {
    super(errorMsg, msgContainer);
    this.name = this.constructor.name;
    this.message = errorMsg;
    this.container = msgContainer;
    this.alert = frontEndAlert(this.message);
  }
}

module.exports = {
  InputInvalid,
  FrontEndError,
};
