import { State } from '@hookstate/core';

export type TSelectOptionBase = {
  label: string;
  value: string;
  group?: string;
};

export type TSelectOption = TSelectOptionBase | null;

export type TSelectOptionMulti = TSelectOptionBase[] | null;

export type TSelectOptionState = State<TSelectOption>;

export type TSelectOptionGroup = {
  label: string;
  options: TSelectOption[];
};

export type OnChangeArgs = { field: string; value: string | string[] };

export type Families = [4] | [6] | [4, 6] | [];
