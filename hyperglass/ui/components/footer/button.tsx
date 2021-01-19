import { Button, Menu, MenuButton, MenuList } from '@chakra-ui/react';
import { Markdown } from '~/components';
import { useColorValue, useBreakpointValue } from '~/context';
import { useOpposingColor } from '~/hooks';

import type { TFooterButton } from './types';

export const FooterButton: React.FC<TFooterButton> = (props: TFooterButton) => {
  const { content, title, side, ...rest } = props;
  const placement = side === 'left' ? 'top' : side === 'right' ? 'top-end' : undefined;
  const bg = useColorValue('white', 'gray.900');
  const color = useOpposingColor(bg);
  const size = useBreakpointValue({ base: 'xs', lg: 'sm' });
  return (
    <Menu placement={placement} preventOverflow isLazy>
      <MenuButton
        zIndex={2}
        as={Button}
        size={size}
        variant="ghost"
        aria-label={typeof title === 'string' ? title : undefined}
      >
        {title}
      </MenuButton>
      <MenuList
        px={6}
        py={4}
        bg={bg}
        // Ensure the height doesn't overtake the viewport, especially on mobile. See overflow also.
        maxH="50vh"
        color={color}
        boxShadow="2xl"
        textAlign="left"
        overflowY="auto"
        mx={{ base: 1, lg: 2 }}
        maxW={{ base: '100%', lg: '50vw' }}
        {...rest}
      >
        <Markdown content={content} />
      </MenuList>
    </Menu>
  );
};
