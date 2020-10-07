import * as React from 'react';
import {
  Checkbox as ChakraCheckbox,
  Divider as ChakraDivider,
  Code as ChakraCode,
  Heading as ChakraHeading,
  Link as ChakraLink,
  List as ChakraList,
  ListItem as ChakraListItem,
  Text as ChakraText,
} from '@chakra-ui/core';

import { TableCell, TableHeader, Table as ChakraTable } from './MDTable';

import { CodeBlock as CustomCodeBlock } from 'app/components';

export const Checkbox = ({ checked, children }) => (
  <ChakraCheckbox isChecked={checked}>{children}</ChakraCheckbox>
);

export const List = ({ ordered, children }) => (
  <ChakraList as={ordered ? 'ol' : 'ul'}>{children}</ChakraList>
);

export const ListItem = ({ checked, children }) =>
  checked ? (
    <Checkbox checked={checked}>{children}</Checkbox>
  ) : (
    <ChakraListItem>{children}</ChakraListItem>
  );

export const Heading = ({ level, children }) => {
  const levelMap = {
    1: { as: 'h1', size: 'lg', fontWeight: 'bold' },
    2: { as: 'h2', size: 'lg', fontWeight: 'normal' },
    3: { as: 'h3', size: 'lg', fontWeight: 'bold' },
    4: { as: 'h4', size: 'md', fontWeight: 'normal' },
    5: { as: 'h5', size: 'md', fontWeight: 'bold' },
    6: { as: 'h6', size: 'sm', fontWeight: 'bold' },
  };
  return <ChakraHeading {...levelMap[level]}>{children}</ChakraHeading>;
};

export const Link = ({ children, ...props }) => (
  <ChakraLink isExternal {...props}>
    {children}
  </ChakraLink>
);

export const CodeBlock = ({ value }) => <CustomCodeBlock>{value}</CustomCodeBlock>;

export const TableData = ({ isHeader, children, ...props }) => {
  const Component = isHeader ? TableHeader : TableCell;
  return <Component {...props}>{children}</Component>;
};

export const Paragraph = props => <ChakraText {...props} />;
export const InlineCode = props => <ChakraCode {...props} />;
export const Divider = props => <ChakraDivider {...props} />;
export const Table = props => <ChakraTable {...props} />;
