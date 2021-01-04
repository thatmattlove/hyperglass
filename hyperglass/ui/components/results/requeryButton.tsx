import { forwardRef } from 'react';
import dynamic from 'next/dynamic';
import { Button, Icon, Tooltip } from '@chakra-ui/react';

import type { TRequeryButton } from './types';

const Repeat = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiRepeat));

const _RequeryButton: React.ForwardRefRenderFunction<HTMLButtonElement, TRequeryButton> = (
  props: TRequeryButton,
  ref,
) => {
  const { requery, ...rest } = props;

  return (
    <Tooltip hasArrow label="Reload Query" placement="top">
      <Button
        mx={1}
        as="a"
        ref={ref}
        size="sm"
        zIndex="1"
        variant="ghost"
        onClick={requery as TRequeryButton['onClick']}
        colorScheme="secondary"
        {...rest}
      >
        <Icon as={Repeat} boxSize="16px" />
      </Button>
    </Tooltip>
  );
};

export const RequeryButton = forwardRef<HTMLButtonElement, TRequeryButton>(_RequeryButton);
