import { forwardRef } from 'react';
import dynamic from 'next/dynamic';
import { Button, Icon } from '@chakra-ui/react';
import { useLGState } from '~/hooks';

import type { ButtonProps } from '@chakra-ui/react';

const ChevronLeft = dynamic<MeronexIcon>(() =>
  import('@meronex/icons/fi').then(i => i.FiChevronLeft),
);

export const ResetButton = forwardRef<HTMLButtonElement, ButtonProps>((props, ref) => {
  const { isSubmitting } = useLGState();
  return (
    <Button
      ref={ref}
      color="current"
      variant="ghost"
      aria-label="Reset Form"
      opacity={isSubmitting.value ? 1 : 0}
      {...props}>
      <Icon as={ChevronLeft} boxSize={8} />
    </Button>
  );
});
