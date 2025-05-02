import { Spinner } from '@chakra-ui/react';
import { NoConfig } from '~/elements';

export const Loading = (): JSX.Element => {
  return (
    <NoConfig color="#118ab2">
      <Spinner boxSize="8rem" />
    </NoConfig>
  );
};
