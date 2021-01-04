import { Flex } from '@chakra-ui/react';

import { FlexProps } from '@chakra-ui/react';

export const FormRow: React.FC<FlexProps> = (props: FlexProps) => {
  return (
    <Flex
      w="100%"
      flexDir="row"
      flexWrap="wrap"
      justifyContent={{ base: 'center', lg: 'space-between' }}
      {...props}
    />
  );
};
