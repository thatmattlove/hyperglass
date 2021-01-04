import { Box } from '@chakra-ui/react';
import { useColorValue } from '~/context';

import type { BoxProps } from '@chakra-ui/react';

export const CodeBlock: React.FC<BoxProps> = (props: BoxProps) => {
  const bg = useColorValue('blackAlpha.100', 'gray.800');
  const color = useColorValue('black', 'white');
  return (
    <Box
      p={3}
      mt={5}
      bg={bg}
      as="pre"
      border="1px"
      rounded="md"
      color={color}
      fontSize="sm"
      fontFamily="mono"
      borderColor="inherit"
      whiteSpace="pre-wrap"
      {...props}
    />
  );
};
