import { Box } from '@chakra-ui/react';
import { useColorValue } from '~/context';

import type { TTextOutput } from './types';

export const TextOutput: React.FC<TTextOutput> = (props: TTextOutput) => {
  const { children, ...rest } = props;

  const bg = useColorValue('blackAlpha.100', 'gray.800');
  const color = useColorValue('black', 'white');
  const selectionBg = useColorValue('black', 'white');
  const selectionColor = useColorValue('white', 'black');

  return (
    <Box
      p={3}
      mt={5}
      mx={2}
      bg={bg}
      as="pre"
      border="1px"
      rounded="md"
      color={color}
      fontSize="sm"
      fontFamily="mono"
      borderColor="inherit"
      whiteSpace="pre-wrap"
      css={{
        '&::selection': {
          backgroundColor: selectionBg,
          color: selectionColor,
        },
      }}
      {...rest}
    >
      {children.split('\\n').join('\n').replace(/\n\n/g, '\n')}
    </Box>
  );
};
