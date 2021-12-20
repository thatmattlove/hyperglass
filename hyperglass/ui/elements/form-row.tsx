import { Flex } from '@chakra-ui/react';

import type { FlexProps } from '@chakra-ui/react';

export const FormRow = (props: FlexProps): JSX.Element => {
  return (
    <Flex
      w="100%"
      flexDir="row"
      flexWrap="wrap"
      justifyContent={{ base: 'center', lg: 'space-between' }}
      sx={{ '& > *': { display: 'flex', flex: { base: '1 0 100%', lg: '1 0 33.33%' } } }}
      {...props}
    />
  );
};
