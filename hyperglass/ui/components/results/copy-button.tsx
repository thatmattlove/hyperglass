import { Button, Tooltip, useClipboard } from '@chakra-ui/react';
import { DynamicIcon } from '~/elements';

import type { ButtonProps } from '@chakra-ui/react';

interface CopyButtonProps extends ButtonProps {
  copyValue: string;
}

export const CopyButton = (props: CopyButtonProps): JSX.Element => {
  const { copyValue, ...rest } = props;
  const { onCopy, hasCopied } = useClipboard(copyValue);
  return (
    <Tooltip hasArrow label="Copy Output" placement="top">
      <Button
        as="a"
        mx={1}
        size="sm"
        variant="ghost"
        onClick={onCopy}
        colorScheme="secondary"
        {...rest}
      >
        <DynamicIcon icon={{ fi: hasCopied ? 'FiCheck' : 'FiCopy' }} boxSize="16px" />
      </Button>
    </Tooltip>
  );
};
