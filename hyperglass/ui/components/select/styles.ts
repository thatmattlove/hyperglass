import { useToken } from '@chakra-ui/react';
import { mergeWith } from '@chakra-ui/utils';
/* eslint-disable react-hooks/exhaustive-deps */
import { useCallback } from 'react';
import {
  useColorToken,
  useColorValue,
  useMobile,
  useOpposingColor,
  useOpposingColorCallback,
} from '~/hooks';
import { useSelectContext } from './select';

import * as ReactSelect from 'react-select';
import type { SingleOption } from '~/types';
import type { RSStyleCallbackProps, RSStyleFunction, RSThemeFunction } from './types';

export const useContainerStyle = <Opt extends SingleOption, IsMulti extends boolean>(
  props: RSStyleCallbackProps,
): RSStyleFunction<'container', Opt, IsMulti> => {
  return useCallback((base, state) => {
    return { width: '100%' };
  }, []);
};

export const useControlStyle = <Opt extends SingleOption, IsMulti extends boolean>(
  props: RSStyleCallbackProps,
): RSStyleFunction<'control', Opt, IsMulti> => {
  const { colorMode } = props;

  const { isError } = useSelectContext();

  const minHeight = useToken('space', 12);
  const borderRadius = useToken('radii', 'md');
  const color = useColorToken('colors', 'black', 'whiteAlpha.800');
  const focusBorder = useColorToken('colors', 'blue.500', 'blue.300');
  const invalidBorder = useColorToken('colors', 'red.500', 'red.300');
  // const borderColor = useColorToken('colors', 'gray.200', 'whiteAlpha.300');
  const borderColor = useColorToken('colors', 'gray.100', 'whiteAlpha.50');
  const borderHover = useColorToken('colors', 'gray.300', 'whiteAlpha.400');
  const backgroundColor = useColorToken('colors', 'white', 'blackSolid.800');

  return useCallback(
    (base, state) => {
      const { isFocused } = state;
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
      return mergeWith({}, base, styles);
    },
    [colorMode, isError],
  );
};

export const useMenuStyle = <Opt extends SingleOption, IsMulti extends boolean>(
  props: RSStyleCallbackProps,
): RSStyleFunction<'menu', Opt, IsMulti> => {
  const { colorMode } = props;

  const { isOpen } = useSelectContext();

  const backgroundColor = useColorToken('colors', 'white', 'blackSolid.700');
  const styles = { backgroundColor, zIndex: 1500 };

  return useCallback(base => mergeWith({}, base, styles), [colorMode, isOpen]);
};

export const useMenuListStyle = <Opt extends SingleOption, IsMulti extends boolean>(
  props: RSStyleCallbackProps,
): RSStyleFunction<'menuList', Opt, IsMulti> => {
  const { colorMode } = props;

  const { isOpen } = useSelectContext();

  const borderRadius = useToken('radii', 'md');
  const backgroundColor = useColorToken('colors', 'white', 'blackSolid.700');
  const scrollbarTrack = useColorToken('colors', 'blackAlpha.50', 'whiteAlpha.50');
  const scrollbarThumb = useColorToken('colors', 'blackAlpha.300', 'whiteAlpha.300');
  const scrollbarThumbHover = useColorToken('colors', 'blackAlpha.400', 'whiteAlpha.400');
  const styles = {
    borderRadius,
    backgroundColor,
    '&::-webkit-scrollbar': { width: '5px' },
    '&::-webkit-scrollbar-track': { backgroundColor: scrollbarTrack },
    '&::-webkit-scrollbar-thumb': { backgroundColor: scrollbarThumb },
    '&::-webkit-scrollbar-thumb:hover': { backgroundColor: scrollbarThumbHover },
    '-ms-overflow-style': { display: 'none' },
  };

  return useCallback(base => mergeWith({}, base, styles), [colorMode, isOpen]);
};

export const useOptionStyle = <Opt extends SingleOption, IsMulti extends boolean>(
  props: RSStyleCallbackProps,
): RSStyleFunction<'option', Opt, IsMulti> => {
  const { colorMode } = props;

  const { isOpen } = useSelectContext();

  const fontSize = useToken('fontSizes', 'lg');
  const disabled = useToken('colors', 'whiteAlpha.400');
  const active = useColorToken('colors', 'primary.600', 'primary.400');
  const focused = useColorToken('colors', 'primary.500', 'primary.300');
  const selected = useColorToken('colors', 'blackAlpha.400', 'whiteAlpha.400');

  const activeColor = useOpposingColor(active);
  const getColor = useOpposingColorCallback();

  return useCallback(
    (base, state) => {
      const { isFocused, isSelected, isDisabled } = state;

      let backgroundColor = 'transparent';
      switch (true) {
        case isDisabled:
          backgroundColor = disabled;
          break;
        case isSelected:
          backgroundColor = selected;
          break;
        case isFocused:
          backgroundColor = focused;
          break;
      }
      const color = getColor(backgroundColor);

      const styles = {
        color: backgroundColor === 'transparent' ? 'currentColor' : color,
        '&:active': { backgroundColor: active, color: activeColor },
        '&:focus': { backgroundColor: active, color: activeColor },
        backgroundColor,
        fontSize,
      };

      return mergeWith({}, base, styles);
    },
    [isOpen, colorMode],
  );
};

export const useIndicatorSeparatorStyle = <Opt extends SingleOption, IsMulti extends boolean>(
  props: RSStyleCallbackProps,
): RSStyleFunction<'indicatorSeparator', Opt, IsMulti> => {
  const { colorMode } = props;
  const backgroundColor = useColorToken('colors', 'gray.200', 'whiteAlpha.300');
  const styles = { backgroundColor };

  return useCallback(base => mergeWith({}, base, styles), [colorMode]);
};

export const usePlaceholderStyle = <Opt extends SingleOption, IsMulti extends boolean>(
  props: RSStyleCallbackProps,
): RSStyleFunction<'placeholder', Opt, IsMulti> => {
  const { colorMode } = props;

  const color = useColorToken('colors', 'gray.600', 'whiteAlpha.700');
  const fontSize = useToken('fontSizes', 'lg');

  return useCallback(base => mergeWith({}, base, { color, fontSize }), [colorMode]);
};

export const useSingleValueStyle = <Opt extends SingleOption, IsMulti extends boolean>(
  props: RSStyleCallbackProps,
): RSStyleFunction<'singleValue', Opt, IsMulti> => {
  const { colorMode } = props;

  const color = useColorValue('black', 'whiteAlpha.800');
  const fontSize = useToken('fontSizes', 'lg');
  const styles = { color, fontSize };

  return useCallback(base => mergeWith({}, base, styles), [color, colorMode]);
};

export const useMultiValueStyle = <Opt extends SingleOption, IsMulti extends boolean>(
  props: RSStyleCallbackProps,
): RSStyleFunction<'multiValue', Opt, IsMulti> => {
  const { colorMode } = props;

  const backgroundColor = useColorToken('colors', 'primary.500', 'primary.300');
  const color = useOpposingColor(backgroundColor);
  const borderRadius = useToken('radii', 'md');
  const styles = { backgroundColor, color, borderRadius };

  return useCallback(base => mergeWith({}, base, styles), [backgroundColor, colorMode]);
};

export const useMultiValueLabelStyle = <Opt extends SingleOption, IsMulti extends boolean>(
  props: RSStyleCallbackProps,
): RSStyleFunction<'multiValueLabel', Opt, IsMulti> => {
  const { colorMode } = props;

  const backgroundColor = useColorToken('colors', 'primary.500', 'primary.300');
  const color = useOpposingColor(backgroundColor);
  const styles = { color };

  return useCallback(base => mergeWith({}, base, styles), [colorMode]);
};

export const useMultiValueRemoveStyle = <Opt extends SingleOption, IsMulti extends boolean>(
  props: RSStyleCallbackProps,
): RSStyleFunction<'multiValueRemove', Opt, IsMulti> => {
  const { colorMode } = props;

  const backgroundColor = useColorToken('colors', 'primary.500', 'primary.300');
  const color = useOpposingColor(backgroundColor);
  const styles = {
    color,
    '&:hover': { backgroundColor: 'transparent', color, opacity: 0.8 },
  };

  return useCallback(base => mergeWith({}, base, styles), [colorMode]);
};

export const useRSTheme = (): RSThemeFunction => {
  const borderRadius = useToken('radii', 'md') as unknown as number;

  return useCallback((t: ReactSelect.Theme): ReactSelect.Theme => ({ ...t, borderRadius }), []);
};

export const useMenuPortal = <Opt extends SingleOption, IsMulti extends boolean>(): RSStyleFunction<
  'menuPortal',
  Opt,
  IsMulti
> => {
  const isMobile = useMobile();
  const styles = {
    zIndex: 1500,
  };

  return useCallback(base => mergeWith({}, base, styles), [isMobile]);
};
