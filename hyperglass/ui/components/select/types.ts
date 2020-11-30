import type {
  Props as IReactSelect,
  ControlProps,
  MenuProps,
  MenuListComponentProps,
  OptionProps,
  MultiValueProps,
  IndicatorProps,
  Theme,
  PlaceholderProps,
} from 'react-select';
import type { BoxProps } from '@chakra-ui/react';
import type { ColorNames } from '~/types';

export interface TSelectState {
  [k: string]: string[];
}

export type TSelectOption = {
  label: string;
  value: string;
};

export type TSelectOptionGroup = {
  label: string;
  options: TSelectOption[];
};

export type TOptions = Array<TSelectOptionGroup | TSelectOption>;

export type TBoxAsReactSelect = Omit<IReactSelect, 'isMulti' | 'onSelect' | 'onChange'> &
  Omit<BoxProps, 'onChange' | 'onSelect'>;

export interface TSelect extends TBoxAsReactSelect {
  options: TOptions;
  name: string;
  required?: boolean;
  multi?: boolean;
  onSelect?: (v: TSelectOption[]) => void;
  onChange?: (c: TSelectOption | TSelectOption[]) => void;
  colorScheme?: ColorNames;
}

export interface TSelectContext {
  colorMode: 'light' | 'dark';
  isOpen: boolean;
}

export interface TMultiValueRemoveProps {
  children: Node;
  data: any;
  innerProps: {
    className: string;
    onTouchEnd: (e: any) => void;
    onClick: (e: any) => void;
    onMouseDown: (e: any) => void;
  };
  selectProps: any;
}

export interface TRSTheme extends Omit<Theme, 'borderRadius'> {
  borderRadius: string | number;
}

export type TControl = ControlProps<TOptions>;

export type TMenu = MenuProps<TOptions>;

export type TMenuList = MenuListComponentProps<TOptions>;

export type TOption = OptionProps<TOptions>;

export type TMultiValueState = MultiValueProps<TOptions>;

export type TIndicator = IndicatorProps<TOptions>;

export type TPlaceholder = PlaceholderProps<TOptions>;

export type TMultiValue = Pick<TSelectContext, 'colorMode'>;

export type { Styles as TStyles } from 'react-select';
