import { Flex, Spinner } from '@chakra-ui/react';
import { useColorValue } from '~/context';

export const Loading: React.FC = () => {
  const bg = useColorValue('white', 'black');
  const color = useColorValue('black', 'white');
  return (
    <Flex flexDirection="column" minHeight="100vh" w="100%" bg={bg} color={color}>
      <Flex
        px={2}
        py={0}
        w="100%"
        as="main"
        flexGrow={1}
        flexShrink={1}
        flexBasis="auto"
        textAlign="center"
        alignItems="center"
        justifyContent="start"
        flexDirection="column"
        mt={{ base: '50%', xl: '25%' }}>
        <Spinner color="primary.500" w="6rem" h="6rem" />
      </Flex>
    </Flex>
  );
};
