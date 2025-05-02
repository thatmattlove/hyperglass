import { useMemo } from 'react';
import { Button, Menu, MenuButton, MenuList } from '@chakra-ui/react';
import { useConfig } from '~/context';
import { Markdown } from '~/elements';
import { useColorValue, useBreakpointValue, useOpposingColor, useStrf } from '~/hooks';

import type { MenuListProps } from '@chakra-ui/react';
import type { Config } from '~/types';

interface FooterButtonProps extends Omit<MenuListProps, 'title'> {
  side: 'left' | 'right';
  title?: MenuListProps['children'];
  content: string;
}

/**
 * Filter the configuration object based on values that are strings for formatting.
 */
function getConfigFmt(config: Config): Record<string, string> {
  const fmt = {} as Record<string, string>;
  for (const [k, v] of Object.entries(config)) {
    if (typeof v === 'string') {
      fmt[k] = v;
    }
  }
  return fmt;
}

export const FooterButton = (props: FooterButtonProps): JSX.Element => {
  const { content, title, side, ...rest } = props;

  const config = useConfig();
  const strF = useStrf();
  const fmt = useMemo(() => getConfigFmt(config), [config]);
  const fmtContent = useMemo(() => strF(content, fmt), [fmt, content, strF]);

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
        lineHeight={0}
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
        whiteSpace="normal"
        mx={{ base: 1, lg: 2 }}
        maxW={{ base: '100%', lg: '50vw' }}
        {...rest}
      >
        <Markdown content={fmtContent} />
      </MenuList>
    </Menu>
  );
};
