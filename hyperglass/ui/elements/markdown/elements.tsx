import {
  Th,
  Tr,
  Td,
  Box,
  Tbody,
  Thead,
  useToken,
  OrderedList,
  UnorderedList,
  Code as ChakraCode,
  Link as ChakraLink,
  Text as ChakraText,
  Table as ChakraTable,
  Divider as ChakraDivider,
  Heading as ChakraHeading,
  Checkbox as ChakraCheckbox,
  ListItem as ChakraListItem,
} from '@chakra-ui/react';
import { If, Then, Else } from 'react-if';
import { CodeBlock as CustomCodeBlock } from '~/elements';
import { useColorValue } from '~/hooks';

import type {
  BoxProps,
  CodeProps,
  LinkProps,
  TextProps,
  TableProps,
  ChakraProps,
  DividerProps,
  TableRowProps,
  TableBodyProps,
  TableHeadProps,
  ListProps as ChakraListProps,
  HeadingProps as ChakraHeadingProps,
  CheckboxProps as ChakraCheckboxProps,
  TableCellProps as ChakraTableCellProps,
} from '@chakra-ui/react';

interface CheckboxProps extends ChakraCheckboxProps {
  checked: boolean;
}

interface ListItemProps {
  checked: boolean;
  children?: React.ReactNode;
}

interface ListProps extends ChakraListProps {
  ordered: boolean;
  children?: React.ReactNode;
}

interface HeadingProps extends ChakraHeadingProps {
  level: 1 | 2 | 3 | 4 | 5 | 6;
}

interface CodeBlockProps {
  value: React.ReactNode;
}

interface TableCellProps extends BoxProps {
  isHeader: boolean;
}

type MDProps = {
  node: Dict;
};

// biome-ignore lint/suspicious/noExplicitAny: reasons!
function hasNode<C>(p: any): p is C & MDProps {
  return 'node' in p;
}

function clean<P extends ChakraProps>(props: P): P {
  if (hasNode<P>(props)) {
    const { node, ...rest } = props;
    const r = rest as unknown as P;
    return r;
  }
  return props;
}

export const Checkbox = (props: CheckboxProps & MDProps): JSX.Element => {
  const { checked, node, ...rest } = props;
  return <ChakraCheckbox isChecked={checked} {...rest} />;
};

export const List = (props: ListProps): JSX.Element => {
  const { ordered, ...rest } = props;
  return (
    <If condition={ordered}>
      <Then>
        <OrderedList {...rest} />
      </Then>
      <Else>
        <UnorderedList {...rest} />
      </Else>
    </If>
  );
};

export const ListItem = (props: ListItemProps & MDProps): JSX.Element => {
  const { checked, node, ...rest } = props;
  return checked ? (
    <Checkbox checked={checked} node={node} {...rest} />
  ) : (
    <ChakraListItem {...rest} />
  );
};

export const Heading = (props: HeadingProps): JSX.Element => {
  const { level, ...rest } = props;

  const levelMap = {
    1: { as: 'h1', size: 'lg', fontWeight: 'bold' },
    2: { as: 'h2', size: 'lg', fontWeight: 'normal' },
    3: { as: 'h3', size: 'lg', fontWeight: 'bold' },
    4: { as: 'h4', size: 'md', fontWeight: 'normal' },
    5: { as: 'h5', size: 'md', fontWeight: 'bold' },
    6: { as: 'h6', size: 'sm', fontWeight: 'bold' },
  } as { [i: number]: ChakraHeadingProps };

  return <ChakraHeading {...levelMap[level]} {...clean<Omit<HeadingProps, 'level'>>(rest)} />;
};

export const Link = (props: LinkProps): JSX.Element => {
  const color = useColorValue('blue.500', 'blue.300');
  return <ChakraLink isExternal color={color} {...clean<LinkProps>(props)} />;
};

export const CodeBlock = (props: CodeBlockProps): JSX.Element => (
  <CustomCodeBlock>{props.value}</CustomCodeBlock>
);

export const Paragraph = (props: TextProps): JSX.Element => (
  <ChakraText
    my={4}
    css={{
      '&:first-of-type': { marginTop: useToken('space', 2) },
      '&:last-of-type': { marginBottom: 0 },
    }}
    {...clean<TextProps>(props)}
  />
);

export const InlineCode = (props: CodeProps): JSX.Element => (
  <ChakraCode borderRadius="md" px={1} {...clean<CodeProps>(props)} />
);

export const Divider = (props: DividerProps): JSX.Element => (
  <ChakraDivider my={2} {...clean<DividerProps>(props)} />
);

export const Table = (props: TableProps): JSX.Element => (
  <ChakraTable my={4} variant="simple" size="md" {...clean<TableProps>(props)} />
);

export const TableRow = (props: TableRowProps): JSX.Element => (
  <Tr {...clean<TableRowProps>(props)} />
);

export const TableBody = (props: TableBodyProps): JSX.Element => (
  <Tbody {...clean<TableBodyProps>(props)} />
);

export const TableHead = (props: TableHeadProps): JSX.Element => (
  <Thead {...clean<TableHeadProps>(props)} />
);

export const TableCell = (props: TableCellProps): JSX.Element => {
  const { isHeader, ...rest } = props;
  return (
    <If condition={isHeader}>
      <Then>
        <Th {...clean<ChakraTableCellProps>(rest)} />
      </Then>
      <Else>
        <Td {...clean<ChakraTableCellProps>(rest)} />
      </Else>
    </If>
  );
};

export const Br = (props: BoxProps): JSX.Element => (
  <Box as="br" m={16} {...clean<BoxProps>(props)} />
);
