import { forwardRef } from 'react';
import { Button, Tooltip } from '@chakra-ui/react';
import { DynamicIcon } from '~/components';

import type { TRequeryButton } from './types';

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
        <DynamicIcon icon={{ fi: 'FiRepeat' }} boxSize="16px" />
      </Button>
    </Tooltip>
  );
};

export const RequeryButton = forwardRef<HTMLButtonElement, TRequeryButton>(_RequeryButton);
