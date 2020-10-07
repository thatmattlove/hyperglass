import * as React from 'react';
import { IconButton } from '@chakra-ui/core';

export const TableIconButton = ({ icon, onClick, isDisabled, color, children, ...props }) => (
  <IconButton
    size="sm"
    icon={icon}
    borderWidth={1}
    onClick={onClick}
    variantColor={color}
    isDisabled={isDisabled}
    aria-label="Table Icon Button"
    {...props}>
    {children}
  </IconButton>
);
