import { useCallback, useMemo } from 'react';
import { useToken } from '@chakra-ui/react';
import { mergeWith } from '@chakra-ui/utils';
import { useOpposingColor } from '~/hooks';
import { useColorValue, useColorToken, useMobile } from '~/context';
import { useSelectContext } from './select';

import type {
  TMenu,
  TOption,
  TStyles,
  TControl,
  TRSTheme,
  TMultiValue,
  TRSThemeCallback,
  TRSStyleCallback,
} from './types';

export const useControlStyle = (base: TStyles, state: TControl): TStyles => {
  const { isFocused } = state;
  const { colorMode, isError } = useSelectContext();

  const minHeight = useToken('space', 12);
  const borderRadius = useToken('radii', 'md');
  const color = useColorToken('colors', 'black', 'whiteAlpha.800');
  const focusBorder = useColorToken('colors', 'blue.500', 'blue.300');
  const invalidBorder = useColorToken('colors', 'red.500', 'red.300');
  const borderColor = useColorToken('colors', 'gray.100', 'whiteAlpha.50');
  const borderHover = useColorToken('colors', 'gray.300', 'whiteAlpha.400');
  const backgroundColor = useColorToken('colors', 'white', 'whiteAlpha.100');

  const styles = {
    backgroundColor,
    borderRadius,
    color,
    minHeight,
    transition: 'all 0.2s',
    borderColor: isError ? invalidBorder : isFocused ? focusBorder : borderColor,
    boxShadow: isError
      ? `0 0 0 1px ${invalidBorder}`
      : isFocused
      ? `0 0 0 1px ${focusBorder}`
      : undefined,
    '&:hover': { borderColor: isFocused ? focusBorder : borderHover },
    '&:hover > div > span': { backgroundColor: borderHover },
    '&:focus': { borderColor: isError ? invalidBorder : focusBorder },
    '&.invalid': { borderColor: invalidBorder, boxShadow: `0 0 0 1px ${invalidBorder}` },
  };
  return useMemo(() => mergeWith({}, base, styles), [colorMode, isFocused, isError]);
};

export const useMenuStyle = (base: TStyles, _: TMenu): TStyles => {
  const { colorMode, isOpen } = useSelectContext();
  const backgroundColor = useColorToken('colors', 'white', 'blackSolid.700');
  const borderRadius = useToken('radii', 'md');
  const styles = { borderRadius, backgroundColor };
  return useMemo(() => mergeWith({}, base, styles), [colorMode, isOpen]);
};

export const useMenuListStyle = (base: TStyles): TStyles => {
  const { colorMode, isOpen } = useSelectContext();

  const scrollbarTrack = useColorToken('colors', 'blackAlpha.50', 'whiteAlpha.50');
  const scrollbarThumb = useColorToken('colors', 'blackAlpha.300', 'whiteAlpha.300');
  const scrollbarThumbHover = useColorToken('colors', 'blackAlpha.400', 'whiteAlpha.400');

  const styles = {
    '&::-webkit-scrollbar': { width: '5px' },
    '&::-webkit-scrollbar-track': { backgroundColor: scrollbarTrack },
    '&::-webkit-scrollbar-thumb': { backgroundColor: scrollbarThumb },
    '&::-webkit-scrollbar-thumb:hover': { backgroundColor: scrollbarThumbHover },
    '-ms-overflow-style': { display: 'none' },
  };
  return useMemo(() => mergeWith({}, base, styles), [colorMode, isOpen]);
};

export const useOptionStyle = (base: TStyles, state: TOption): TStyles => {
  const { isFocused, isSelected, isDisabled } = state;
  const { colorMode, isOpen } = useSelectContext();

  const fontSize = useToken('fontSizes', 'lg');
  const disabled = useToken('colors', 'whiteAlpha.400');
  const active = useColorToken('colors', 'primary.600', 'primary.400');
  const focused = useColorToken('colors', 'primary.500', 'primary.300');
  const selected = useColorToken('colors', 'blackAlpha.400', 'whiteAlpha.400');

  const activeColor = useOpposingColor(active);

  const backgroundColor = useMemo(() => {
    let bg = 'transparent';
    switch (true) {
      case isDisabled:
        bg = disabled;
        break;
      case isSelected:
        bg = selected;
        break;
      case isFocused:
        bg = focused;
        break;
    }
    return bg;
  }, [isDisabled, isFocused, isSelected]);

  const color = useOpposingColor(backgroundColor);

  const styles = {
    color: backgroundColor === 'transparent' ? 'currentColor' : color,
    '&:active': { backgroundColor: active, color: activeColor },
    '&:focus': { backgroundColor: active, color: activeColor },
    backgroundColor,
    fontSize,
  };

  return useMemo(() => mergeWith({}, base, styles), [
    isOpen,
    colorMode,
    isFocused,
    isDisabled,
    isSelected,
  ]);
};

export const useIndicatorSeparatorStyle = (base: TStyles): TStyles => {
  const { colorMode } = useSelectContext();
  const backgroundColor = useColorToken('colors', 'whiteAlpha.700', 'gray.600');
  const styles = { backgroundColor };
  return useMemo(() => mergeWith({}, base, styles), [colorMode]);
};

export const usePlaceholderStyle = (base: TStyles): TStyles => {
  const { colorMode } = useSelectContext();
  const color = useColorToken('colors', 'gray.600', 'whiteAlpha.700');
  const fontSize = useToken('fontSizes', 'lg');
  return useMemo(() => mergeWith({}, base, { color, fontSize }), [colorMode]);
};

export const useSingleValueStyle = (): TRSStyleCallback => {
  const { colorMode } = useSelectContext();

  const color = useColorValue('black', 'whiteAlpha.800');
  const fontSize = useToken('fontSizes', 'lg');

  const styles = { color, fontSize };
  return useCallback((base: TStyles) => mergeWith({}, base, styles), [color, colorMode]);
};

export const useMultiValueStyle = (props: TMultiValue): TRSStyleCallback => {
  const { colorMode } = props;

  const backgroundColor = useColorToken('colors', 'primary.500', 'primary.300');
  const color = useOpposingColor(backgroundColor);

  const styles = { backgroundColor, color };
  return useCallback((base: TStyles) => mergeWith({}, base, styles), [backgroundColor, colorMode]);
};

export const useMultiValueLabelStyle = (props: TMultiValue): TRSStyleCallback => {
  const { colorMode } = props;

  const backgroundColor = useColorToken('colors', 'primary.500', 'primary.300');
  const color = useOpposingColor(backgroundColor);

  const styles = { color };
  return useCallback((base: TStyles) => mergeWith({}, base, styles), [colorMode]);
};

export const useMultiValueRemoveStyle = (props: TMultiValue): TRSStyleCallback => {
  const { colorMode } = props;

  const backgroundColor = useColorToken('colors', 'primary.500', 'primary.300');
  const color = useOpposingColor(backgroundColor);

  const styles = {
    color,
    '&:hover': { backgroundColor: 'inherit', color, opacity: 0.7 },
  };
  return useCallback((base: TStyles) => mergeWith({}, base, styles), [colorMode]);
};

export const useRSTheme = (): TRSThemeCallback => {
  const borderRadius = useToken('radii', 'md');
  return useCallback((t: TRSTheme): TRSTheme => ({ ...t, borderRadius }), []);
};

export const useMenuPortal = (): TRSStyleCallback => {
  const isMobile = useMobile();
  const styles = {
    zIndex: isMobile ? 1500 : 1,
  };
  return useCallback((base: TStyles) => mergeWith({}, base, styles), [isMobile]);
};
