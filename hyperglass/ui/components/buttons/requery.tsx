import dynamic from 'next/dynamic';
import { Button, Icon, Tooltip } from '@chakra-ui/react';

import type { TRequeryButton } from './types';

const Repeat = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiRepeat));

export const RequeryButton = (props: TRequeryButton) => {
  const { requery, bg = 'secondary', ...rest } = props;
  return (
    <Tooltip hasArrow label="Reload Query" placement="top">
      <Button mx={1} as="a" size="sm" zIndex="1" variantColor={bg} onClick={requery} {...rest}>
        <Icon as={Repeat} boxSize="16px" />
      </Button>
    </Tooltip>
  );
};
