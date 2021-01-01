import { Flex } from '@chakra-ui/react';
import { useColorValue } from '~/context';

import type { ICardBody } from './types';

export const CardBody = (props: ICardBody) => {
  const { onClick, ...rest } = props;
  const bg = useColorValue('white', 'dark.500');
  const color = useColorValue('dark.500', 'white');
  return (
    <Flex
      bg={bg}
      w="100%"
      maxW="95%"
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
