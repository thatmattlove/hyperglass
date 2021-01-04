import { Box } from '@chakra-ui/react';
import { useColorValue } from '~/context';

import type { BoxProps } from '@chakra-ui/react';

export const Table: React.FC<BoxProps> = (props: BoxProps) => (
  <Box as="table" textAlign="left" mt={4} width="full" {...props} />
);

export const TH: React.FC<BoxProps> = (props: BoxProps) => {
  const bg = useColorValue('blackAlpha.50', 'whiteAlpha.50');
  return <Box as="th" bg={bg} fontWeight="semibold" p={2} fontSize="sm" {...props} />;
};

export const TD: React.FC<BoxProps> = (props: BoxProps) => {
  return (
    <Box
      p={2}
      as="td"
      fontSize="sm"
      whiteSpace="normal"
      borderTopWidth="1px"
      borderColor="inherit"
      {...props}
    />
  );
};
