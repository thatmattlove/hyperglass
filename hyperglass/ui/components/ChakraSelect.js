import * as React from 'react';
import { Text, useColorMode, useTheme } from '@chakra-ui/core';
import Select from 'react-select';
import { opposingColor } from 'app/util';

export const ChakraSelect = React.forwardRef(
  ({ placeholder = 'Select...', isFullWidth, size, children, ...props }, ref) => {
    const theme = useTheme();
    const { colorMode } = useColorMode();
    const sizeMap = {
      lg: { height: theme.space[12] },
      md: { height: theme.space[10] },
      sm: { height: theme.space[8] },
    };
    const colorSetPrimaryBg = {
      dark: theme.colors.primary[300],
      light: theme.colors.primary[500],
    };
    const colorSetPrimaryColor = opposingColor(theme, colorSetPrimaryBg[colorMode]);
    const bg = {
      dark: theme.colors.whiteAlpha[100],
      light: theme.colors.white,
    };
    const color = {
      dark: theme.colors.whiteAlpha[800],
      light: theme.colors.black,
    };
    const borderFocused = theme.colors.secondary[500];
    const borderDisabled = theme.colors.whiteAlpha[100];
    const border = {
      dark: theme.colors.whiteAlpha[50],
      light: theme.colors.gray[100],
    };
    const borderRadius = theme.space[1];
    const hoverColor = {
      dark: theme.colors.whiteAlpha[200],
      light: theme.colors.gray[300],
    };
    const { height } = sizeMap[size];
    const optionBgActive = {
      dark: theme.colors.primary[400],
      light: theme.colors.primary[600],
    };
    const optionBgColor = opposingColor(theme, optionBgActive[colorMode]);
    const optionSelectedBg = {
      dark: theme.colors.whiteAlpha[400],
      light: theme.colors.blackAlpha[400],
    };
    const optionSelectedColor = opposingColor(theme, optionSelectedBg[colorMode]);
    const selectedDisabled = theme.colors.whiteAlpha[400];
    const placeholderColor = {
      dark: theme.colors.whiteAlpha[700],
      light: theme.colors.gray[600],
    };
    const menuBg = {
      dark: theme.colors.blackFaded[800],
      light: theme.colors.whiteFaded[50],
    };
    const menuColor = {
      dark: theme.colors.white,
      light: theme.colors.blackAlpha[800],
    };
    const scrollbar = {
      dark: theme.colors.whiteAlpha[300],
      light: theme.colors.blackAlpha[300],
    };
    const scrollbarHover = {
      dark: theme.colors.whiteAlpha[400],
      light: theme.colors.blackAlpha[400],
    };
    const scrollbarBg = {
      dark: theme.colors.whiteAlpha[50],
      light: theme.colors.blackAlpha[50],
    };
    return (
      <Select
        ref={ref}
        styles={{
          container: base => ({
            ...base,
            minHeight: height,
            borderRadius: borderRadius,
            width: '100%',
          }),
          control: (base, state) => ({
            ...base,
            minHeight: height,
            backgroundColor: bg[colorMode],
            color: color[colorMode],
            borderColor: state.isDisabled
              ? borderDisabled
              : state.isFocused
              ? borderFocused
              : border[colorMode],
            borderRadius: borderRadius,
            '&:hover': {
              borderColor: hoverColor[colorMode],
            },
          }),
          menu: base => ({
            ...base,
            backgroundColor: menuBg[colorMode],
            borderRadius: borderRadius,
          }),
          menuList: base => ({
            ...base,
            '&::-webkit-scrollbar': { width: '5px' },
            '&::-webkit-scrollbar-track': {
              backgroundColor: scrollbarBg[colorMode],
            },
            '&::-webkit-scrollbar-thumb': {
              backgroundColor: scrollbar[colorMode],
            },
            '&::-webkit-scrollbar-thumb:hover': {
              backgroundColor: scrollbarHover[colorMode],
            },

            '-ms-overflow-style': { display: 'none' },
          }),
          option: (base, state) => ({
            ...base,
            backgroundColor: state.isDisabled
              ? selectedDisabled
              : state.isSelected
              ? optionSelectedBg[colorMode]
              : state.isFocused
              ? colorSetPrimaryBg[colorMode]
              : 'transparent',
            color: state.isDisabled
              ? selectedDisabled
              : state.isFocused
              ? colorSetPrimaryColor
              : state.isSelected
              ? optionSelectedColor
              : menuColor[colorMode],
            fontSize: theme.fontSizes[size],
            '&:active': {
              backgroundColor: optionBgActive[colorMode],
              color: optionBgColor,
            },
          }),
          indicatorSeparator: base => ({
            ...base,
            backgroundColor: placeholderColor[colorMode],
          }),
          dropdownIndicator: base => ({
            ...base,
            color: placeholderColor[colorMode],
            '&:hover': {
              color: color[colorMode],
            },
          }),
          valueContainer: base => ({
            ...base,
            paddingLeft: theme.space[4],
            paddingRight: theme.space[4],
          }),
          multiValue: base => ({
            ...base,
            backgroundColor: colorSetPrimaryBg[colorMode],
          }),
          multiValueLabel: base => ({
            ...base,
            color: colorSetPrimaryColor,
          }),
          multiValueRemove: base => ({
            ...base,
            color: colorSetPrimaryColor,
            '&:hover': {
              color: colorSetPrimaryColor,
              backgroundColor: 'inherit',
            },
          }),
          singleValue: base => ({
            ...base,
            color: color[colorMode],
            fontSize: theme.fontSizes[size],
          }),
        }}
        placeholder={
          <Text color={placeholderColor[colorMode]} fontSize={size} fontFamily={theme.fonts.body}>
            {placeholder}
          </Text>
        }
        {...props}>
        {children}
      </Select>
    );
  },
);
