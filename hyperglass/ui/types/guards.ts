import type { State } from '@hookstate/core';
import type { FormData, TStringTableData, TQueryResponseString } from './data';
import type { TSelectOption } from './common';
import type { QueryContent, DirectiveSelect, Directive } from './config';

export function isString(a: unknown): a is string {
  return typeof a === 'string';
}

/**
 * Type Guard to determine if an argument is an object, e.g. `{}` (`Record<string, unknown>`).
 * Maintains type of object if a type argument is provided.
 */
export function isObject<T extends unknown = unknown>(
  obj: unknown,
): obj is { [P in keyof T]: T[P] } {
  return typeof obj === 'object' && obj !== null && !Array.isArray(obj);
}

export function isStructuredOutput(data: unknown): data is TStringTableData {
  return isObject(data) && 'output' in data;
}

export function isStringOutput(data: unknown): data is TQueryResponseString {
  return (
    isObject(data) && 'output' in data && typeof (data as { output: unknown }).output === 'string'
  );
}

export function isQueryContent(content: unknown): content is QueryContent {
  return isObject(content) && 'content' in content;
}

/**
 * Determine if an object is a Select option.
 */
export function isSelectOption(a: unknown): a is NonNullable<TSelectOption> {
  return isObject(a) && 'label' in a && 'value' in a;
}

/**
 * Determine if an object is a HookState Proxy.
 */
export function isState<S>(a: unknown): a is State<NonNullable<S>> {
  if (isObject(a) && 'get' in a && 'set' in a && 'promised' in a) {
    const obj = a as { get: never; set: never; promised: never };
    return typeof obj.get === 'function' && typeof obj.set === 'function';
  }
  return false;
}

/**
 * Determine if a form field name is a valid form key name.
 */
export function isQueryField(field: string): field is keyof FormData {
  return ['queryLocation', 'queryType', 'queryGroup', 'queryTarget'].includes(field);
}

/**
 * Determine if a directive is a select directive.
 */
export function isSelectDirective(directive: Directive): directive is DirectiveSelect {
  return directive.fieldType === 'select';
}
