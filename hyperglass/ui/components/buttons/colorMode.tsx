import { forwardRef } from 'react';
import dynamic from 'next/dynamic';
import { Button, Icon } from '@chakra-ui/react';
import { If } from '~/components';
import { useColorMode, useColorValue } from '~/context';

import type { TColorModeToggle } from './types';

const Sun = dynamic<MeronexIcon>(() => import('@meronex/icons/hi').then(i => i.HiSun));
const Moon = dynamic<MeronexIcon>(() => import('@meronex/icons/hi').then(i => i.HiMoon));

const outlineColor = { dark: 'primary.300', light: 'primary.600' };

export const ColorModeToggle = forwardRef<HTMLButtonElement, TColorModeToggle>((props, ref) => {
  const { size = '1.5rem', ...rest } = props;
  const { colorMode, toggleColorMode } = useColorMode();

  const label = useColorValue('Switch to dark mode', 'Switch to light mode');

  return (
    <Button
      ref={ref}
      aria-label={label}
      title={label}
      onClick={toggleColorMode}
      variant="ghost"
      borderWidth="1px"
      borderColor="transparent"
      _hover={{
        backgroundColor: 'unset',
        borderColor: outlineColor[colorMode],
      }}
      color="currentColor"
      px={4}
      {...rest}>
      <If c={colorMode === 'light'}>
        <Icon as={Moon} boxSize={size} />
      </If>
      <If c={colorMode === 'dark'}>
        <Icon as={Sun} boxSize={size} />
      </If>
    </Button>
  );
});
