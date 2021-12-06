interface AnyOption {
  label: string;
}

export interface SingleOption<T extends Record<string, unknown> = Record<string, unknown>>
  extends AnyOption {
  value: string;
  group?: string;
  tags?: string[];
  data?: T;
}

export interface OptionGroup<Opt extends SingleOption> extends AnyOption {
  options: Opt[];
}

export type OptionsOrGroup<Opt extends SingleOption> = Array<Opt | OptionGroup<Opt>>;

export type OnChangeArgs = { field: string; value: string | string[] };
