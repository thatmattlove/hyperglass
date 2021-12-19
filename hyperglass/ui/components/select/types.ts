import * as ReactSelect from 'react-select';

import type { StylesProps, StylesConfigFunction } from 'react-select/dist/declarations/src/styles';
import type { Theme, SingleOption } from '~/types';

export type SelectOnChange<
  Opt extends SingleOption = SingleOption,
  IsMulti extends boolean = boolean,
> = NonNullable<Get<ReactSelect.Props<Opt, IsMulti>, 'onChange'>>;

export interface SelectProps<Opt extends SingleOption, IsMulti extends boolean>
  extends ReactSelect.Props<Opt, IsMulti> {
  name: string;
  isMulti?: IsMulti;
  isError?: boolean;
  required?: boolean;
  onSelect?: (s: ReactSelect.MultiValue<Opt>) => void;
  colorScheme?: Theme.ColorNames;
}

export interface SelectContextProps {
  colorMode: 'light' | 'dark';
  isOpen: boolean;
  isError: boolean;
}

export interface RSStyleCallbackProps {
  colorMode: 'light' | 'dark';
}

type StyleConfigKeys = keyof ReactSelect.StylesConfig<
  SingleOption,
  boolean,
  ReactSelect.GroupBase<SingleOption>
>;

export type RSStyleFunction<
  K extends StyleConfigKeys,
  Opt extends SingleOption,
  IsMulti extends boolean,
> = StylesConfigFunction<StylesProps<Opt, IsMulti, ReactSelect.GroupBase<Opt>>[K]>;

export type RSThemeFunction = (theme: ReactSelect.Theme) => ReactSelect.Theme;

export function isSingleValue<Opt extends SingleOption>(
  value: ReactSelect.SingleValue<Opt> | ReactSelect.MultiValue<Opt>,
): value is NonNullable<ReactSelect.SingleValue<Opt>> {
  return value !== null && !Array.isArray(value);
}

export function isMultiValue<Opt extends SingleOption>(
  value: ReactSelect.SingleValue<Opt> | ReactSelect.MultiValue<Opt>,
): value is NonNullable<ReactSelect.MultiValue<Opt>> {
  return value !== null && Array.isArray(value);
}
