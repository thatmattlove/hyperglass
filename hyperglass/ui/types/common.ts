type AnyOption = {
  label: string;
};

export type SingleOption = AnyOption & {
  value: string;
  group?: string;
  tags?: string[];
};

export type OptionGroup = AnyOption & {
  options: SingleOption[];
};

export type SelectOption<T extends unknown = unknown> = (SingleOption | OptionGroup) & { data: T };

export type OnChangeArgs = { field: string; value: string | string[] };
