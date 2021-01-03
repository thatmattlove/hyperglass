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

export const Checkbox = (props: TCheckbox & MDProps) => {
  const { checked, node, ...rest } = props;
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

export const ListItem = (props: TListItem & MDProps) => {
  const { checked, node, ...rest } = props;
  return checked ? (
    <Checkbox checked={checked} node={node} {...rest} />
  ) : (
    <ChakraListItem {...rest} />
  );
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

  return <ChakraHeading {...levelMap[level]} {...clean<Omit<THeading, 'level'>>(rest)} />;
};

export const Link = (props: LinkProps) => {
  const color = useColorValue('blue.500', 'blue.300');
  return <ChakraLink isExternal color={color} {...clean<LinkProps>(props)} />;
};

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

export const Paragraph = (props: TextProps) => (
  <ChakraText
    my={4}
    css={{
      '&:first-of-type': { marginTop: useToken('space', 2) },
      '&:last-of-type': { marginBottom: 0 },
    }}
    {...clean<TextProps>(props)}
  />
);
export const InlineCode = (props: CodeProps) => (
  <ChakraCode borderRadius="md" px={1} {...clean<CodeProps>(props)} />
);
export const Divider = (props: DividerProps) => (
  <ChakraDivider my={2} {...clean<DividerProps>(props)} />
);
export const Table = (props: BoxProps) => <ChakraTable {...clean<BoxProps>(props)} />;
export const Br = (props: BoxProps) => <Box as="br" m={16} {...clean<BoxProps>(props)} />;
