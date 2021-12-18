import { Box } from '@chakra-ui/react';
import { useColorValue, useConfig } from '~/context';
import { Highlighted } from './highlighted';

import type { TTextOutput } from './types';

export const TextOutput = (props: TTextOutput): JSX.Element => {
  const { children, ...rest } = props;

  const bg = useColorValue('blackAlpha.100', 'gray.800');
  const color = useColorValue('black', 'white');
  const selectionBg = useColorValue('black', 'white');
  const selectionColor = useColorValue('white', 'black');

  const {
    web: { highlight },
  } = useConfig();

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
      <Highlighted patterns={highlight}>
        {children.split('\\n').join('\n').replace(/\n\n/g, '\n')}
      </Highlighted>
    </Box>
  );
};
