import type { ReactNode } from 'react';
import type { BoxProps, CheckboxProps, HeadingProps } from '@chakra-ui/core';
export interface IMarkdown {
  content: string;
}
export interface ICheckbox extends CheckboxProps {
  checked: boolean;
}

export interface IList {
  ordered: boolean;
  children?: ReactNode;
}
export interface IHeading extends HeadingProps {
  level: 1 | 2 | 3 | 4 | 5 | 6;
}

export interface ICodeBlock {
  value: ReactNode;
}

export interface ITableData extends BoxProps {
  isHeader: boolean;
}
