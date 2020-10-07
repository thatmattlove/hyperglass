import * as React from 'react';
import { forwardRef } from 'react';
import { Button, useColorMode } from '@chakra-ui/core';

const Sun = ({ color, size = '1.5rem', ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 512 512"
    style={{
      height: size,
      width: size,
    }}
    strokeWidth={0}
    stroke="currentColor"
    fill="currentColor"
    {...props}>
    <path
      d="M256 32a224 224 0 00-161.393 69.035h323.045A224 224 0 00256 32zM79.148 118.965a224 224 0 00-16.976 25.16H449.74a224 224 0 00-16.699-25.16H79.148zm-27.222 45.16A224 224 0 0043.3 186.25h425.271a224 224 0 00-8.586-22.125H51.926zM36.783 210.25a224 224 0 00-3.02 19.125h444.368a224 224 0 00-3.113-19.125H36.783zm-4.752 45.125A224 224 0 0032 256a224 224 0 00.64 16.5h446.534A224 224 0 00480 256a224 224 0 00-.021-.625H32.03zm4.67 45.125a224 224 0 003.395 15.125h431.578a224 224 0 003.861-15.125H36.701zm14.307 45.125a224 224 0 006.017 13.125H454.82a224 224 0 006.342-13.125H51.008zm26.316 45.125a224 224 0 009.04 11.125H425.86a224 224 0 008.727-11.125H77.324zm45.62 45.125A224 224 0 00136.247 445h239.89a224 224 0 0012.936-9.125h-266.13z"
      fill={color || 'currentColor'}
    />
  </svg>
);

const Moon = ({ color, size = '1.5rem', ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    style={{
      height: size,
      width: size,
    }}
    strokeWidth={0}
    stroke="currentColor"
    fill="currentColor"
    {...props}>
    <path
      d="M14.53 10.53a7 7 0 01-9.058-9.058A7.003 7.003 0 008 15a7.002 7.002 0 006.53-4.47z"
      fill={color || 'currentColor'}
      fillRule="evenodd"
      clipRule="evenodd"
    />
  </svg>
);

const iconMap = { dark: Moon, light: Sun };
const outlineColor = { dark: 'primary.300', light: 'primary.600' };

export const ColorModeToggle = forwardRef((props, ref) => {
  const { colorMode, toggleColorMode } = useColorMode();
  const Icon = iconMap[colorMode];

  const label = `Switch to ${colorMode === 'light' ? 'dark' : 'light'} mode`;

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
      color="current"
      px={4}
      {...props}>
      <Icon />
    </Button>
  );
});
