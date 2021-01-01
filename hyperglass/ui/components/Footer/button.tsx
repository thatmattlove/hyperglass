import { Button, Menu, MenuButton, MenuList } from '@chakra-ui/react';
import { Markdown } from '~/components';
import { useColorValue, useBreakpointValue } from '~/context';
import { useOpposingColor } from '~/hooks';

import type { TFooterButton } from './types';

export const FooterButton = (props: TFooterButton) => {
  const { content, title, side, ...rest } = props;
  const placement = side === 'left' ? 'top' : side === 'right' ? 'top-start' : undefined;
  const bg = useColorValue('white', 'gray.900');
  const color = useOpposingColor(bg);
  const size = useBreakpointValue({ base: 'xs', lg: 'sm' });
  return (
    <Menu placement={placement}>
      <MenuButton
        as={Button}
        size={size}
        variant="ghost"
        aria-label={typeof title === 'string' ? title : undefined}>
        {title}
      </MenuButton>
      <MenuList
        bg={bg}
        boxShadow="2xl"
        color={color}
        px={6}
        py={4}
        textAlign="left"
        mx={{ base: 1, lg: 2 }}
        maxW={{ base: '100vw', lg: '50vw' }}
        {...rest}>
        <Markdown content={content} />
      </MenuList>
    </Menu>
  );
};
