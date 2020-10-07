import * as React from 'react';
import { Button } from '@chakra-ui/core';
import { FiChevronLeft } from '@meronex/icons/fi';

export const ResetButton = React.forwardRef(({ isSubmitting, onClick }, ref) => (
  <Button
    ref={ref}
    color="current"
    variant="ghost"
    onClick={onClick}
    aria-label="Reset Form"
    opacity={isSubmitting ? 1 : 0}>
    <FiChevronLeft size={24} />
  </Button>
));
