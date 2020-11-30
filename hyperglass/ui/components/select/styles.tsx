import { useCallback, useMemo } from 'react';
import { useToken } from '@chakra-ui/react';
import { mergeWith } from '@chakra-ui/utils';
import { useOpposingColor } from '~/hooks';
import { useColorValue, useMobile } from '~/context';
import { useSelectContext } from './select';

import type {
  TControl,
  TIndicator,
  TMenu,
  TMenuList,
  TMultiValueState,
  TOption,
  TPlaceholder,
  TStyles,
  TRSTheme,
  TMultiValue,
} from './types';

export const useControlStyle = (base: TStyles, state: TControl): TStyles => {
  const { isFocused } = state;
  const { colorMode } = useSelectContext();
  const borderHover = useColorValue(
    useToken('colors', 'gray.300'),
    useToken('colors', 'whiteAlpha.200'),
  );
  const focusBorder = useToken('colors', 'secondary.500');
  const invalidBorder = useColorValue(useToken('colors', 'red.500'), useToken('colors', 'red.300'));

  const borderRadius = useToken('radii', 'md');
  const minHeight = useToken('sizes', 'lg');
  const color = useColorValue(useToken('colors', 'black'), useToken('colors', 'whiteAlpha.800'));
  const backgroundColor = useColorValue(
    useToken('colors', 'white'),
    useToken('colors', 'whiteAlpha.100'),
  );
  const styles = {
    backgroundColor,
    borderRadius,
    color,
    minHeight,
    '&:hover': { borderColor: isFocused ? focusBorder : borderHover },
    '&:hover > div > span': { backgroundColor: borderHover },

    '&.invalid': { borderColor: invalidBorder, boxShadow: `0 0 0 1px ${invalidBorder}` },
  };
  return useMemo(() => mergeWith({}, base, styles), [colorMode, isFocused]);
};

export const useMenuStyle = (base: TStyles, state: TMenu): TStyles => {
  const { colorMode, isOpen } = useSelectContext();
  const backgroundColor = useColorValue(
    useToken('colors', 'white'),
    useToken('colors', 'whiteFaded.50'),
  );
  const borderRadius = useToken('radii', 'md');
  const styles = { borderRadius, backgroundColor };
  return useMemo(() => mergeWith({}, base, styles), [colorMode, isOpen]);
};

export const useMenuListStyle = (base: TStyles, state: TMenuList): TStyles => {
  const { colorMode, isOpen } = useSelectContext();

  const scrollbarTrack = useColorValue(
    useToken('colors', 'blackAlpha.50'),
    useToken('colors', 'whiteAlpha.50'),
  );
  const scrollbarThumb = useColorValue(
    useToken('colors', 'blackAlpha.300'),
    useToken('colors', 'whiteAlpha.300'),
  );

  const scrollbarThumbHover = useColorValue(
    useToken('colors', 'blackAlpha.400'),
    useToken('colors', 'whiteAlpha.400'),
  );

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
  const { isFocused } = state;
  const { colorMode, isOpen } = useSelectContext();
  const fontSize = useToken('fontSizes', 'lg');
  const disabled = useToken('colors', 'whiteAlpha.400');
  const selected = useColorValue(
    useToken('colors', 'blackAlpha.400'),
    useToken('colors', 'whiteAlpha.400'),
  );
  const focused = useColorValue(
    useToken('colors', 'primary.500'),
    useToken('colors', 'primary.300'),
  );
  const active = useColorValue(
    useToken('colors', 'primary.600'),
    useToken('colors', 'primary.400'),
  );
  const disabledColor = useOpposingColor(disabled);
  const selectedColor = useOpposingColor(selected);
  const focusedColor = useOpposingColor(focused);
  const activeColor = useOpposingColor(active);

  const styles = {
    backgroundColor: state.isDisabled
      ? disabled
      : state.isSelected
      ? selected
      : state.isFocused
      ? focused
      : 'transparent',
    color: state.isDisabled
      ? disabledColor
      : state.isSelected
      ? selectedColor
      : state.isFocused
      ? focusedColor
      : 'transparent',
    fontSize,
    '&:focus': { backgroundColor: active, color: activeColor },
    '&:active': { backgroundColor: active, color: activeColor },
  };
  return useMemo(() => mergeWith({}, base, styles), [colorMode, isFocused, isOpen]);
};

export const useIndicatorSeparatorStyle = (base: TStyles, state: TIndicator): TStyles => {
  const { colorMode } = useSelectContext();
  const backgroundColor = useColorValue(
    useToken('colors', 'whiteAlpha.700'),
    useToken('colors', 'gray.600'),
  );
  const styles = { backgroundColor };
  return useMemo(() => mergeWith({}, base, styles), [colorMode]);
};

export const usePlaceholderStyle = (base: TStyles, state: TPlaceholder): TStyles => {
  const { colorMode } = useSelectContext();
  const color = useColorValue(useToken('colors', 'whiteAlpha.700'), useToken('colors', 'gray.600'));
  return useMemo(() => mergeWith({}, base, { color }), [colorMode]);
};

export const useSingleValueStyle = (props: TStyles) => {
  const { colorMode } = useSelectContext();

  const color = useColorValue('black', 'whiteAlpha.800');
  const fontSize = useToken('fontSizes', 'lg');

  const styles = { color, fontSize };
  return useCallback((base: TStyles, state: TMultiValueState) => mergeWith({}, base, styles), [
    color,
    colorMode,
  ]);
};

export const useMultiValueStyle = (props: TMultiValue) => {
  const { colorMode } = props;

  const backgroundColor = useColorValue(
    useToken('colors', 'primary.500'),
    useToken('colors', 'primary.300'),
  );
  const color = useOpposingColor(backgroundColor);
  const styles = { backgroundColor, color };

  return useCallback((base: TStyles, state: TMultiValueState) => mergeWith({}, base, styles), [
    backgroundColor,
    colorMode,
  ]);
};

export const useMultiValueLabelStyle = (props: TMultiValue) => {
  const { colorMode } = props;
  const backgroundColor = useColorValue(
    useToken('colors', 'primary.500'),
    useToken('colors', 'primary.300'),
  );
  const color = useOpposingColor(backgroundColor);
  const styles = { color };

  return useCallback((base: TStyles, state: TMultiValueState) => mergeWith({}, base, styles), [
    colorMode,
  ]);
};

export const useMultiValueRemoveStyle = (props: TMultiValue) => {
  const { colorMode } = props;
  const backgroundColor = useColorValue(
    useToken('colors', 'primary.500'),
    useToken('colors', 'primary.300'),
  );
  const color = useOpposingColor(backgroundColor);
  const styles = {
    color,
    '&:hover': { backgroundColor: 'inherit', color, opacity: 0.7 },
  };
  return useCallback((base: TStyles, state: TMultiValueState) => mergeWith({}, base, styles), [
    colorMode,
  ]);
};

export const useRSTheme = (props: TMultiValue) => {
  const borderRadius = useToken('radii', 'md');
  return useCallback((t: TRSTheme): TRSTheme => ({ ...t, borderRadius }), []);
};

export const useMenuPortal = (props: TMultiValue) => {
  const isMobile = useMobile();
  const styles = {
    zIndex: isMobile ? 1500 : 1,
  };
  return useCallback((base: TStyles, state: TMultiValueState) => mergeWith({}, base, styles), [
    isMobile,
  ]);
};
