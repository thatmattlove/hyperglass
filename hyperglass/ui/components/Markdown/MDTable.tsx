import { Box } from '@chakra-ui/core';
import { useColorValue } from '~/context';
import type { BoxProps } from '@chakra-ui/core';
import type { ITableData } from './types';

export const Table = (props: BoxProps) => (
  <Box as="table" textAlign="left" mt={4} width="full" {...props} />
);

export const TableHeader = (props: BoxProps) => {
  const bg = useColorValue('blackAlpha.50', 'whiteAlpha.50');
  return <Box as="th" bg={bg} fontWeight="semibold" p={2} fontSize="sm" {...props} />;
};

export const TableCell = (props: ITableData) => {
  const { isHeader = false, ...rest } = props;
  return (
    <Box
      as={isHeader ? 'th' : 'td'}
      p={2}
      borderTopWidth="1px"
      borderColor="inherit"
      fontSize="sm"
      whiteSpace="normal"
      {...rest}
    />
  );
};
