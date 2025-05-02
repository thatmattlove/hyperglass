import { Flex } from '@chakra-ui/react';
import { useColorValue } from '~/hooks';

import type { FlexProps } from '@chakra-ui/react';

interface CardBodyProps extends Omit<FlexProps, 'onClick'> {
  onClick?: () => boolean;
}

export const CardBody = (props: CardBodyProps): JSX.Element => {
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
