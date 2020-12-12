import { Button, Menu, MenuButton, MenuList } from '@chakra-ui/react';
import { Markdown } from '~/components';

import type { TFooterButton } from './types';

export const FooterButton = (props: TFooterButton) => {
  const { content, title, side, ...rest } = props;
  const placement = side === 'left' ? 'top-end' : side === 'right' ? 'top-start' : undefined;
  return (
    <Menu placement={placement}>
      <MenuButton
        as={Button}
        size="xs"
        variant="ghost"
        aria-label={typeof title === 'string' ? title : undefined}>
        {title}
      </MenuButton>
      <MenuList
        px={6}
        py={4}
        textAlign={side}
        mx={{ base: 1, lg: 2 }}
        maxW={{ base: '100vw', lg: '50vw' }}
        {...rest}>
        <Markdown content={content} />
      </MenuList>
    </Menu>
  );
};
