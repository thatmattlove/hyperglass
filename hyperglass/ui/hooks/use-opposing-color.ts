import { useMemo, useCallback } from 'react';
import { getColor, isLight } from '@chakra-ui/theme-tools';
import { useTheme } from './theme-hooks';

interface OpposingColorOptions {
  light?: string;
  dark?: string;
}

export type UseIsDarkCallbackReturn = (color: string) => boolean;

/**
 * Parse the color string to determine if it's a Chakra UI theme key, and determine if the
 * opposing color should be black or white.
 */
export function useIsDark(color: string): boolean {
  const isDarkFn = useIsDarkCallback();
  return useMemo((): boolean => isDarkFn(color), [color, isDarkFn]);
}

export function useIsDarkCallback(): UseIsDarkCallbackReturn {
  const theme = useTheme();
  return useCallback(
    (color: string): boolean => {
      let opposing = color;
      if (typeof color === 'string' && color.match(/[a-zA-Z]+\.[a-zA-Z0-9]+/g)) {
        opposing = getColor(theme, color, color);
      }
      let opposingShouldBeDark = true;
      try {
        opposingShouldBeDark = isLight(opposing)(theme);
      } catch (err) {
        console.error(err);
      }
      return opposingShouldBeDark;
    },
    [theme],
  );
}

/**
 * Determine if the foreground color for `color` should be white or black.
 */
export function useOpposingColor(color: string, options?: OpposingColorOptions): string {
  const isBlack = useIsDark(color);

  return useMemo(() => {
    if (isBlack) {
      return options?.dark ?? 'black';
    }
    return options?.light ?? 'white';
  }, [isBlack, options?.dark, options?.light]);
}

export function useOpposingColorCallback(
  options?: OpposingColorOptions,
): (color: string) => string {
  const isDark = useIsDarkCallback();
  return useCallback(
    (color: string) => {
      const isBlack = isDark(color);
      if (isBlack) {
        return options?.dark ?? 'black';
      }
      return options?.light ?? 'white';
    },
    [isDark, options?.dark, options?.light],
  );
}
