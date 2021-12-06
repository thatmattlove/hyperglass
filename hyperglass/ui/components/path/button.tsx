import { Button, Tooltip } from '@chakra-ui/react';
import { DynamicIcon } from '~/components';

import type { TPathButton } from './types';

export const PathButton = (props: TPathButton): JSX.Element => {
  const { onOpen } = props;
  return (
    <Tooltip hasArrow label="View AS Path" placement="top">
      <Button as="a" mx={1} size="sm" variant="ghost" onClick={onOpen} colorScheme="secondary">
        <DynamicIcon icon={{ bi: 'BiNetworkChart' }} boxSize="16px" />
      </Button>
    </Tooltip>
  );
};
