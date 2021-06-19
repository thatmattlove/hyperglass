import { useMemo } from 'react';
import { Button, Menu, MenuButton, MenuList } from '@chakra-ui/react';
import { Markdown } from '~/components';
import { useColorValue, useBreakpointValue, useConfig } from '~/context';
import { useOpposingColor, useStrf } from '~/hooks';

import type { IConfig } from '~/types';
import type { TFooterButton } from './types';

/**
 * Filter the configuration object based on values that are strings for formatting.
 */
function getConfigFmt(config: IConfig): Record<string, string> {
  const fmt = {} as Record<string, string>;
  for (const [k, v] of Object.entries(config)) {
    if (typeof v === 'string') {
      fmt[k] = v;
    }
  }
  return fmt;
}

export const FooterButton: React.FC<TFooterButton> = (props: TFooterButton) => {
  const { content, title, side, ...rest } = props;

  const config = useConfig();
  const fmt = useMemo(() => getConfigFmt(config), []);
  const fmtContent = useStrf(content, fmt);

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
