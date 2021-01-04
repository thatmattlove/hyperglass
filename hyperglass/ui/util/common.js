'use strict';
var __assign =
  (this && this.__assign) ||
  function () {
    __assign =
      Object.assign ||
      function (t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
          s = arguments[i];
          for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
        }
        return t;
      };
    return __assign.apply(this, arguments);
  };
var __awaiter =
  (this && this.__awaiter) ||
  function (thisArg, _arguments, P, generator) {
    function adopt(value) {
      return value instanceof P
        ? value
        : new P(function (resolve) {
            resolve(value);
          });
    }
    return new (P || (P = Promise))(function (resolve, reject) {
      function fulfilled(value) {
        try {
          step(generator.next(value));
        } catch (e) {
          reject(e);
        }
      }
      function rejected(value) {
        try {
          step(generator['throw'](value));
        } catch (e) {
          reject(e);
        }
      }
      function step(result) {
        result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected);
      }
      step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
  };
var __generator =
  (this && this.__generator) ||
  function (thisArg, body) {
    var _ = {
        label: 0,
        sent: function () {
          if (t[0] & 1) throw t[1];
          return t[1];
        },
        trys: [],
        ops: [],
      },
      f,
      y,
      t,
      g;
    return (
      (g = { next: verb(0), throw: verb(1), return: verb(2) }),
      typeof Symbol === 'function' &&
        (g[Symbol.iterator] = function () {
          return this;
        }),
      g
    );
    function verb(n) {
      return function (v) {
        return step([n, v]);
      };
    }
    function step(op) {
      if (f) throw new TypeError('Generator is already executing.');
      while (_)
        try {
          if (
            ((f = 1),
            y &&
              (t =
                op[0] & 2
                  ? y['return']
                  : op[0]
                  ? y['throw'] || ((t = y['return']) && t.call(y), 0)
                  : y.next) &&
              !(t = t.call(y, op[1])).done)
          )
            return t;
          if (((y = 0), t)) op = [op[0] & 2, t.value];
          switch (op[0]) {
            case 0:
            case 1:
              t = op;
              break;
            case 4:
              _.label++;
              return { value: op[1], done: false };
            case 5:
              _.label++;
              y = op[1];
              op = [0];
              continue;
            case 7:
              op = _.ops.pop();
              _.trys.pop();
              continue;
            default:
              if (
                !((t = _.trys), (t = t.length > 0 && t[t.length - 1])) &&
                (op[0] === 6 || op[0] === 2)
              ) {
                _ = 0;
                continue;
              }
              if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) {
                _.label = op[1];
                break;
              }
              if (op[0] === 6 && _.label < t[1]) {
                _.label = t[1];
                t = op;
                break;
              }
              if (t && _.label < t[2]) {
                _.label = t[2];
                _.ops.push(op);
                break;
              }
              if (t[2]) _.ops.pop();
              _.trys.pop();
              continue;
          }
          op = body.call(thisArg, _);
        } catch (e) {
          op = [6, e];
          y = 0;
        } finally {
          f = t = 0;
        }
      if (op[0] & 5) throw op[1];
      return { value: op[0] ? op[1] : void 0, done: true };
    }
  };
var __rest =
  (this && this.__rest) ||
  function (s, e) {
    var t = {};
    for (var p in s)
      if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0) t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === 'function')
      for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
        if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
          t[p[i]] = s[p[i]];
      }
    return t;
  };
exports.__esModule = true;
exports.fetchWithTimeout = exports.arrangeIntoTree = exports.chunkArray = exports.flatten = exports.all = void 0;
function all() {
  var iter = [];
  for (var _i = 0; _i < arguments.length; _i++) {
    iter[_i] = arguments[_i];
  }
  for (var _a = 0, iter_1 = iter; _a < iter_1.length; _a++) {
    var i = iter_1[_a];
    if (!i) {
      return false;
    }
  }
  return true;
}
exports.all = all;
function flatten(arr) {
  return arr.reduce(function (flat, toFlatten) {
    return flat.concat(Array.isArray(toFlatten) ? flatten(toFlatten) : toFlatten);
  }, []);
}
exports.flatten = flatten;
function chunkArray(array, size) {
  var result = [];
  for (var i = 0; i < array.length; i += size) {
    var chunk = array.slice(i, i + size);
    result.push(chunk);
  }
  return result;
}
exports.chunkArray = chunkArray;
/**
 * Arrange an array of arrays into a tree of nodes.
 *
 * Blatantly stolen from:
 * @see https://gist.github.com/stephanbogner/4b590f992ead470658a5ebf09167b03d
 */
function arrangeIntoTree(paths) {
  var tree = [];
  for (var i = 0; i < paths.length; i++) {
    var path = paths[i];
    var currentLevel = tree;
    for (var j = 0; j < path.length; j++) {
      var part = path[j];
      var existingPath = findWhere(currentLevel, 'base', part);
      if (existingPath !== false) {
        currentLevel = existingPath.children;
      } else {
        var newPart = {
          base: part,
          children: [],
        };
        currentLevel.push(newPart);
        currentLevel = newPart.children;
      }
    }
  }
  return tree;
  function findWhere(array, idx, value) {
    var t = 0;
    while (t < array.length && array[t][idx] !== value) {
      t++;
    }
    if (t < array.length) {
      return array[t];
    } else {
      return false;
    }
  }
}
exports.arrangeIntoTree = arrangeIntoTree;
/**
 * Fetch Wrapper that incorporates a timeout via a passed AbortController instance.
 *
 * Adapted from: https://lowmess.com/blog/fetch-with-timeout
 */
function fetchWithTimeout(uri, options, timeout, controller) {
  if (options === void 0) {
    options = {};
  }
  return __awaiter(this, void 0, void 0, function () {
    var _a, signal, allOptions, config;
    return __generator(this, function (_b) {
      switch (_b.label) {
        case 0:
          (_a = options.signal),
            (signal = _a === void 0 ? new AbortController().signal : _a),
            (allOptions = __rest(options, ['signal']));
          config = __assign(__assign({}, allOptions), { signal: signal });
          /**
           * Set a timeout limit for the request using `setTimeout`. If the body of this timeout is
           * reached before the request is completed, it will be cancelled.
           */
          setTimeout(function () {
            controller.abort();
          }, timeout);
          return [4 /*yield*/, fetch(uri, config)];
        case 1:
          return [2 /*return*/, _b.sent()];
      }
    });
  });
}
exports.fetchWithTimeout = fetchWithTimeout;
