import {
  OrderedList,
  UnorderedList,
  Code as ChakraCode,
  Link as ChakraLink,
  Text as ChakraText,
  Divider as ChakraDivider,
  Heading as ChakraHeading,
  Checkbox as ChakraCheckbox,
  ListItem as ChakraListItem,
} from '@chakra-ui/react';

import { TD, TH, Table as ChakraTable } from './table';

import { CodeBlock as CustomCodeBlock, If } from '~/components';

import type {
  BoxProps,
  TextProps,
  CodeProps,
  LinkProps,
  HeadingProps,
  DividerProps,
} from '@chakra-ui/react';
import type { TCheckbox, TList, THeading, TCodeBlock, TTableData, TListItem } from './types';

export const Checkbox = (props: TCheckbox) => {
  const { checked, ...rest } = props;
  return <ChakraCheckbox isChecked={checked} {...rest} />;
};

export const List = (props: TList) => {
  const { ordered, ...rest } = props;
  return (
    <>
      <If c={ordered}>
        <OrderedList {...rest} />
      </If>
      <If c={!ordered}>
        <UnorderedList {...rest} />
      </If>
    </>
  );
};

export const ListItem = (props: TListItem) => {
  const { checked, ...rest } = props;
  return checked ? <Checkbox checked={checked} {...rest} /> : <ChakraListItem {...rest} />;
};

export const Heading = (props: THeading) => {
  const { level, ...rest } = props;

  const levelMap = {
    1: { as: 'h1', size: 'lg', fontWeight: 'bold' },
    2: { as: 'h2', size: 'lg', fontWeight: 'normal' },
    3: { as: 'h3', size: 'lg', fontWeight: 'bold' },
    4: { as: 'h4', size: 'md', fontWeight: 'normal' },
    5: { as: 'h5', size: 'md', fontWeight: 'bold' },
    6: { as: 'h6', size: 'sm', fontWeight: 'bold' },
  } as { [i: number]: HeadingProps };

  return <ChakraHeading {...levelMap[level]} {...rest} />;
};

export const Link = (props: LinkProps) => <ChakraLink isExternal {...props} />;

export const CodeBlock = (props: TCodeBlock) => <CustomCodeBlock>{props.value}</CustomCodeBlock>;

export const TableData = (props: TTableData) => {
  const { isHeader, ...rest } = props;
  return (
    <>
      <If c={isHeader}>
        <TH {...rest} />
      </If>
      <If c={!isHeader}>
        <TD {...rest} />
      </If>
    </>
  );
};

export const Paragraph = (props: TextProps) => <ChakraText {...props} />;
export const InlineCode = (props: CodeProps) => <ChakraCode children={props.children} />;
export const Divider = (props: DividerProps) => <ChakraDivider {...props} />;
export const Table = (props: BoxProps) => <ChakraTable {...props} />;
