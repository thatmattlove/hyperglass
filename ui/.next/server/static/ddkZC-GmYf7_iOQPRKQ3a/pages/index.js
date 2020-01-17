module.exports =
/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = require('../../../ssr-module-cache.js');
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		var threw = true;
/******/ 		try {
/******/ 			modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 			threw = false;
/******/ 		} finally {
/******/ 			if(threw) delete installedModules[moduleId];
/******/ 		}
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 2);
/******/ })
/************************************************************************/
/******/ ({

/***/ "+Iqc":
/***/ (function(module, exports) {

module.exports = require("react-string-replace");

/***/ }),

/***/ "/T1H":
/***/ (function(module, exports) {

module.exports = require("next/dynamic");

/***/ }),

/***/ 2:
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__("RNiq");


/***/ }),

/***/ "2Eek":
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__("ltjX");

/***/ }),

/***/ "4mXO":
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__("k1wZ");

/***/ }),

/***/ "9yvl":
/***/ (function(module, exports) {

module.exports = require("react-icons/go");

/***/ }),

/***/ "BTiB":
/***/ (function(module, exports) {

module.exports = require("react-hook-form");

/***/ }),

/***/ "C8TP":
/***/ (function(module, exports) {

module.exports = require("yup");

/***/ }),

/***/ "C9pf":
/***/ (function(module, exports) {

module.exports = require("react-icons/fi");

/***/ }),

/***/ "Eqhy":
/***/ (function(module, exports) {

module.exports = require("string-format");

/***/ }),

/***/ "Jo+v":
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__("Z6Kq");

/***/ }),

/***/ "QTVn":
/***/ (function(module, exports) {

module.exports = require("core-js/library/fn/object/get-own-property-descriptors");

/***/ }),

/***/ "QmcS":
/***/ (function(module, exports) {

module.exports = require("chroma-js");

/***/ }),

/***/ "RNiq":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);

// EXTERNAL MODULE: external "react"
var external_react_ = __webpack_require__("cDcd");
var external_react_default = /*#__PURE__*/__webpack_require__.n(external_react_);

// EXTERNAL MODULE: external "next/dynamic"
var dynamic_ = __webpack_require__("/T1H");
var dynamic_default = /*#__PURE__*/__webpack_require__.n(dynamic_);

// EXTERNAL MODULE: external "axios-hooks"
var external_axios_hooks_ = __webpack_require__("qUDc");
var external_axios_hooks_default = /*#__PURE__*/__webpack_require__.n(external_axios_hooks_);

// EXTERNAL MODULE: external "@chakra-ui/core"
var core_ = __webpack_require__("WKWs");

// EXTERNAL MODULE: external "framer-motion"
var external_framer_motion_ = __webpack_require__("wmQq");

// EXTERNAL MODULE: external "react-icons/fi"
var fi_ = __webpack_require__("C9pf");

// CONCATENATED MODULE: ./components/ResetButton.js
var __jsx = external_react_default.a.createElement;



/* harmony default export */ var ResetButton = (external_react_default.a.forwardRef(({
  isSubmitting,
  onClick
}, ref) => __jsx(core_["Box"], {
  ref: ref,
  position: "fixed",
  bottom: 16,
  left: 8,
  opacity: isSubmitting ? 1 : 0
}, __jsx(core_["Button"], {
  variantColor: "primary",
  variant: "outline",
  p: 2,
  onClick: onClick
}, __jsx(fi_["FiChevronLeft"], {
  size: 24
})))));
// EXTERNAL MODULE: ./node_modules/@babel/runtime-corejs2/core-js/object/assign.js
var object_assign = __webpack_require__("UXZV");
var assign_default = /*#__PURE__*/__webpack_require__.n(object_assign);

// CONCATENATED MODULE: ./node_modules/@babel/runtime-corejs2/helpers/esm/extends.js

function _extends() {
  _extends = assign_default.a || function (target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];

      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }

    return target;
  };

  return _extends.apply(this, arguments);
}
// EXTERNAL MODULE: ./node_modules/@babel/runtime-corejs2/core-js/object/get-own-property-symbols.js
var get_own_property_symbols = __webpack_require__("4mXO");
var get_own_property_symbols_default = /*#__PURE__*/__webpack_require__.n(get_own_property_symbols);

// EXTERNAL MODULE: ./node_modules/@babel/runtime-corejs2/core-js/object/keys.js
var object_keys = __webpack_require__("pLtp");
var keys_default = /*#__PURE__*/__webpack_require__.n(object_keys);

// CONCATENATED MODULE: ./node_modules/@babel/runtime-corejs2/helpers/esm/objectWithoutPropertiesLoose.js

function _objectWithoutPropertiesLoose(source, excluded) {
  if (source == null) return {};
  var target = {};

  var sourceKeys = keys_default()(source);

  var key, i;

  for (i = 0; i < sourceKeys.length; i++) {
    key = sourceKeys[i];
    if (excluded.indexOf(key) >= 0) continue;
    target[key] = source[key];
  }

  return target;
}
// CONCATENATED MODULE: ./node_modules/@babel/runtime-corejs2/helpers/esm/objectWithoutProperties.js


function _objectWithoutProperties(source, excluded) {
  if (source == null) return {};
  var target = _objectWithoutPropertiesLoose(source, excluded);
  var key, i;

  if (get_own_property_symbols_default.a) {
    var sourceSymbolKeys = get_own_property_symbols_default()(source);

    for (i = 0; i < sourceSymbolKeys.length; i++) {
      key = sourceSymbolKeys[i];
      if (excluded.indexOf(key) >= 0) continue;
      if (!Object.prototype.propertyIsEnumerable.call(source, key)) continue;
      target[key] = source[key];
    }
  }

  return target;
}
// EXTERNAL MODULE: external "react-hook-form"
var external_react_hook_form_ = __webpack_require__("BTiB");

// EXTERNAL MODULE: external "lodash"
var external_lodash_ = __webpack_require__("YLtl");
var external_lodash_default = /*#__PURE__*/__webpack_require__.n(external_lodash_);

// EXTERNAL MODULE: external "yup"
var external_yup_ = __webpack_require__("C8TP");

// EXTERNAL MODULE: external "string-format"
var external_string_format_ = __webpack_require__("Eqhy");
var external_string_format_default = /*#__PURE__*/__webpack_require__.n(external_string_format_);

// EXTERNAL MODULE: external "react-markdown"
var external_react_markdown_ = __webpack_require__("id0+");
var external_react_markdown_default = /*#__PURE__*/__webpack_require__.n(external_react_markdown_);

// CONCATENATED MODULE: ./components/CodeBlock.js
var CodeBlock_jsx = external_react_default.a.createElement;


/* harmony default export */ var CodeBlock = (({
  children
}) => {
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const theme = Object(core_["useTheme"])();
  const bg = {
    dark: theme.colors.gray[800],
    light: theme.colors.blackAlpha[100]
  };
  const color = {
    dark: theme.colors.white,
    light: theme.colors.black
  };
  return CodeBlock_jsx(core_["Box"], {
    fontFamily: "mono",
    mt: 5,
    p: 3,
    border: "1px",
    borderColor: "inherit",
    rounded: "md",
    bg: bg[colorMode],
    color: color[colorMode],
    fontSize: "sm",
    whiteSpace: "pre-wrap",
    as: "pre"
  }, children);
});
// CONCATENATED MODULE: ./hooks/useColored.js

/* harmony default export */ var useColored = ((mode = "light", light = "black", dark = "white") => Object(external_react_["useMemo"])(() => mode ? light : dark));
// CONCATENATED MODULE: ./components/Table.js


var Table_jsx = external_react_default.a.createElement;




const Table = props => Table_jsx(core_["Box"], _extends({
  as: "table",
  textAlign: "left",
  mt: 4,
  width: "full"
}, props));

const TableHeader = props => {
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const bg = {
    light: "blackAlpha.50",
    dark: "whiteAlpha.50"
  };
  return Table_jsx(core_["Box"], _extends({
    as: "th",
    bg: bg[colorMode],
    fontWeight: "semibold",
    p: 2,
    fontSize: "sm"
  }, props));
};

const TableCell = (_ref) => {
  let {
    isHeader = false
  } = _ref,
      props = _objectWithoutProperties(_ref, ["isHeader"]);

  return Table_jsx(core_["Box"], _extends({
    as: isHeader ? "th" : "td",
    p: 2,
    borderTopWidth: "1px",
    borderColor: "inherit",
    fontSize: "sm",
    whiteSpace: "normal"
  }, props));
};


// CONCATENATED MODULE: ./components/MarkDown.js


var MarkDown_jsx = external_react_default.a.createElement;






const Checkbox = ({
  checked,
  children
}) => MarkDown_jsx(core_["Checkbox"], {
  isChecked: checked
}, children);

const List = ({
  ordered,
  children
}) => MarkDown_jsx(core_["List"], {
  as: ordered ? "ol" : "ul"
}, children);

const ListItem = ({
  checked,
  children
}) => checked ? MarkDown_jsx(Checkbox, {
  checked: checked
}, children) : MarkDown_jsx(core_["ListItem"], null, children);

const Heading = ({
  level,
  children
}) => {
  const levelMap = {
    1: {
      as: "h1",
      size: "lg",
      fontWeight: "bold"
    },
    2: {
      as: "h2",
      size: "lg",
      fontWeight: "normal"
    },
    3: {
      as: "h3",
      size: "lg",
      fontWeight: "bold"
    },
    4: {
      as: "h4",
      size: "md",
      fontWeight: "normal"
    },
    5: {
      as: "h5",
      size: "md",
      fontWeight: "bold"
    },
    6: {
      as: "h6",
      size: "sm",
      fontWeight: "bold"
    }
  };
  return MarkDown_jsx(core_["Heading"], levelMap[level], children);
};

const Link = (_ref) => {
  let {
    children
  } = _ref,
      props = _objectWithoutProperties(_ref, ["children"]);

  return MarkDown_jsx(core_["Link"], _extends({
    isExternal: true
  }, props), children);
};

const MarkDown_CodeBlock = ({
  value
}) => MarkDown_jsx(CodeBlock, null, value);

const TableData = (_ref2) => {
  let {
    isHeader,
    children
  } = _ref2,
      props = _objectWithoutProperties(_ref2, ["isHeader", "children"]);

  const Component = isHeader ? TableHeader : TableCell;
  return MarkDown_jsx(Component, props, children);
};

const mdComponents = {
  paragraph: core_["Text"],
  link: Link,
  heading: Heading,
  inlineCode: core_["Code"],
  list: List,
  listItem: ListItem,
  thematicBreak: core_["Divider"],
  code: MarkDown_CodeBlock,
  table: Table,
  tableCell: TableData
};
/* harmony default export */ var MarkDown = (external_react_default.a.forwardRef(({
  content
}, ref) => MarkDown_jsx(external_react_markdown_default.a, {
  ref: ref,
  renderers: mdComponents,
  source: content
})));
// CONCATENATED MODULE: ./components/HelpModal.js
var HelpModal_jsx = external_react_default.a.createElement;




const AnimatedIcon = external_framer_motion_["motion"].custom(core_["IconButton"]);
/* harmony default export */ var HelpModal = (({
  item,
  name
}) => {
  const {
    isOpen,
    onOpen,
    onClose
  } = Object(core_["useDisclosure"])();
  const theme = Object(core_["useTheme"])();
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const bg = {
    light: theme.colors.white,
    dark: theme.colors.dark
  };
  const color = {
    light: theme.colors.black,
    dark: theme.colors.white
  };
  const iconColor = {
    light: theme.colors.primary[500],
    dark: theme.colors.primary[300]
  };
  return HelpModal_jsx(external_react_default.a.Fragment, null, HelpModal_jsx(external_framer_motion_["AnimatePresence"], null, HelpModal_jsx(AnimatedIcon, {
    initial: {
      opacity: 0,
      scale: 0.3,
      color: theme.colors.gray[500]
    },
    animate: {
      opacity: 1,
      scale: 1,
      color: iconColor[colorMode]
    },
    transition: {
      duration: 0.2
    },
    exit: {
      opacity: 0,
      scale: 0.3
    },
    variantColor: "primary",
    "aria-label": `${name}_help`,
    icon: "info-outline",
    variant: "link",
    size: "sm",
    h: "unset",
    w: 3,
    minW: 3,
    maxW: 3,
    h: 3,
    minH: 3,
    maxH: 3,
    ml: 1,
    mb: 1,
    onClick: onOpen
  })), HelpModal_jsx(core_["Modal"], {
    isOpen: isOpen,
    onClose: onClose,
    size: "xl"
  }, HelpModal_jsx(core_["ModalOverlay"], null), HelpModal_jsx(core_["ModalContent"], {
    bg: bg[colorMode],
    color: color[colorMode],
    py: 4,
    borderRadius: "md"
  }, HelpModal_jsx(core_["ModalHeader"], null, item.params.title), HelpModal_jsx(core_["ModalCloseButton"], null), HelpModal_jsx(core_["ModalBody"], null, HelpModal_jsx(MarkDown, {
    content: item.content
  })))));
});
// CONCATENATED MODULE: ./components/FormField.js


var FormField_jsx = external_react_default.a.createElement;



/* harmony default export */ var FormField = ((_ref) => {
  let {
    label,
    name,
    error,
    hiddenLabels,
    helpIcon,
    children
  } = _ref,
      props = _objectWithoutProperties(_ref, ["label", "name", "error", "hiddenLabels", "helpIcon", "children"]);

  const theme = Object(core_["useTheme"])();
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const labelColor = colorMode === "dark" ? theme.colors.whiteAlpha[600] : theme.colors.blackAlpha[600];
  return FormField_jsx(core_["FormControl"], _extends({
    as: core_["Flex"],
    flexDirection: "column",
    flexGrow: 1,
    flexBasis: 0,
    w: "100%",
    maxW: "100%",
    mx: 2,
    isInvalid: error && error.message
  }, props), FormField_jsx(core_["FormLabel"], {
    htmlFor: name,
    color: labelColor,
    pl: 1,
    opacity: hiddenLabels ? 0 : null
  }, label, (helpIcon === null || helpIcon === void 0 ? void 0 : helpIcon.enable) && FormField_jsx(HelpModal, {
    item: helpIcon,
    name: name
  })), children, FormField_jsx(core_["FormErrorMessage"], {
    opacity: hiddenLabels ? 0 : null
  }, error && error.message));
});
// EXTERNAL MODULE: ./node_modules/@babel/runtime-corejs2/core-js/object/define-property.js
var define_property = __webpack_require__("hfKm");
var define_property_default = /*#__PURE__*/__webpack_require__.n(define_property);

// EXTERNAL MODULE: ./node_modules/@babel/runtime-corejs2/core-js/object/define-properties.js
var define_properties = __webpack_require__("2Eek");
var define_properties_default = /*#__PURE__*/__webpack_require__.n(define_properties);

// EXTERNAL MODULE: ./node_modules/@babel/runtime-corejs2/core-js/object/get-own-property-descriptors.js
var get_own_property_descriptors = __webpack_require__("XoMD");
var get_own_property_descriptors_default = /*#__PURE__*/__webpack_require__.n(get_own_property_descriptors);

// EXTERNAL MODULE: ./node_modules/@babel/runtime-corejs2/core-js/object/get-own-property-descriptor.js
var get_own_property_descriptor = __webpack_require__("Jo+v");
var get_own_property_descriptor_default = /*#__PURE__*/__webpack_require__.n(get_own_property_descriptor);

// EXTERNAL MODULE: ./node_modules/@babel/runtime-corejs2/helpers/esm/defineProperty.js
var defineProperty = __webpack_require__("vYYK");

// EXTERNAL MODULE: external "react-select"
var external_react_select_ = __webpack_require__("vtRj");
var external_react_select_default = /*#__PURE__*/__webpack_require__.n(external_react_select_);

// EXTERNAL MODULE: external "chroma-js"
var external_chroma_js_ = __webpack_require__("QmcS");
var external_chroma_js_default = /*#__PURE__*/__webpack_require__.n(external_chroma_js_);

// CONCATENATED MODULE: ./util.js


const isDark = color => {
  // YIQ equation from http://24ways.org/2010/calculating-color-contrast
  const rgb = external_chroma_js_default()(color).rgb();
  const yiq = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000;
  return yiq < 128;
};

const isLight = color => isDark(color);

const opposingColor = (theme, color) => {
  const opposing = isDark(color) ? theme.colors.white : theme.colors.black;
  return opposing;
};

const googleFontUrl = (fontFamily, weights = [300, 400, 700]) => {
  const urlWeights = weights.join(",");
  const fontName = fontFamily.split(/, /)[0].trim().replace(/'|"/g, "");
  const urlFont = fontName.split(/ /).join("+");
  const urlBase = `https://fonts.googleapis.com/css?family=${urlFont}:${urlWeights}&display=swap`;
  return urlBase;
};


// CONCATENATED MODULE: ./components/ChakraSelect.js









var ChakraSelect_jsx = external_react_default.a.createElement;

function ownKeys(object, enumerableOnly) { var keys = keys_default()(object); if (get_own_property_symbols_default.a) { var symbols = get_own_property_symbols_default()(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return get_own_property_descriptor_default()(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { Object(defineProperty["a" /* default */])(target, key, source[key]); }); } else if (get_own_property_descriptors_default.a) { define_properties_default()(target, get_own_property_descriptors_default()(source)); } else { ownKeys(Object(source)).forEach(function (key) { define_property_default()(target, key, get_own_property_descriptor_default()(source, key)); }); } } return target; }





/* harmony default export */ var ChakraSelect = ((_ref) => {
  let {
    placeholder = "Select...",
    isFullWidth,
    size,
    children
  } = _ref,
      props = _objectWithoutProperties(_ref, ["placeholder", "isFullWidth", "size", "children"]);

  const theme = Object(core_["useTheme"])();
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const sizeMap = {
    lg: {
      height: theme.space[12]
    },
    md: {
      height: theme.space[10]
    },
    sm: {
      height: theme.space[8]
    }
  };
  const colorSetPrimaryBg = {
    dark: theme.colors.primary[300],
    light: theme.colors.primary[500]
  };
  const colorSetPrimaryColor = opposingColor(theme, colorSetPrimaryBg[colorMode]);
  const bg = {
    dark: theme.colors.whiteAlpha[100],
    light: theme.colors.white
  };
  const color = {
    dark: theme.colors.whiteAlpha[800],
    light: theme.colors.black
  };
  const borderFocused = theme.colors.secondary[500];
  const borderDisabled = theme.colors.whiteAlpha[100];
  const border = {
    dark: theme.colors.whiteAlpha[50],
    light: theme.colors.gray[100]
  };
  const borderRadius = theme.space[1];
  const hoverColor = {
    dark: theme.colors.whiteAlpha[200],
    light: theme.colors.gray[300]
  };
  const {
    height
  } = sizeMap[size];
  const optionBgActive = {
    dark: theme.colors.primary[400],
    light: theme.colors.primary[600]
  };
  const optionBgColor = opposingColor(theme, optionBgActive[colorMode]);
  const selectedDisabled = theme.colors.whiteAlpha[400];
  const placeholderColor = {
    dark: theme.colors.whiteAlpha[400],
    light: theme.colors.gray[400]
  };
  const menuBg = {
    dark: theme.colors.black,
    light: theme.colors.white
  };
  const menuColor = {
    dark: theme.colors.white,
    light: theme.colors.blackAlpha[800]
  };
  return ChakraSelect_jsx(external_react_select_default.a, _extends({
    styles: {
      container: base => _objectSpread({}, base, {
        minHeight: height,
        borderRadius: borderRadius,
        width: "100%"
      }),
      control: (base, state) => _objectSpread({}, base, {
        minHeight: height,
        backgroundColor: bg[colorMode],
        color: color[colorMode],
        borderColor: state.isDisabled ? borderDisabled : state.isFocused ? borderFocused : border[colorMode],
        borderRadius: borderRadius,
        "&:hover": {
          borderColor: hoverColor[colorMode]
        }
      }),
      menu: base => _objectSpread({}, base, {
        backgroundColor: menuBg[colorMode],
        borderRadius: borderRadius
      }),
      option: (base, state) => _objectSpread({}, base, {
        backgroundColor: state.isDisabled ? selectedDisabled : state.isSelected ? colorSetPrimaryBg[colorMode] : state.isFocused ? colorSetPrimaryBg[colorMode] : "transparent",
        color: state.isDisabled ? selectedDisabled : state.isFocused ? colorSetPrimaryColor : state.isSelected ? colorSetPrimaryColor : menuColor[colorMode],
        fontSize: theme.fontSizes[size],
        "&:active": {
          backgroundColor: optionBgActive[colorMode],
          color: optionBgColor
        }
      }),
      indicatorSeparator: base => _objectSpread({}, base, {
        backgroundColor: placeholderColor[colorMode]
      }),
      dropdownIndicator: base => _objectSpread({}, base, {
        color: placeholderColor[colorMode],
        "&:hover": {
          color: color[colorMode]
        }
      }),
      valueContainer: base => _objectSpread({}, base, {
        paddingLeft: theme.space[4],
        paddingRight: theme.space[4]
      }),
      multiValue: base => _objectSpread({}, base, {
        backgroundColor: colorSetPrimaryBg[colorMode]
      }),
      multiValueLabel: base => _objectSpread({}, base, {
        color: colorSetPrimaryColor
      }),
      multiValueRemove: base => _objectSpread({}, base, {
        color: colorSetPrimaryColor,
        "&:hover": {
          color: colorSetPrimaryColor,
          backgroundColor: "inherit"
        }
      }),
      singleValue: base => _objectSpread({}, base, {
        color: color[colorMode],
        fontSize: theme.fontSizes[size]
      })
    },
    placeholder: ChakraSelect_jsx(core_["Text"], {
      color: placeholderColor[colorMode],
      fontSize: size,
      fontFamily: theme.fonts.body
    }, placeholder)
  }, props), children);
});
// CONCATENATED MODULE: ./components/QueryLocation.js
var QueryLocation_jsx = external_react_default.a.createElement;



const buildLocations = networks => {
  const locations = [];
  networks.map(net => {
    const netLocations = [];
    net.locations.map(loc => {
      netLocations.push({
        label: loc.display_name,
        value: loc.name,
        group: net.display_name
      });
    });
    locations.push({
      label: net.display_name,
      options: netLocations
    });
  });
  return locations;
};

/* harmony default export */ var QueryLocation = (({
  locations,
  onChange
}) => {
  const options = buildLocations(locations);

  const handleChange = e => {
    const selected = [];
    e && e.map(sel => {
      selected.push(sel.value);
    });
    onChange({
      field: "query_location",
      value: selected
    });
  };

  return QueryLocation_jsx(ChakraSelect, {
    size: "lg",
    name: "query_location",
    onChange: handleChange,
    options: options,
    isMulti: true
  });
});
// CONCATENATED MODULE: ./components/QueryType.js
var QueryType_jsx = external_react_default.a.createElement;



const buildQueries = queryTypes => {
  const queries = [];
  queryTypes.map(q => {
    queries.push({
      value: q.name,
      label: q.display_name
    });
  });
  return queries;
};

/* harmony default export */ var QueryType = (({
  queryTypes,
  onChange
}) => {
  const queries = buildQueries(queryTypes);
  return QueryType_jsx(ChakraSelect, {
    size: "lg",
    name: "query_type",
    onChange: e => onChange({
      field: "query_type",
      value: e.value
    }),
    options: queries
  });
});
// EXTERNAL MODULE: external "@emotion/styled"
var styled_ = __webpack_require__("UlNW");
var styled_default = /*#__PURE__*/__webpack_require__.n(styled_);

// CONCATENATED MODULE: ./components/QueryTarget.js
var QueryTarget_jsx = external_react_default.a.createElement;



const StyledInput = styled_default()(core_["Input"])`
    &::placeholder {
        color: ${props => props.placeholderColor};
    }
`;
/* harmony default export */ var QueryTarget = (({
  placeholder,
  register
}) => {
  const theme = Object(core_["useTheme"])();
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const bg = colorMode === "dark" ? theme.colors.whiteAlpha[100] : theme.colors.white;
  const color = colorMode === "dark" ? theme.colors.whiteAlpha[800] : theme.colors.gray[400];
  const border = colorMode === "dark" ? theme.colors.whiteAlpha[50] : theme.colors.gray[100];
  const borderRadius = theme.space[1];
  const placeholderColor = colorMode === "dark" ? theme.colors.whiteAlpha[400] : theme.colors.gray[400];
  return QueryTarget_jsx(StyledInput, {
    name: "query_target",
    ref: register,
    placeholder: placeholder,
    placeholderColor: placeholderColor,
    size: "lg",
    bg: bg,
    color: color,
    borderColor: border,
    borderRadius: borderRadius
  });
});
// CONCATENATED MODULE: ./components/QueryVrf.js
var QueryVrf_jsx = external_react_default.a.createElement;


/* harmony default export */ var QueryVrf = (({
  vrfs,
  onChange
}) => {
  return QueryVrf_jsx(ChakraSelect, {
    size: "lg",
    placeholder: "VRF",
    onChange: e => onChange({
      field: "query_vrf",
      value: e.value
    }),
    name: "query_vrf",
    options: vrfs
  });
});
// CONCATENATED MODULE: ./components/SubmitButton.js


var SubmitButton_jsx = external_react_default.a.createElement;




const btnProps = {
  display: "inline-flex",
  appearance: "none",
  alignItems: "center",
  justifyContent: "center",
  transition: "all 250ms",
  userSelect: "none",
  position: "relative",
  whiteSpace: "nowrap",
  verticalAlign: "middle",
  lineHeight: "1.2",
  outline: "none",
  as: "button",
  type: "submit",
  borderRadius: "md",
  fontWeight: "semibold"
};
const btnSizeMap = {
  lg: {
    height: 12,
    minWidth: 12,
    fontSize: "lg",
    px: 6
  },
  md: {
    height: 10,
    minWidth: 10,
    fontSize: "md",
    px: 4
  },
  sm: {
    height: 8,
    minWidth: 8,
    fontSize: "sm",
    px: 3
  },
  xs: {
    height: 6,
    minWidth: 6,
    fontSize: "xs",
    px: 2
  }
};
/* harmony default export */ var SubmitButton = (external_react_default.a.forwardRef((_ref, ref) => {
  let {
    isLoading = false,
    isDisabled = false,
    isActive = false,
    isFullWidth = false,
    size = "lg",
    loadingText,
    children
  } = _ref,
      props = _objectWithoutProperties(_ref, ["isLoading", "isDisabled", "isActive", "isFullWidth", "size", "loadingText", "children"]);

  const _isDisabled = isDisabled || isLoading;

  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const theme = Object(core_["useTheme"])();
  const btnBg = {
    dark: theme.colors.primary[300],
    light: theme.colors.primary[500]
  };
  const btnBgActive = {
    dark: theme.colors.primary[400],
    light: theme.colors.primary[600]
  };
  const btnBgHover = {
    dark: theme.colors.primary[200],
    light: theme.colors.primary[400]
  };
  const btnColor = opposingColor(theme, btnBg[colorMode]);
  const btnColorActive = opposingColor(theme, btnBgActive[colorMode]);
  const btnColorHover = opposingColor(theme, btnBgHover[colorMode]);
  const btnSize = btnSizeMap[size];
  return SubmitButton_jsx(core_["PseudoBox"], _extends({
    ref: ref,
    disabled: _isDisabled,
    "aria-disabled": _isDisabled,
    width: isFullWidth ? "full" : undefined,
    "data-active": isActive ? "true" : undefined,
    bg: btnBg[colorMode],
    color: btnColor,
    _active: {
      bg: btnBgActive[colorMode],
      color: btnColorActive
    },
    _hover: {
      bg: btnBgHover[colorMode],
      color: btnColorHover
    },
    _focus: {
      boxShadow: theme.shadows.outline
    }
  }, btnProps, btnSize, props), isLoading ? SubmitButton_jsx(core_["Spinner"], {
    position: loadingText ? "relative" : "absolute",
    mr: loadingText ? 2 : 0,
    color: "currentColor",
    size: "1em"
  }) : SubmitButton_jsx(fi_["FiSearch"], {
    color: btnColor
  }), isLoading ? loadingText || SubmitButton_jsx(core_["Box"], {
    as: "span",
    opacity: "0"
  }, children) : children);
}));
// CONCATENATED MODULE: ./components/HyperglassForm.js


var HyperglassForm_jsx = external_react_default.a.createElement;












external_string_format_default.a.extend(String.prototype, {});

const HyperglassForm_all = (...items) => [...items].every(i => i ? true : false);

const formSchema = config => external_yup_["object"]().shape({
  query_location: external_yup_["array"]().of(external_yup_["string"]()).required(config.messages.no_input.format({
    field: config.branding.text.query_location
  })),
  query_type: external_yup_["string"]().required(config.messages.no_input.format({
    field: config.branding.text.query_type
  })),
  query_vrf: external_yup_["string"](),
  query_target: external_yup_["string"]().required(config.messages.no_input.format({
    field: config.branding.text.query_target
  }))
});

const FormRow = (_ref) => {
  let {
    children
  } = _ref,
      props = _objectWithoutProperties(_ref, ["children"]);

  return HyperglassForm_jsx(core_["Flex"], _extends({
    flexDirection: "row",
    flexWrap: "wrap",
    w: "100%",
    my: 4
  }, props), children);
};

/* harmony default export */ var HyperglassForm = (external_react_default.a.forwardRef((_ref2, ref) => {
  var _ref3, _config$content$vrf$q;

  let {
    config,
    isSubmitting,
    setSubmitting,
    setFormData
  } = _ref2,
      props = _objectWithoutProperties(_ref2, ["config", "isSubmitting", "setSubmitting", "setFormData"]);

  const {
    handleSubmit,
    register,
    setValue,
    errors
  } = Object(external_react_hook_form_["useForm"])({
    validationSchema: formSchema(config)
  });
  const {
    0: queryLocation,
    1: setQueryLocation
  } = Object(external_react_["useState"])([]);
  const {
    0: queryType,
    1: setQueryType
  } = Object(external_react_["useState"])("");
  const {
    0: queryVrf,
    1: setQueryVrf
  } = Object(external_react_["useState"])("");
  const {
    0: availVrfs,
    1: setAvailVrfs
  } = Object(external_react_["useState"])([]); // const [showHelpIcon, setShowHelpIcon] = useState(false);

  const onSubmit = values => {
    setFormData(values);
    setSubmitting(true);
  };

  const handleLocChange = locObj => {
    setQueryLocation(locObj.value);
    const allVrfs = [];
    locObj.value.map(loc => {
      const locVrfs = [];
      config.devices[loc].vrfs.map(vrf => {
        locVrfs.push({
          label: vrf.display_name,
          value: vrf.id
        });
      });
      allVrfs.push(locVrfs);
    });
    const intersecting = external_lodash_default.a.intersectionWith(...allVrfs, external_lodash_default.a.isEqual);
    setAvailVrfs(intersecting);
    !intersecting.includes(queryVrf) && setQueryVrf("");
  };

  const handleChange = e => {
    setValue(e.field, e.value);
    e.field === "query_location" ? handleLocChange(e) : e.field === "query_type" ? setQueryType(e.value) : e.field === "query_vrf" ? setQueryVrf(e.value) : null;
  };

  Object(external_react_["useEffect"])(() => {
    register({
      name: "query_location"
    });
    register({
      name: "query_type"
    });
    register({
      name: "query_vrf"
    });
  });
  return HyperglassForm_jsx(core_["Box"], _extends({
    maxW: ["100%", "100%", "75%", "50%"],
    w: "100%",
    p: 0,
    mx: "auto",
    my: 4,
    textAlign: "left",
    ref: ref
  }, props), HyperglassForm_jsx("form", {
    onSubmit: handleSubmit(onSubmit)
  }, HyperglassForm_jsx(FormRow, null, HyperglassForm_jsx(FormField, {
    label: config.branding.text.query_location,
    name: "query_location",
    error: errors.query_location
  }, HyperglassForm_jsx(QueryLocation, {
    onChange: handleChange,
    locations: config.networks
  })), HyperglassForm_jsx(FormField, {
    label: config.branding.text.query_type,
    name: "query_type",
    error: errors.query_type,
    helpIcon: (_ref3 = (_config$content$vrf$q = config.content.vrf[queryVrf]) === null || _config$content$vrf$q === void 0 ? void 0 : _config$content$vrf$q[queryType]) !== null && _ref3 !== void 0 ? _ref3 : null
  }, HyperglassForm_jsx(QueryType, {
    onChange: handleChange,
    queryTypes: config.queries
  }))), HyperglassForm_jsx(FormRow, null, availVrfs.length > 0 && HyperglassForm_jsx(FormField, {
    label: config.branding.text.query_vrf,
    name: "query_vrf",
    error: errors.query_vrf
  }, HyperglassForm_jsx(QueryVrf, {
    placeholder: config.branding.text.query_vrf,
    vrfs: availVrfs,
    onChange: handleChange
  })), HyperglassForm_jsx(FormField, {
    label: config.branding.text.query_target,
    name: "query_target",
    error: errors.query_target
  }, HyperglassForm_jsx(QueryTarget, {
    placeholder: config.branding.text.query_target,
    register: register
  })), HyperglassForm_jsx(FormField, {
    flexGrow: 0,
    label: "Submit",
    error: errors.query_target,
    hiddenLabels: true
  }, HyperglassForm_jsx(SubmitButton, {
    isLoading: isSubmitting
  })))));
}));
// CONCATENATED MODULE: ./components/Label.js
var Label_jsx = external_react_default.a.createElement;


/* harmony default export */ var Label = (external_react_default.a.forwardRef(({
  value,
  label,
  labelBg,
  labelColor,
  valueBg,
  valueColor
}, ref) => {
  const theme = Object(core_["useTheme"])();
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const _labelBg = {
    light: theme.colors.black,
    dark: theme.colors.gray[200]
  };
  const _labelColor = {
    light: theme.colors.white,
    dark: theme.colors.white
  };
  const _valueBg = {
    light: theme.colors.primary[600],
    dark: theme.colors.primary[600]
  };
  const _valueColor = {
    light: theme.colors.white,
    dark: theme.colors.white
  };
  return Label_jsx(core_["Flex"], {
    ref: ref,
    flexWrap: "wrap",
    alignItems: "center",
    justifyContent: "flex-start",
    mx: 2
  }, Label_jsx(core_["Flex"], {
    display: "inline-flex",
    justifyContent: "center",
    lineHeight: "1.5",
    px: 3,
    whiteSpace: "nowrap",
    mb: 2,
    mr: 0,
    bg: valueBg || _valueBg[colorMode],
    color: valueColor || _valueColor[colorMode],
    borderBottomLeftRadius: 4,
    borderTopLeftRadius: 4,
    borderBottomRightRadius: 0,
    borderTopRightRadius: 0,
    fontSize: "sm",
    fontWeight: "bold"
  }, value), Label_jsx(core_["Flex"], {
    display: "inline-flex",
    justifyContent: "center",
    lineHeight: "1.5",
    px: 3,
    whiteSpace: "nowrap",
    mb: 2,
    ml: 0,
    mr: 0,
    bg: labelBg || _labelBg[colorMode],
    color: labelColor || _labelColor[colorMode],
    borderBottomRightRadius: 4,
    borderTopRightRadius: 4,
    borderBottomLeftRadius: 0,
    borderTopLeftRadius: 0,
    fontSize: "sm"
  }, label));
}));
// EXTERNAL MODULE: external "react-string-replace"
var external_react_string_replace_ = __webpack_require__("+Iqc");
var external_react_string_replace_default = /*#__PURE__*/__webpack_require__.n(external_react_string_replace_);

// CONCATENATED MODULE: ./components/CopyButton.js
var CopyButton_jsx = external_react_default.a.createElement;


/* harmony default export */ var CopyButton = (({
  bg = "secondary",
  copyValue
}) => {
  const {
    onCopy,
    hasCopied
  } = Object(core_["useClipboard"])(copyValue);
  return CopyButton_jsx(core_["Tooltip"], {
    hasArrow: true,
    label: "Copy Output",
    placement: "top"
  }, CopyButton_jsx(core_["Button"], {
    size: "sm",
    variantColor: bg,
    zIndex: "1",
    onClick: onCopy,
    mx: 1
  }, hasCopied ? CopyButton_jsx(core_["Icon"], {
    name: "check",
    size: "16px"
  }) : CopyButton_jsx(core_["Icon"], {
    name: "copy",
    size: "16px"
  })));
});
// CONCATENATED MODULE: ./components/RequeryButton.js
var RequeryButton_jsx = external_react_default.a.createElement;


/* harmony default export */ var RequeryButton = (({
  isLoading,
  requery,
  bg = "secondary"
}) => {
  return RequeryButton_jsx(core_["Tooltip"], {
    hasArrow: true,
    label: "Reload Query",
    placement: "top"
  }, RequeryButton_jsx(core_["Button"], {
    size: "sm",
    variantColor: bg,
    zIndex: "1",
    onClick: requery,
    mx: 1
  }, isLoading ? RequeryButton_jsx(core_["Spinner"], {
    size: "sm"
  }) : RequeryButton_jsx(core_["Icon"], {
    size: "16px",
    name: "repeat"
  })));
});
// CONCATENATED MODULE: ./components/ResultHeader.js
var ResultHeader_jsx = external_react_default.a.createElement;


/* harmony default export */ var ResultHeader = (external_react_default.a.forwardRef(({
  config,
  title,
  loading,
  error
}, ref) => {
  var _error$response, _error$response$data, _error$response2, _error$response2$data;

  const theme = Object(core_["useTheme"])();
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const statusColor = {
    dark: theme.colors.primary[300],
    light: theme.colors.primary[500]
  };
  const defaultWarningColor = {
    dark: theme.colors.danger[300],
    light: theme.colors.danger[500]
  };
  const warningColor = {
    dark: 300,
    light: 500
  };
  const defaultStatusColor = {
    dark: theme.colors.success[300],
    light: theme.colors.success[500]
  };
  return ResultHeader_jsx(core_["Stack"], {
    ref: ref,
    isInline: true,
    alignItems: "center"
  }, loading ? ResultHeader_jsx(core_["Spinner"], {
    size: "sm",
    mr: 4,
    color: statusColor[colorMode]
  }) : error ? ResultHeader_jsx(core_["Tooltip"], {
    hasArrow: true,
    label: ((_error$response = error.response) === null || _error$response === void 0 ? void 0 : (_error$response$data = _error$response.data) === null || _error$response$data === void 0 ? void 0 : _error$response$data.output) || error.message || config.messages.general,
    placement: "top"
  }, ResultHeader_jsx(core_["Icon"], {
    name: "warning",
    color: error.response ? theme.colors[(_error$response2 = error.response) === null || _error$response2 === void 0 ? void 0 : (_error$response2$data = _error$response2.data) === null || _error$response2$data === void 0 ? void 0 : _error$response2$data.alert][warningColor[colorMode]] : defaultWarningColor[colorMode],
    mr: 4,
    size: 6
  })) : ResultHeader_jsx(core_["Icon"], {
    name: "check",
    color: defaultStatusColor[colorMode],
    mr: 4,
    size: 6
  }), ResultHeader_jsx(core_["Text"], {
    fontSize: "lg"
  }, title));
}));
// CONCATENATED MODULE: ./components/Result.js
var Result_jsx = external_react_default.a.createElement;








const PreBox = styled_default()(core_["Box"])`
    &::selection {
        background-color: ${props => props.selectionBg};
        color: ${props => props.selectionColor};
    }
`;

const FormattedError = ({
  keywords,
  message
}) => {
  const patternStr = `(${keywords.join("|")})`;
  const pattern = new RegExp(patternStr, "gi");
  const errorFmt = external_react_string_replace_default()(message, pattern, match => Result_jsx(core_["Text"], {
    as: "strong"
  }, match));
  return Result_jsx(core_["Text"], null, errorFmt);
};

/* harmony default export */ var Result = (external_react_default.a.forwardRef(({
  config,
  device,
  timeout,
  queryLocation,
  queryType,
  queryVrf,
  queryTarget
}, ref) => {
  var _error$response, _error$response$data, _error$response2, _error$response2$data, _error$response3, _error$response3$data;

  const theme = Object(core_["useTheme"])();
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const bg = {
    dark: theme.colors.gray[800],
    light: theme.colors.blackAlpha[100]
  };
  const color = {
    dark: theme.colors.white,
    light: theme.colors.black
  };
  const selectionBg = {
    dark: theme.colors.white,
    light: theme.colors.black
  };
  const selectionColor = {
    dark: theme.colors.black,
    light: theme.colors.white
  };
  const [{
    data,
    loading,
    error
  }, refetch] = external_axios_hooks_default()({
    url: "/query",
    method: "post",
    data: {
      query_location: queryLocation,
      query_type: queryType,
      query_vrf: queryVrf,
      query_target: queryTarget
    },
    timeout: timeout
  });
  const cleanOutput = data && data.output.split("\\n").join("\n").replace(/\n\n/g, "");
  const errorKw = error && ((_error$response = error.response) === null || _error$response === void 0 ? void 0 : (_error$response$data = _error$response.data) === null || _error$response$data === void 0 ? void 0 : _error$response$data.keywords) || [];
  const errorMsg = error && ((_error$response2 = error.response) === null || _error$response2 === void 0 ? void 0 : (_error$response2$data = _error$response2.data) === null || _error$response2$data === void 0 ? void 0 : _error$response2$data.output) || error && error.message || config.messages.general;
  return Result_jsx(core_["AccordionItem"], {
    isDisabled: loading,
    ref: ref,
    css: {
      "&:last-of-type": {
        borderBottom: "none"
      },
      "&:first-of-type": {
        borderTop: "none"
      }
    }
  }, Result_jsx(core_["AccordionHeader"], {
    justifyContent: "space-between"
  }, Result_jsx(ResultHeader, {
    config: config,
    title: device.display_name,
    loading: loading,
    error: error
  }), Result_jsx(core_["Flex"], null, Result_jsx(core_["AccordionIcon"], null))), Result_jsx(core_["AccordionPanel"], {
    pb: 4
  }, Result_jsx(core_["Box"], {
    position: "relative"
  }, data && Result_jsx(PreBox, {
    fontFamily: "mono",
    mt: 5,
    p: 3,
    border: "1px",
    borderColor: "inherit",
    rounded: "md",
    bg: bg[colorMode],
    color: color[colorMode],
    fontSize: "sm",
    whiteSpace: "pre-wrap",
    as: "pre",
    selectionBg: selectionBg[colorMode],
    selectionColor: selectionColor[colorMode]
  }, cleanOutput), error && Result_jsx(core_["Alert"], {
    rounded: "lg",
    my: 2,
    py: 4,
    status: ((_error$response3 = error.response) === null || _error$response3 === void 0 ? void 0 : (_error$response3$data = _error$response3.data) === null || _error$response3$data === void 0 ? void 0 : _error$response3$data.alert) || "error"
  }, Result_jsx(FormattedError, {
    keywords: errorKw,
    message: errorMsg
  })), Result_jsx(core_["ButtonGroup"], {
    position: "absolute",
    top: 0,
    right: 5,
    py: 3,
    spacing: 4
  }, Result_jsx(CopyButton, {
    copyValue: cleanOutput
  }), Result_jsx(RequeryButton, {
    isLoading: loading,
    requery: refetch
  })))));
}));
// CONCATENATED MODULE: ./components/Results.js


var Results_jsx = external_react_default.a.createElement;





const AnimatedResult = external_framer_motion_["motion"].custom(Result);
const AnimatedLabel = external_framer_motion_["motion"].custom(Label);
/* harmony default export */ var Results = ((_ref) => {
  let {
    config,
    queryLocation,
    queryType,
    queryVrf,
    queryTarget,
    setSubmitting
  } = _ref,
      props = _objectWithoutProperties(_ref, ["config", "queryLocation", "queryType", "queryVrf", "queryTarget", "setSubmitting"]);

  const theme = Object(core_["useTheme"])();
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const matchedVrf = config.vrfs.filter(v => v.id === queryVrf)[0];
  const labelColor = {
    light: theme.colors.white,
    dark: theme.colors.black
  };
  return Results_jsx(external_react_default.a.Fragment, null, Results_jsx(core_["Box"], _extends({
    maxW: ["100%", "100%", "75%", "50%"],
    w: "100%",
    p: 0,
    mx: "auto",
    my: 4,
    textAlign: "left"
  }, props), Results_jsx(core_["Stack"], {
    isInline: true,
    align: "center",
    justify: "center",
    mt: 4
  }, Results_jsx(external_framer_motion_["AnimatePresence"], null, queryLocation && Results_jsx(external_react_default.a.Fragment, null, Results_jsx(AnimatedLabel, {
    initial: {
      opacity: 0,
      x: -100
    },
    animate: {
      opacity: 1,
      x: 0
    },
    transition: {
      duration: 0.3,
      delay: 0.3
    },
    exit: {
      opacity: 0,
      x: -100
    },
    label: config.branding.text.query_type,
    value: config.branding.text[queryType],
    valueBg: theme.colors.cyan[500],
    labelColor: labelColor[colorMode]
  }), Results_jsx(AnimatedLabel, {
    initial: {
      opacity: 0,
      scale: 0.5
    },
    animate: {
      opacity: 1,
      scale: 1
    },
    transition: {
      duration: 0.3,
      delay: 0.3
    },
    exit: {
      opacity: 0,
      scale: 0.5
    },
    label: config.branding.text.query_target,
    value: queryTarget,
    valueBg: theme.colors.teal[600],
    labelColor: labelColor[colorMode]
  }), Results_jsx(AnimatedLabel, {
    initial: {
      opacity: 0,
      x: 100
    },
    animate: {
      opacity: 1,
      x: 0
    },
    transition: {
      duration: 0.3,
      delay: 0.3
    },
    exit: {
      opacity: 0,
      x: 100
    },
    label: config.branding.text.query_vrf,
    value: matchedVrf.display_name,
    valueBg: theme.colors.blue[500],
    labelColor: labelColor[colorMode]
  }))))), Results_jsx(core_["Box"], {
    maxW: ["100%", "100%", "75%", "50%"],
    w: "100%",
    p: 0,
    mx: "auto",
    my: 4,
    textAlign: "left",
    borderWidth: "1px",
    rounded: "lg",
    overflow: "hidden"
  }, Results_jsx(core_["Accordion"], {
    initial: {
      opacity: 1
    },
    transition: {
      duration: 0.3
    },
    animate: {
      opacity: 1,
      y: 0
    },
    exit: {
      opacity: 0,
      y: 300
    }
  }, Results_jsx(external_framer_motion_["AnimatePresence"], null, queryLocation && queryLocation.map((loc, i) => Results_jsx(AnimatedResult, {
    config: config,
    initial: {
      opacity: 0,
      y: 300
    },
    animate: {
      opacity: 1,
      y: 0
    },
    transition: {
      duration: 0.3,
      delay: i * 0.3
    },
    exit: {
      opacity: 0,
      y: 300
    },
    key: loc,
    timeout: config.general.request_timeout * 1000,
    device: config.devices[loc],
    queryLocation: loc,
    queryType: queryType,
    queryVrf: queryVrf,
    queryTarget: queryTarget,
    setSubmitting: setSubmitting
  }))))));
});
// CONCATENATED MODULE: ./components/Header.js
var Header_jsx = external_react_default.a.createElement;



const AnimatedFlex = external_framer_motion_["motion"].custom(core_["Flex"]);
/* harmony default export */ var Header = (() => {
  const theme = Object(core_["useTheme"])();
  const {
    colorMode,
    toggleColorMode
  } = Object(core_["useColorMode"])();
  const bg = {
    light: theme.colors.white,
    dark: theme.colors.black
  };
  const icon = {
    light: "moon",
    dark: "sun"
  };
  return Header_jsx(core_["Flex"], {
    position: "fixed",
    as: "header",
    top: "0",
    zIndex: "4",
    bg: bg[colorMode],
    color: theme.colors.gray[500],
    left: "0",
    right: "0",
    width: "full",
    height: "4rem"
  }, Header_jsx(core_["Flex"], {
    w: "100%",
    mx: "auto",
    px: 6,
    justifyContent: "flex-end"
  }, Header_jsx(AnimatedFlex, {
    align: "center",
    initial: {
      opacity: 0
    },
    animate: {
      opacity: 1
    },
    transition: {
      duration: 0.6
    }
  }, Header_jsx(core_["IconButton"], {
    "aria-label": `Switch to ${colorMode === "light" ? "dark" : "light"} mode`,
    variant: "ghost",
    color: "current",
    ml: "2",
    fontSize: "20px",
    onClick: toggleColorMode,
    icon: icon[colorMode]
  }))));
});
// EXTERNAL MODULE: external "react-icons/go"
var go_ = __webpack_require__("9yvl");

// CONCATENATED MODULE: ./components/FooterButton.js


var FooterButton_jsx = external_react_default.a.createElement;



const FooterButton_AnimatedFlex = external_framer_motion_["motion"].custom(core_["Flex"]);
/* harmony default export */ var FooterButton = (external_react_default.a.forwardRef((_ref, ref) => {
  let {
    onClick,
    side,
    children
  } = _ref,
      props = _objectWithoutProperties(_ref, ["onClick", "side", "children"]);

  return FooterButton_jsx(FooterButton_AnimatedFlex, {
    p: 0,
    w: "auto",
    ref: ref,
    flexGrow: 0,
    float: side,
    flexShrink: 0,
    maxWidth: "100%",
    flexBasis: "auto",
    initial: {
      opacity: 0
    },
    animate: {
      opacity: 1
    },
    transition: {
      duration: 0.6
    }
  }, FooterButton_jsx(core_["Button"], _extends({
    size: "xs",
    variant: "ghost",
    onClick: onClick
  }, props), children));
}));
// CONCATENATED MODULE: ./components/FooterContent.js


var FooterContent_jsx = external_react_default.a.createElement;



/* harmony default export */ var FooterContent = (external_react_default.a.forwardRef((_ref, ref) => {
  let {
    isOpen = false,
    content,
    side = "left",
    title
  } = _ref,
      props = _objectWithoutProperties(_ref, ["isOpen", "content", "side", "title"]);

  return FooterContent_jsx(core_["Collapse"], _extends({
    px: 6,
    py: 4,
    w: "auto",
    ref: ref,
    borderBottom: "1px",
    display: "flex",
    maxWidth: "100%",
    isOpen: isOpen,
    flexBasis: "auto",
    justifyContent: side === "left" ? "flex-start" : "flex-end"
  }, props), FooterContent_jsx(core_["Box"], {
    textAlign: side
  }, FooterContent_jsx(MarkDown, {
    content: content
  })));
}));
// CONCATENATED MODULE: ./components/Footer.js
var Footer_jsx = external_react_default.a.createElement;







external_string_format_default.a.extend(String.prototype, {});
/* harmony default export */ var Footer = (({
  general,
  help,
  extLink,
  credit,
  terms,
  content
}) => {
  const theme = Object(core_["useTheme"])();
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const footerBg = {
    light: theme.colors.blackAlpha[50],
    dark: theme.colors.whiteAlpha[100]
  };
  const footerColor = {
    light: theme.colors.black,
    dark: theme.colors.white
  };
  const contentBorder = {
    light: theme.colors.blackAlpha[100],
    dark: theme.colors.whiteAlpha[200]
  };
  const {
    0: helpVisible,
    1: showHelp
  } = Object(external_react_["useState"])(false);
  const {
    0: termsVisible,
    1: showTerms
  } = Object(external_react_["useState"])(false);
  const {
    0: creditVisible,
    1: showCredit
  } = Object(external_react_["useState"])(false);
  const extUrl = extLink.url.includes("{primary_asn}") ? extLink.url.format({
    primary_asn: general.primary_asn
  }) : extLink.url || "/";

  const handleCollapse = i => {
    if (i === "help") {
      showTerms(false);
      showCredit(false);
      showHelp(!helpVisible);
    } else if (i === "credit") {
      showTerms(false);
      showHelp(false);
      showCredit(!creditVisible);
    } else if (i === "terms") {
      showHelp(false);
      showCredit(false);
      showTerms(!termsVisible);
    }
  };

  return Footer_jsx(external_react_default.a.Fragment, null, help.enable && Footer_jsx(FooterContent, {
    isOpen: helpVisible,
    content: content.help_menu,
    title: help.title,
    bg: footerBg[colorMode],
    borderColor: contentBorder[colorMode],
    side: "left"
  }), terms.enable && Footer_jsx(FooterContent, {
    isOpen: termsVisible,
    content: content.terms,
    title: terms.title,
    bg: footerBg[colorMode],
    borderColor: contentBorder[colorMode],
    side: "left"
  }), credit.enable && Footer_jsx(FooterContent, {
    isOpen: creditVisible,
    content: content.credit,
    title: credit.title,
    bg: footerBg[colorMode],
    borderColor: contentBorder[colorMode],
    side: "right"
  }), Footer_jsx(core_["Flex"], {
    py: 2,
    px: 6,
    w: "100%",
    as: "footer",
    flexWrap: "wrap",
    textAlign: "center",
    alignItems: "center",
    bg: footerBg[colorMode],
    color: footerColor[colorMode],
    justifyContent: "space-between"
  }, terms.enable && Footer_jsx(FooterButton, {
    side: "left",
    onClick: () => handleCollapse("terms")
  }, terms.title), help.enable && Footer_jsx(FooterButton, {
    side: "left",
    onClick: () => handleCollapse("help")
  }, help.title), Footer_jsx(core_["Flex"], {
    flexBasis: "auto",
    flexGrow: 0,
    flexShrink: 0,
    maxWidth: "100%",
    marginRight: "auto",
    p: 0
  }), credit.enable && Footer_jsx(FooterButton, {
    side: "right",
    onClick: () => handleCollapse("credit")
  }, Footer_jsx(fi_["FiCode"], null)), extLink.enable && Footer_jsx(FooterButton, {
    as: "a",
    href: extUrl,
    target: "_blank",
    rel: "noopener noreferrer",
    variant: "ghost",
    rightIcon: go_["GoLinkExternal"],
    size: "xs"
  }, extLink.title)));
});
// CONCATENATED MODULE: ./components/Title.js
var Title_jsx = external_react_default.a.createElement;



const TitleOnly = ({
  text
}) => Title_jsx(core_["Heading"], {
  as: "h1",
  size: "2xl"
}, text);

const SubtitleOnly = ({
  text
}) => Title_jsx(core_["Heading"], {
  as: "h3",
  size: "md"
}, text);

const TextOnly = ({
  text
}) => Title_jsx(core_["Stack"], {
  spacing: 2
}, Title_jsx(TitleOnly, {
  text: text.title
}), Title_jsx(SubtitleOnly, {
  text: text.subtitle
}));

const LogoOnly = ({
  text,
  logo
}) => {
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const logoColor = {
    light: logo.dark,
    dark: logo.light
  };
  const logoPath = logoColor[colorMode];
  return Title_jsx(core_["Image"], {
    src: `http://localhost:8001${logoPath}`,
    alt: text.title,
    w: logo.width,
    h: logo.height || null
  });
};

const LogoTitle = ({
  text,
  logo
}) => Title_jsx(external_react_default.a.Fragment, null, Title_jsx(LogoOnly, {
  text: text,
  logo: logo
}), Title_jsx(SubtitleOnly, {
  text: text.title
}));

const All = ({
  text,
  logo
}) => Title_jsx(external_react_default.a.Fragment, null, Title_jsx(LogoOnly, {
  text: text,
  logo: logo
}), Title_jsx(TextOnly, {
  text: text
}));

const modeMap = {
  text_only: TextOnly,
  logo_only: LogoOnly,
  logo_title: LogoTitle,
  all: All
};
/* harmony default export */ var Title = (external_react_default.a.forwardRef(({
  text,
  logo,
  resetForm
}, ref) => {
  const MatchedMode = modeMap[text.title_mode];
  return Title_jsx(core_["Button"], {
    variant: "link",
    onClick: resetForm,
    _focus: {
      boxShadow: "non"
    }
  }, Title_jsx(core_["Flex"], {
    ref: ref
  }, Title_jsx(MatchedMode, {
    text: text,
    logo: logo
  })));
}));
// EXTERNAL MODULE: external "next/head"
var head_ = __webpack_require__("xnum");
var head_default = /*#__PURE__*/__webpack_require__.n(head_);

// CONCATENATED MODULE: ./components/Meta.js
var Meta_jsx = external_react_default.a.createElement;




/* harmony default export */ var Meta = (({
  config
}) => {
  const theme = Object(core_["useTheme"])();
  const {
    0: location,
    1: setLocation
  } = Object(external_react_["useState"])({});
  const title = (config === null || config === void 0 ? void 0 : config.general.org_name) || "hyperglass";
  const description = (config === null || config === void 0 ? void 0 : config.general.site_description) || "The modern looking glass.";
  const siteName = `${title} - ${description}`;
  const keywords = (config === null || config === void 0 ? void 0 : config.general.site_keywords) || ["hyperglass", "looking glass", "lg", "peer", "peering", "ipv4", "ipv6", "transit", "community", "communities", "bgp", "routing", "network", "isp"];
  const author = (config === null || config === void 0 ? void 0 : config.general.org_name) || "Matt Love, matt@hyperglass.io";
  const language = (config === null || config === void 0 ? void 0 : config.general.language) || "en";
  const currentYear = new Date().getFullYear();
  const copyright = config ? `${currentYear} ${config.general.org_name}` : `${currentYear} hyperglass`;
  const ogImage = (config === null || config === void 0 ? void 0 : config.general.opengraph.image) || null;
  const ogImageHeight = (config === null || config === void 0 ? void 0 : config.general.opengraph.height) || null;
  const ogImageWidth = (config === null || config === void 0 ? void 0 : config.general.opengraph.width) || null;
  const primaryFont = googleFontUrl(theme.fonts.body);
  const monoFont = googleFontUrl(theme.fonts.mono);
  Object(external_react_["useEffect"])(() => {
    setLocation(window.location);
  });
  return Meta_jsx(head_default.a, null, Meta_jsx("title", null, title), Meta_jsx("meta", {
    charSet: "UTF-8"
  }), Meta_jsx("meta", {
    httpEquiv: "Content-Type",
    content: "text/html"
  }), Meta_jsx("meta", {
    name: "description",
    content: description
  }), Meta_jsx("meta", {
    name: "keywords",
    content: keywords.join(", ")
  }), Meta_jsx("meta", {
    name: "author",
    content: author
  }), Meta_jsx("meta", {
    name: "language",
    content: language
  }), Meta_jsx("meta", {
    name: "copyright",
    content: copyright
  }), Meta_jsx("meta", {
    name: "url",
    content: location.href
  }), Meta_jsx("meta", {
    name: "og:title",
    content: title
  }), Meta_jsx("meta", {
    name: "og:type",
    content: "website"
  }), Meta_jsx("meta", {
    name: "og:site_name",
    content: siteName
  }), Meta_jsx("meta", {
    name: "og:url",
    content: location.href
  }), Meta_jsx("meta", {
    name: "og:image",
    content: ogImage
  }), Meta_jsx("meta", {
    name: "og:description",
    content: description
  }), Meta_jsx("meta", {
    property: "og:image:alt",
    content: siteName
  }), Meta_jsx("meta", {
    property: "og:image:width",
    content: ogImageWidth
  }), Meta_jsx("meta", {
    property: "og:image:height",
    content: ogImageHeight
  }), Meta_jsx("link", {
    href: primaryFont,
    rel: "stylesheet"
  }), Meta_jsx("link", {
    href: monoFont,
    rel: "stylesheet"
  }));
});
// CONCATENATED MODULE: ./components/Layout.js
var Layout_jsx = external_react_default.a.createElement;










const AnimatedForm = external_framer_motion_["motion"].custom(HyperglassForm);
const AnimatedTitle = external_framer_motion_["motion"].custom(Title);
const AnimatedResetButton = external_framer_motion_["motion"].custom(ResetButton);
/* harmony default export */ var Layout = (({
  config
}) => {
  const theme = Object(core_["useTheme"])();
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const bg = {
    light: theme.colors.white,
    dark: theme.colors.black
  };
  const color = {
    light: theme.colors.black,
    dark: theme.colors.white
  };
  const {
    0: isSubmitting,
    1: setSubmitting
  } = Object(external_react_["useState"])(false);
  const {
    0: formData,
    1: setFormData
  } = Object(external_react_["useState"])({});

  const handleFormReset = () => {
    setSubmitting(false);
  };

  return Layout_jsx(external_react_default.a.Fragment, null, Layout_jsx(Meta, {
    config: config
  }), Layout_jsx(core_["Flex"], {
    flexDirection: "column",
    minHeight: "100vh",
    w: "100%",
    bg: bg[colorMode],
    color: color[colorMode]
  }, Layout_jsx(Header, null), Layout_jsx(core_["Flex"], {
    as: "main",
    w: "100%",
    flexGrow: 1,
    flexShrink: 1,
    flexBasis: "auto",
    alignItems: "center",
    justifyContent: "start",
    textAlign: "center",
    flexDirection: "column",
    px: 2,
    py: 0,
    mt: ["5%", "5%", "5%", "10%"]
  }, Layout_jsx(external_framer_motion_["AnimatePresence"], null, Layout_jsx(AnimatedTitle, {
    initial: {
      opacity: 0,
      y: -300
    },
    animate: {
      opacity: 1,
      y: 0
    },
    transition: {
      duration: 0.3
    },
    exit: {
      opacity: 0,
      y: -300
    },
    text: config.branding.text,
    logo: config.branding.logo,
    resetForm: handleFormReset
  })), isSubmitting && formData && Layout_jsx(Results, {
    config: config,
    queryLocation: formData.query_location,
    queryType: formData.query_type,
    queryVrf: formData.query_vrf,
    queryTarget: formData.query_target,
    setSubmitting: setSubmitting
  }), Layout_jsx(external_framer_motion_["AnimatePresence"], null, !isSubmitting && Layout_jsx(AnimatedForm, {
    initial: {
      opacity: 0,
      y: 300
    },
    animate: {
      opacity: 1,
      y: 0
    },
    transition: {
      duration: 0.3
    },
    exit: {
      opacity: 0,
      x: -300
    },
    config: config,
    isSubmitting: isSubmitting,
    setSubmitting: setSubmitting,
    setFormData: setFormData
  }))), Layout_jsx(external_framer_motion_["AnimatePresence"], null, isSubmitting && Layout_jsx(AnimatedResetButton, {
    initial: {
      opacity: 0,
      x: -50
    },
    animate: {
      opacity: 1,
      x: 0
    },
    transition: {
      duration: 0.3
    },
    exit: {
      opacity: 0,
      x: -50
    },
    isSubmitting: isSubmitting,
    onClick: handleFormReset
  })), Layout_jsx(Footer, {
    general: config.general,
    content: config.content,
    terms: config.branding.terms,
    help: config.branding.help_menu,
    credit: config.branding.credit,
    extLink: config.branding.external_link
  })));
});
// CONCATENATED MODULE: ./components/PreConfig.js
var PreConfig_jsx = external_react_default.a.createElement;



const ErrorMsg = ({
  title
}) => PreConfig_jsx(external_react_default.a.Fragment, null, PreConfig_jsx(core_["Heading"], {
  mb: 4,
  color: "danger.500",
  as: "h1",
  fontSize: "2xl"
}, title));

const ErrorBtn = ({
  text,
  onClick
}) => PreConfig_jsx(core_["Button"], {
  variant: "outline",
  variantColor: "danger",
  onClick: onClick
}, text);

/* harmony default export */ var PreConfig = (({
  loading,
  error,
  refresh
}) => {
  var _error$response, _error$response$data;

  const theme = Object(core_["useTheme"])();
  const {
    colorMode
  } = Object(core_["useColorMode"])();
  const bg = {
    light: theme.colors.white,
    dark: theme.colors.dark
  };
  const color = {
    light: theme.colors.dark,
    dark: theme.colors.white
  };
  return PreConfig_jsx(core_["Flex"], {
    flexDirection: "column",
    minHeight: "100vh",
    w: "100%",
    bg: bg[colorMode],
    color: color[colorMode]
  }, PreConfig_jsx(core_["Flex"], {
    as: "main",
    w: "100%",
    flexGrow: 1,
    flexShrink: 1,
    flexBasis: "auto",
    alignItems: "center",
    justifyContent: "start",
    textAlign: "center",
    flexDirection: "column",
    px: 2,
    py: 0,
    mt: ["50%", "50%", "50%", "25%"]
  }, loading && PreConfig_jsx(core_["Spinner"], {
    color: "primary.500",
    w: "6rem",
    h: "6rem"
  }), !loading && error && PreConfig_jsx(external_react_default.a.Fragment, null, PreConfig_jsx(ErrorMsg, {
    title: ((_error$response = error.response) === null || _error$response === void 0 ? void 0 : (_error$response$data = _error$response.data) === null || _error$response$data === void 0 ? void 0 : _error$response$data.output) || error.message || "An Error Occurred"
  }), PreConfig_jsx(ErrorBtn, {
    text: "Retry",
    onClick: refresh
  }))));
});
// CONCATENATED MODULE: ./theme.js








function theme_ownKeys(object, enumerableOnly) { var keys = keys_default()(object); if (get_own_property_symbols_default.a) { var symbols = get_own_property_symbols_default()(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return get_own_property_descriptor_default()(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function theme_objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { theme_ownKeys(Object(source), true).forEach(function (key) { Object(defineProperty["a" /* default */])(target, key, source[key]); }); } else if (get_own_property_descriptors_default.a) { define_properties_default()(target, get_own_property_descriptors_default()(source)); } else { theme_ownKeys(Object(source)).forEach(function (key) { define_property_default()(target, key, get_own_property_descriptor_default()(source, key)); }); } } return target; }




const alphaColors = color => ({
  900: external_chroma_js_default()(color).alpha(0.92).css(),
  800: external_chroma_js_default()(color).alpha(0.8).css(),
  700: external_chroma_js_default()(color).alpha(0.6).css(),
  600: external_chroma_js_default()(color).alpha(0.48).css(),
  500: external_chroma_js_default()(color).alpha(0.38).css(),
  400: external_chroma_js_default()(color).alpha(0.24).css(),
  300: external_chroma_js_default()(color).alpha(0.16).css(),
  200: external_chroma_js_default()(color).alpha(0.12).css(),
  100: external_chroma_js_default()(color).alpha(0.08).css(),
  50: external_chroma_js_default()(color).alpha(0.04).css()
});

const generateColors = colorInput => {
  const lightnessMap = [0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.05];
  const saturationMap = [0.32, 0.16, 0.08, 0.04, 0, 0, 0.04, 0.08, 0.16, 0.32];
  const validColor = external_chroma_js_default.a.valid(colorInput.trim()) ? external_chroma_js_default()(colorInput.trim()) : external_chroma_js_default()("#000");
  const lightnessGoal = validColor.get("hsl.l");
  const closestLightness = lightnessMap.reduce((prev, curr) => Math.abs(curr - lightnessGoal) < Math.abs(prev - lightnessGoal) ? curr : prev);
  const baseColorIndex = lightnessMap.findIndex(l => l === closestLightness);
  const colors = lightnessMap.map(l => validColor.set("hsl.l", l)).map(color => external_chroma_js_default()(color)).map((color, i) => {
    const saturationDelta = saturationMap[i] - saturationMap[baseColorIndex];
    return saturationDelta >= 0 ? color.saturate(saturationDelta) : color.desaturate(saturationDelta * -1);
  });

  const getColorNumber = index => index === 0 ? 50 : index * 100;

  const colorMap = {};
  colors.map((color, i) => {
    const colorIndex = getColorNumber(i);
    colorMap[colorIndex] = color.hex();
  });
  return colorMap;
};

const defaultBasePalette = {
  black: "#262626",
  white: "#f7f7f7",
  gray: "#c1c7cc",
  red: "#d84b4b",
  orange: "ff6b35",
  yellow: "#edae49",
  green: "#35b246",
  blue: "#314cb6",
  teal: "#35b299",
  cyan: "#118ab2",
  pink: "#f2607d",
  purple: "#8d30b5"
};
const defaultSwatchPalette = {
  black: defaultBasePalette.black,
  white: defaultBasePalette.white,
  gray: generateColors(defaultBasePalette.gray),
  red: generateColors(defaultBasePalette.red),
  orange: generateColors(defaultBasePalette.orange),
  yellow: generateColors(defaultBasePalette.yellow),
  green: generateColors(defaultBasePalette.green),
  blue: generateColors(defaultBasePalette.blue),
  teal: generateColors(defaultBasePalette.teal),
  cyan: generateColors(defaultBasePalette.cyan),
  pink: generateColors(defaultBasePalette.pink),
  purple: generateColors(defaultBasePalette.purple)
};
const defaultAlphaPalette = {
  blackAlpha: alphaColors(defaultBasePalette.black),
  whiteAlpha: alphaColors(defaultBasePalette.white)
};
const defaultFuncSwatchPalette = {
  primary: generateColors(defaultBasePalette.cyan),
  secondary: generateColors(defaultBasePalette.blue),
  dark: generateColors(defaultBasePalette.black),
  light: generateColors(defaultBasePalette.white),
  success: generateColors(defaultBasePalette.green),
  warning: generateColors(defaultBasePalette.yellow),
  error: generateColors(defaultBasePalette.orange),
  danger: generateColors(defaultBasePalette.red)
};

const defaultColors = theme_objectSpread({
  transparent: "transparent",
  current: "currentColor"
}, defaultFuncSwatchPalette, {}, defaultAlphaPalette, {}, defaultSwatchPalette);

const defaultBodyFonts = ["Nunito", "-apple-system", "BlinkMacSystemFont", '"Segoe UI"', "Helvetica", "Arial", "sans-serif", '"Apple Color Emoji"', '"Segoe UI Emoji"', '"Segoe UI Symbol"'];
const defaultMonoFonts = ['"Fira Code"', "SFMono-Regular", "Melno", "Monaco", "Consolas", '"Liberation Mono"', '"Courier New"', "monospace"];
const defaultFonts = {
  body: defaultBodyFonts.join(", "),
  heading: defaultBodyFonts.join(", "),
  mono: defaultMonoFonts.join(", ")
};

const defaultTheme = theme_objectSpread({}, core_["theme"], {
  colors: defaultColors,
  fonts: defaultFonts
});

const generatePalette = palette => ({
  black: palette.black,
  white: palette.white,
  gray: generateColors(palette.gray),
  red: generateColors(palette.red),
  orange: generateColors(palette.orange),
  yellow: generateColors(palette.yellow),
  green: generateColors(palette.green),
  blue: generateColors(palette.blue),
  teal: generateColors(palette.teal),
  cyan: generateColors(palette.cyan),
  pink: generateColors(palette.pink),
  purple: generateColors(palette.purple)
});

const generateFuncPalette = palette => ({
  primary: generateColors(palette.cyan),
  secondary: generateColors(palette.blue),
  dark: generateColors(palette.black),
  light: generateColors(palette.white),
  success: generateColors(palette.green),
  warning: generateColors(palette.yellow),
  error: generateColors(palette.orange),
  danger: generateColors(palette.red)
});

const generateAlphaPalette = palette => ({
  blackAlpha: alphaColors(palette.black),
  whiteAlpha: alphaColors(palette.white)
});

const importFonts = userFonts => {
  const [body, mono] = [defaultBodyFonts, defaultMonoFonts];
  userFonts.primary.name && body.unshift(`'${userFonts.primary.name}'`);
  userFonts.mono.name && mono.unshift(`'${userFonts.mono.name}'`);
  return {
    body: body.join(", "),
    heading: body.join(", "),
    mono: mono.join(", ")
  };
};

const importColors = (userColors = {}) => {
  const baseColors = theme_objectSpread({}, defaultBasePalette, {}, userColors);

  const swatchColors = generatePalette(baseColors);
  const funcColors = generateFuncPalette(baseColors);
  const bwAlphaColors = generateAlphaPalette(baseColors);
  return theme_objectSpread({
    transparent: "transparent",
    current: "currentColor"
  }, swatchColors, {}, funcColors, {}, bwAlphaColors);
};

const makeTheme = branding => theme_objectSpread({}, core_["theme"], {
  colors: importColors(branding.colors),
  fonts: importFonts(branding.font)
});


// CONCATENATED MODULE: ./pages/index.js
var pages_jsx = external_react_default.a.createElement;






 // Disable SSR for ColorModeProvider

const ColorModeProvider = dynamic_default()(() => Promise.resolve(/* import() */).then(__webpack_require__.t.bind(null, "WKWs", 7)).then(mod => mod.ColorModeProvider), {
  ssr: false,
  loadableGenerated: {
    webpack: () => [/*require.resolve*/("WKWs")],
    modules: ["@chakra-ui/core"]
  }
});

const Index = () => {
  const [{
    data,
    loading,
    error
  }, refetch] = external_axios_hooks_default()({
    url: "/config",
    method: "get"
  }); // const data = undefined;
  // const loading = false;
  // const error = { message: "Shit broke" };
  // const refetch = () => alert("refetched");

  const userTheme = data && makeTheme(data.branding);
  return pages_jsx(core_["ThemeProvider"], {
    theme: data ? userTheme : defaultTheme
  }, pages_jsx(ColorModeProvider, null, pages_jsx(core_["CSSReset"], null), !data ? pages_jsx(PreConfig, {
    loading: loading,
    error: error,
    refresh: refetch
  }) : pages_jsx(Layout, {
    config: data
  })));
};

/* harmony default export */ var pages = __webpack_exports__["default"] = (Index);

/***/ }),

/***/ "TUA0":
/***/ (function(module, exports) {

module.exports = require("core-js/library/fn/object/define-property");

/***/ }),

/***/ "UXZV":
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__("dGr4");

/***/ }),

/***/ "UlNW":
/***/ (function(module, exports) {

module.exports = require("@emotion/styled");

/***/ }),

/***/ "WKWs":
/***/ (function(module, exports) {

module.exports = require("@chakra-ui/core");

/***/ }),

/***/ "XoMD":
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__("QTVn");

/***/ }),

/***/ "YLtl":
/***/ (function(module, exports) {

module.exports = require("lodash");

/***/ }),

/***/ "Z6Kq":
/***/ (function(module, exports) {

module.exports = require("core-js/library/fn/object/get-own-property-descriptor");

/***/ }),

/***/ "cDcd":
/***/ (function(module, exports) {

module.exports = require("react");

/***/ }),

/***/ "dGr4":
/***/ (function(module, exports) {

module.exports = require("core-js/library/fn/object/assign");

/***/ }),

/***/ "hfKm":
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__("TUA0");

/***/ }),

/***/ "id0+":
/***/ (function(module, exports) {

module.exports = require("react-markdown");

/***/ }),

/***/ "k1wZ":
/***/ (function(module, exports) {

module.exports = require("core-js/library/fn/object/get-own-property-symbols");

/***/ }),

/***/ "ltjX":
/***/ (function(module, exports) {

module.exports = require("core-js/library/fn/object/define-properties");

/***/ }),

/***/ "pLtp":
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__("qJj/");

/***/ }),

/***/ "qJj/":
/***/ (function(module, exports) {

module.exports = require("core-js/library/fn/object/keys");

/***/ }),

/***/ "qUDc":
/***/ (function(module, exports) {

module.exports = require("axios-hooks");

/***/ }),

/***/ "vYYK":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return _defineProperty; });
/* harmony import */ var _core_js_object_define_property__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("hfKm");
/* harmony import */ var _core_js_object_define_property__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_core_js_object_define_property__WEBPACK_IMPORTED_MODULE_0__);

function _defineProperty(obj, key, value) {
  if (key in obj) {
    _core_js_object_define_property__WEBPACK_IMPORTED_MODULE_0___default()(obj, key, {
      value: value,
      enumerable: true,
      configurable: true,
      writable: true
    });
  } else {
    obj[key] = value;
  }

  return obj;
}

/***/ }),

/***/ "vtRj":
/***/ (function(module, exports) {

module.exports = require("react-select");

/***/ }),

/***/ "wmQq":
/***/ (function(module, exports) {

module.exports = require("framer-motion");

/***/ }),

/***/ "xnum":
/***/ (function(module, exports) {

module.exports = require("next/head");

/***/ })

/******/ });