import dynamic from 'next/dynamic';
import { Button, Icon, Tooltip, useClipboard } from '@chakra-ui/react';
import { If } from '~/components';

const Copy = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiCopy));
const Check = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiCheck));

import type { TCopyButton } from './types';

export const CopyButton = (props: TCopyButton) => {
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
        zIndex="dropdown"
        colorScheme="secondary"
        {...rest}>
        <If c={hasCopied}>
          <Icon as={Check} boxSize="16px" />
        </If>
        <If c={!hasCopied}>
          <Icon as={Copy} boxSize="16px" />
        </If>
      </Button>
    </Tooltip>
  );
};
