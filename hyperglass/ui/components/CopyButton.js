import * as React from 'react';
import { Button, Icon, Tooltip, useClipboard } from '@chakra-ui/core';

export const CopyButton = ({ bg = 'secondary', copyValue, ...props }) => {
  const { onCopy, hasCopied } = useClipboard(copyValue);
  return (
    <Tooltip hasArrow label="Copy Output" placement="top">
      <Button
        as="a"
        size="sm"
        variantColor={bg}
        zIndex="dropdown"
        onClick={onCopy}
        mx={1}
        {...props}>
        {hasCopied ? <Icon name="check" size="16px" /> : <Icon name="copy" size="16px" />}
      </Button>
    </Tooltip>
  );
};
