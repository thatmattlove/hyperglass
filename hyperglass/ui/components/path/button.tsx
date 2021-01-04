import dynamic from 'next/dynamic';
import { Button, Icon, Tooltip } from '@chakra-ui/react';

import type { TPathButton } from './types';

const PathIcon = dynamic<MeronexIcon>(() =>
  import('@meronex/icons/bi').then(i => i.BisNetworkChart),
);

export const PathButton: React.FC<TPathButton> = (props: TPathButton) => {
  const { onOpen } = props;
  return (
    <Tooltip hasArrow label="View AS Path" placement="top">
      <Button as="a" mx={1} size="sm" variant="ghost" onClick={onOpen} colorScheme="secondary">
        <Icon as={PathIcon} boxSize="16px" />
      </Button>
    </Tooltip>
  );
};
