import {
  Box,
  Alert,
  Button,
  VStack,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { NoConfig } from '~/elements';

import type { CenterProps } from '@chakra-ui/react';
import type { ConfigLoadError } from '~/util';

interface LoadErrorProps extends CenterProps {
  /**
   * Error thrown by `getHyperglassConfig` when any errors occur.
   */
  error: ConfigLoadError;

  /**
   * Callback to retry the config fetch.
   */
  retry: () => void;

  /**
   * If `true`, the UI is currently retrying the config fetch.
   */
  inProgress: boolean;
}

/**
 * Error component to be displayed when the hyperglass UI is unable to communicate with the
 * hyperglass API to retrieve its configuration.
 */
export const LoadError = (props: LoadErrorProps): JSX.Element => {
  const { error, retry, inProgress, ...rest } = props;

  return (
    <NoConfig {...rest}>
      <Alert
        status="error"
        height="200px"
        variant="subtle"
        borderRadius="lg"
        textAlign="center"
        alignItems="center"
        flexDirection="column"
        justifyContent="center"
        maxW={{ base: '95%', md: '80%', lg: '60%', xl: '40%' }}
      >
        <Box pos="absolute" right={0} top={0} m={4}>
          <Button
            size="sm"
            variant="outline"
            colorScheme="red"
            isLoading={inProgress}
            onClick={() => retry()}
          >
            Retry
          </Button>
        </Box>
        <AlertIcon boxSize={8} mr={0} />
        <VStack spacing={2}>
          <AlertTitle mt={4} mb={1} fontSize="xl">
            Error Loading Configuration
          </AlertTitle>
          <AlertDescription>
            <span>{error.baseMessage}</span>
            <Box as="span" fontWeight="bold">
              {` ${error.url}`}
            </Box>
          </AlertDescription>
          {typeof error.detail !== 'undefined' && (
            <AlertDescription fontWeight="light">{error.detail}</AlertDescription>
          )}
        </VStack>
      </Alert>
    </NoConfig>
  );
};
