import { Box } from '@chakra-ui/react';
import { useConfig } from '~/context';
import { useColorValue } from '~/hooks';
import { Highlighted } from './highlighted';

import type { BoxProps } from '@chakra-ui/react';

type TextOutputProps = Swap<BoxProps, 'children', string>;

export const TextOutput = (props: TextOutputProps): JSX.Element => {
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
