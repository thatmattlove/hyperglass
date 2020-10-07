import * as React from 'react';
import { Button, Icon, Tooltip } from '@chakra-ui/core';

export const RequeryButton = ({ requery, bg = 'secondary', ...props }) => (
  <Tooltip hasArrow label="Reload Query" placement="top">
    <Button mx={1} as="a" size="sm" zIndex="1" variantColor={bg} onClick={requery} {...props}>
      <Icon size="16px" name="repeat" />
    </Button>
  </Tooltip>
);
