import * as React from 'react';
import { forwardRef } from 'react';
import { Box, PseudoBox, Spinner, useColorMode, useTheme } from '@chakra-ui/core';
import { FiSearch } from '@meronex/icons/fi';
import { opposingColor } from 'app/util';

const btnProps = {
  display: 'inline-flex',
  appearance: 'none',
  alignItems: 'center',
  justifyContent: 'center',
  transition: 'all 250ms',
  userSelect: 'none',
  position: 'relative',
  whiteSpace: 'nowrap',
  verticalAlign: 'middle',
  lineHeight: '1.2',
  outline: 'none',
  as: 'button',
  type: 'submit',
  borderRadius: 'md',
  fontWeight: 'semibold',
};

const btnSizeMap = {
  lg: {
    height: 12,
    minWidth: 12,
    fontSize: 'lg',
    px: 6,
  },
  md: {
    height: 10,
    minWidth: 10,
    fontSize: 'md',
    px: 4,
  },
  sm: {
    height: 8,
    minWidth: 8,
    fontSize: 'sm',
    px: 3,
  },
  xs: {
    height: 6,
    minWidth: 6,
    fontSize: 'xs',
    px: 2,
  },
};

const btnBg = { dark: 'primary.300', light: 'primary.500' };
const btnBgActive = { dark: 'primary.400', light: 'primary.600' };
const btnBgHover = { dark: 'primary.200', light: 'primary.400' };

export const SubmitButton = forwardRef(
  (
    {
      isLoading = false,
      isDisabled = false,
      isActive = false,
      isFullWidth = false,
      size = 'lg',
      loadingText,
      children,
      ...props
    },
    ref,
  ) => {
    const _isDisabled = isDisabled || isLoading;
    const { colorMode } = useColorMode();
    const theme = useTheme();
    const btnColor = opposingColor(theme, btnBg[colorMode]);
    const btnColorActive = opposingColor(theme, btnBgActive[colorMode]);
    const btnColorHover = opposingColor(theme, btnBgHover[colorMode]);
    const btnSize = btnSizeMap[size];
    return (
      <PseudoBox
        ref={ref}
        disabled={_isDisabled}
        aria-disabled={_isDisabled}
        aria-label="Submit Query"
        width={isFullWidth ? 'full' : undefined}
        data-active={isActive ? 'true' : undefined}
        bg={btnBg[colorMode]}
        color={btnColor}
        _active={{ bg: btnBgActive[colorMode], color: btnColorActive }}
        _hover={{ bg: btnBgHover[colorMode], color: btnColorHover }}
        _focus={{ boxShadow: theme.shadows.outline }}
        {...btnProps}
        {...btnSize}
        {...props}>
        {isLoading ? (
          <Spinner
            position={loadingText ? 'relative' : 'absolute'}
            mr={loadingText ? 2 : 0}
            color="currentColor"
            size="1em"
          />
        ) : (
          <FiSearch color={btnColor} />
        )}
        {isLoading
          ? loadingText || (
              <Box as="span" opacity="0">
                {children}
              </Box>
            )
          : children}
      </PseudoBox>
    );
  },
);
