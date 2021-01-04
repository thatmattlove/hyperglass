import type { BoxProps, CheckboxProps, HeadingProps, ListProps } from '@chakra-ui/react';

export interface TMarkdown {
  content: string;
}

export interface TCheckbox extends CheckboxProps {
  checked: boolean;
}

export interface TListItem {
  checked: boolean;
  children?: React.ReactNode;
}

export interface TList extends ListProps {
  ordered: boolean;
  children?: React.ReactNode;
}

export interface THeading extends HeadingProps {
  level: 1 | 2 | 3 | 4 | 5 | 6;
}

export interface TCodeBlock {
  value: React.ReactNode;
}

export interface TTableData extends BoxProps {
  isHeader: boolean;
}
