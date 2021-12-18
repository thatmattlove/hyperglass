import { Flex } from '@chakra-ui/react';
import { useColorValue } from '~/context';

import type { TCardBody } from './types';

export const CardBody = (props: TCardBody): JSX.Element => {
  const { onClick, ...rest } = props;
  const bg = useColorValue('white', 'dark.500');
  const color = useColorValue('dark.500', 'white');
  return (
    <Flex
      bg={bg}
      w="100%"
      rounded="md"
      color={color}
      onClick={onClick}
      overflow="hidden"
      borderWidth="1px"
      direction="column"
      {...rest}
    />
  );
};
