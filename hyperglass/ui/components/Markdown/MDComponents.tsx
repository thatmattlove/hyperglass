import {
  Checkbox as ChakraCheckbox,
  Divider as ChakraDivider,
  Code as ChakraCode,
  Heading as ChakraHeading,
  Link as ChakraLink,
  ListItem as ChakraListItem,
  Text as ChakraText,
  UnorderedList,
  OrderedList,
} from '@chakra-ui/core';

import { TableCell, TableHeader, Table as ChakraTable } from './MDTable';

import { CodeBlock as CustomCodeBlock } from '~/components';

import type { BoxProps, TextProps, CodeProps, DividerProps, LinkProps } from '@chakra-ui/core';
import type { ICheckbox, IList, IHeading, ICodeBlock, ITableData } from './types';

export const Checkbox = (props: ICheckbox) => {
  const { checked, ...rest } = props;
  return <ChakraCheckbox isChecked={checked} {...rest} />;
};

export const List = (props: IList) => {
  const { ordered, ...rest } = props;
  const Component = ordered ? OrderedList : UnorderedList;
  return <Component {...rest} />;
};

export const ListItem = (props: ICheckbox) => {
  const { checked, ...rest } = props;
  return checked ? <Checkbox checked={checked} {...rest} /> : <ChakraListItem {...rest} />;
};

export const Heading = (props: IHeading) => {
  const { level, ...rest } = props;
  const levelMap = {
    1: { as: 'h1', size: 'lg', fontWeight: 'bold' },
    2: { as: 'h2', size: 'lg', fontWeight: 'normal' },
    3: { as: 'h3', size: 'lg', fontWeight: 'bold' },
    4: { as: 'h4', size: 'md', fontWeight: 'normal' },
    5: { as: 'h5', size: 'md', fontWeight: 'bold' },
    6: { as: 'h6', size: 'sm', fontWeight: 'bold' },
  };
  return <ChakraHeading {...levelMap[level]} {...rest} />;
};

export const Link = (props: LinkProps) => <ChakraLink isExternal {...props} />;

export const CodeBlock = (props: ICodeBlock) => <CustomCodeBlock>{props.value}</CustomCodeBlock>;

export const TableData = (props: ITableData) => {
  const { isHeader, ...rest } = props;
  const Component = isHeader ? TableHeader : TableCell;
  return <Component {...rest} />;
};

export const Paragraph = (props: TextProps) => <ChakraText {...props} />;
export const InlineCode = (props: CodeProps) => <ChakraCode {...props} />;
export const Divider = (props: DividerProps) => <ChakraDivider {...props} />;
export const Table = (props: BoxProps) => <ChakraTable {...props} />;
