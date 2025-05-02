import { forwardRef } from 'react';
import { Button, Tooltip } from '@chakra-ui/react';
import { Switch, Case } from 'react-if';
import { DynamicIcon } from '~/elements';
import { useOpposingColor, useColorMode, useColorValue, useBreakpointValue } from '~/hooks';

import type { ButtonProps } from '@chakra-ui/react';

interface ColorModeToggleProps extends Omit<ButtonProps, 'size'> {
  size?: string | number;
}

export const ColorModeToggle = forwardRef<HTMLButtonElement, ColorModeToggleProps>(
  (props: ColorModeToggleProps, ref) => {
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
          <Switch>
            <Case condition={colorMode === 'light'}>
              <DynamicIcon icon={{ hi: 'HiMoon' }} boxSize={size} />
            </Case>
            <Case condition={colorMode === 'dark'}>
              <DynamicIcon icon={{ hi: 'HiSun' }} boxSize={size} />
            </Case>
          </Switch>
        </Button>
      </Tooltip>
    );
  },
);
