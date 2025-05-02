import {
  useBreakpointValue,
  useTheme as useChakraTheme,
  useColorModeValue,
  useToken,
} from '@chakra-ui/react';
import type { Theme } from '~/types';

export {
  useBreakpointValue,
  useColorMode,
  useColorModeValue as useColorValue,
  useToken,
} from '@chakra-ui/react';

/**
 * Determine if device is mobile or desktop based on Chakra UI theme breakpoints.
 */
export const useMobile = (): boolean =>
  useBreakpointValue<boolean>({ base: true, md: true, lg: false, xl: false }) ?? true;

/**
 * Get the current theme object.
 */
export const useTheme = (): Theme.Full => useChakraTheme();

/**
 * Convenience function to combine Chakra UI's useToken & useColorModeValue.
 */
export const useColorToken = <L extends string, D extends string>(
  token: keyof Theme.Full,
  light: L,
  dark: D,
): L | D => useColorModeValue<L, D>(useToken(token, light), useToken(token, dark));
