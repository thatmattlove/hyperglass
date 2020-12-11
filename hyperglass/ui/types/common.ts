export type TSelectOption = {
  label: string;
  value: string | string[];
};

export type TSelectOptionGroup = {
  label: string;
  options: TSelectOption[];
};

export type OnChangeArgs = { field: string; value: string | string[] };

export type Families = [4] | [6] | [4, 6] | [];
