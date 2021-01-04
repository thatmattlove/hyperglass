import dynamic from 'next/dynamic';
import { Button, Icon, Tooltip, useClipboard } from '@chakra-ui/react';

const Copy = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiCopy));
const Check = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiCheck));

import type { TCopyButton } from './types';

export const CopyButton: React.FC<TCopyButton> = (props: TCopyButton) => {
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
        <Icon as={hasCopied ? Check : Copy} boxSize="16px" />
      </Button>
    </Tooltip>
  );
};
