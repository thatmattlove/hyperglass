import { forwardRef } from 'react';
import { Box, Spinner } from '@chakra-ui/react';
import { FiSearch } from '@meronex/icons/fi';
import { useColorValue } from '~/context';
import { useOpposingColor } from '~/hooks';

import type { TSubmitButton, TButtonSizeMap } from './types';

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
} as TButtonSizeMap;

export const SubmitButton = forwardRef<HTMLDivElement, TSubmitButton>((props, ref) => {
  const {
    isLoading = false,
    isDisabled = false,
    isActive = false,
    isFullWidth = false,
    size = 'lg',
    loadingText,
    children,
    ...rest
  } = props;
  const _isDisabled = isDisabled || isLoading;

  const bg = useColorValue('primary.500', 'primary.300');
  const bgActive = useColorValue('primary.600', 'primary.400');
  const bgHover = useColorValue('primary.400', 'primary.200');
  const color = useOpposingColor(bg);
  const colorActive = useOpposingColor(bgActive);
  const colorHover = useOpposingColor(bgHover);

  const btnSize = btnSizeMap[size];

  return (
    <Box
      bg={bg}
      ref={ref}
      as="button"
      color={color}
      type="submit"
      outline="none"
      lineHeight="1.2"
      appearance="none"
      userSelect="none"
      borderRadius="md"
      alignItems="center"
      position="relative"
      whiteSpace="nowrap"
      display="inline-flex"
      fontWeight="semibold"
      disabled={_isDisabled}
      transition="all 250ms"
      verticalAlign="middle"
      justifyContent="center"
      aria-label="Submit Query"
      aria-disabled={_isDisabled}
      _focus={{ boxShadow: 'outline' }}
      width={isFullWidth ? 'full' : undefined}
      data-active={isActive ? 'true' : undefined}
      _hover={{ bg: bgHover, color: colorHover }}
      _active={{ bg: bgActive, color: colorActive }}
      {...btnSize}
      {...rest}>
      {isLoading ? (
        <Spinner
          position={loadingText ? 'relative' : 'absolute'}
          mr={loadingText ? 2 : 0}
          color="currentColor"
          size="1em"
        />
      ) : (
        <FiSearch color={color} />
      )}
      {isLoading
        ? loadingText || (
            <Box as="span" opacity="0">
              {children}
            </Box>
          )
        : children}
    </Box>
  );
});
