import { forwardRef } from 'react';
import { Button, Tooltip } from '@chakra-ui/react';
import { DynamicIcon, If } from '~/components';
import { useColorMode, useColorValue, useBreakpointValue } from '~/context';
import { useOpposingColor } from '~/hooks';

import type { TColorModeToggle } from './types';

export const ColorModeToggle = forwardRef<HTMLButtonElement, TColorModeToggle>(
  (props: TColorModeToggle, ref) => {
    const { size = '1.5rem', ...rest } = props;
    const { colorMode, toggleColorMode } = useColorMode();

    const bg = useColorValue('primary.500', 'yellow.300');
    const color = useOpposingColor(bg);
    const label = useColorValue('Switch to dark mode', 'Switch to light mode');
    const btnSize = useBreakpointValue({ base: 'xs', lg: 'sm' });

    return (
      <Tooltip hasArrow placement="top-end" label={label} bg={bg} color={color}>
        <Button
          ref={ref}
          size={btnSize}
          title={label}
          variant="ghost"
          aria-label={label}
          _hover={{ color: bg }}
          color="currentColor"
          onClick={toggleColorMode}
          {...rest}
        >
          <If c={colorMode === 'light'}>
            <DynamicIcon icon={{ hi: 'HiMoon' }} boxSize={size} />
          </If>
          <If c={colorMode === 'dark'}>
            <DynamicIcon icon={{ hi: 'HiSun' }} boxSize={size} />
          </If>
        </Button>
      </Tooltip>
    );
  },
);
