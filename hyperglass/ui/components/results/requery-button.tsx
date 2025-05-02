import { forwardRef } from 'react';
import { Button, Tooltip } from '@chakra-ui/react';
import { DynamicIcon } from '~/elements';

import type { ButtonProps } from '@chakra-ui/react';
import type { UseQueryResult } from '@tanstack/react-query';

interface RequeryButtonProps extends ButtonProps {
  requery: Get<UseQueryResult<QueryResponse>, 'refetch'>;
}

const _RequeryButton: React.ForwardRefRenderFunction<HTMLButtonElement, RequeryButtonProps> = (
  props: RequeryButtonProps,
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
        onClick={requery as Get<RequeryButtonProps, 'onClick'>}
        colorScheme="secondary"
        {...rest}
      >
        <DynamicIcon icon={{ fi: 'FiRepeat' }} boxSize="16px" />
      </Button>
    </Tooltip>
  );
};

export const RequeryButton = forwardRef<HTMLButtonElement, RequeryButtonProps>(_RequeryButton);
