import {
  Box,
  OrderedList,
  UnorderedList,
  Code as ChakraCode,
  Link as ChakraLink,
  Text as ChakraText,
  Divider as ChakraDivider,
  Heading as ChakraHeading,
  Checkbox as ChakraCheckbox,
  ListItem as ChakraListItem,
  useToken,
} from '@chakra-ui/react';

import { CodeBlock as CustomCodeBlock, If } from '~/components';
import { useColorValue } from '~/context';
import { TD, TH, Table as ChakraTable } from './table';

import type {
  BoxProps,
  TextProps,
  CodeProps,
  LinkProps,
  ChakraProps,
  HeadingProps,
  DividerProps,
} from '@chakra-ui/react';
import type { TCheckbox, TList, THeading, TCodeBlock, TTableData, TListItem } from './types';

type MDProps = {
  node: Dict;
};

/* eslint @typescript-eslint/no-explicit-any: off */
function hasNode<C>(p: any): p is C & MDProps {
  return 'node' in p;
}

function clean<P extends ChakraProps>(props: P): P {
  if (hasNode<P>(props)) {
    const { node, ...rest } = props;
    const r = (rest as unknown) as P;
    return r;
  }
  return props;
}

export const Checkbox: React.FC<TCheckbox & MDProps> = (props: TCheckbox & MDProps) => {
  const { checked, node, ...rest } = props;
  return <ChakraCheckbox isChecked={checked} {...rest} />;
};

export const List: React.FC<TList> = (props: TList) => {
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

export const ListItem: React.FC<TListItem & MDProps> = (props: TListItem & MDProps) => {
  const { checked, node, ...rest } = props;
  return checked ? (
    <Checkbox checked={checked} node={node} {...rest} />
  ) : (
    <ChakraListItem {...rest} />
  );
};

export const Heading: React.FC<THeading> = (props: THeading) => {
  const { level, ...rest } = props;

  const levelMap = {
    1: { as: 'h1', size: 'lg', fontWeight: 'bold' },
    2: { as: 'h2', size: 'lg', fontWeight: 'normal' },
    3: { as: 'h3', size: 'lg', fontWeight: 'bold' },
    4: { as: 'h4', size: 'md', fontWeight: 'normal' },
    5: { as: 'h5', size: 'md', fontWeight: 'bold' },
    6: { as: 'h6', size: 'sm', fontWeight: 'bold' },
  } as { [i: number]: HeadingProps };

  return <ChakraHeading {...levelMap[level]} {...clean<Omit<THeading, 'level'>>(rest)} />;
};

export const Link: React.FC<LinkProps> = (props: LinkProps) => {
  const color = useColorValue('blue.500', 'blue.300');
  return <ChakraLink isExternal color={color} {...clean<LinkProps>(props)} />;
};

export const CodeBlock: React.FC<TCodeBlock> = (props: TCodeBlock) => (
  <CustomCodeBlock>{props.value}</CustomCodeBlock>
);

export const TableData: React.FC<TTableData> = (props: TTableData) => {
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

export const Paragraph: React.FC<TextProps> = (props: TextProps) => (
  <ChakraText
    my={4}
    css={{
      '&:first-of-type': { marginTop: useToken('space', 2) },
      '&:last-of-type': { marginBottom: 0 },
    }}
    {...clean<TextProps>(props)}
  />
);

export const InlineCode: React.FC<CodeProps> = (props: CodeProps) => (
  <ChakraCode borderRadius="md" px={1} {...clean<CodeProps>(props)} />
);

export const Divider: React.FC<DividerProps> = (props: DividerProps) => (
  <ChakraDivider my={2} {...clean<DividerProps>(props)} />
);

export const Table: React.FC<BoxProps> = (props: BoxProps) => (
  <ChakraTable {...clean<BoxProps>(props)} />
);

export const Br: React.FC<BoxProps> = (props: BoxProps) => (
  <Box as="br" m={16} {...clean<BoxProps>(props)} />
);
