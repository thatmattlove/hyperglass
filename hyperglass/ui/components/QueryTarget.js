import * as React from 'react';
import { useEffect } from 'react';
import { Input, useColorMode } from '@chakra-ui/core';

const fqdnPattern = /^(?!:\/\/)([a-zA-Z0-9-]+\.)?[a-zA-Z0-9-][a-zA-Z0-9-]+\.[a-zA-Z-]{2,6}?$/gim;

const bg = { dark: 'whiteAlpha.100', light: 'white' };
const color = { dark: 'whiteAlpha.800', light: 'gray.400' };
const border = { dark: 'whiteAlpha.50', light: 'gray.100' };
const placeholderColor = { dark: 'whiteAlpha.700', light: 'gray.600' };

export const QueryTarget = ({
  placeholder,
  register,
  unregister,
  setFqdn,
  name,
  value,
  setTarget,
  resolveTarget,
  displayValue,
  setDisplayValue,
}) => {
  const { colorMode } = useColorMode();

  const handleBlur = () => {
    if (resolveTarget && displayValue && fqdnPattern.test(displayValue)) {
      setFqdn(displayValue);
    } else if (resolveTarget && !displayValue) {
      setFqdn(false);
    }
  };
  const handleChange = e => {
    setDisplayValue(e.target.value);
    setTarget({ field: name, value: e.target.value });
  };
  const handleKeyDown = e => {
    if ([9, 13].includes(e.keyCode)) {
      handleBlur();
    }
  };
  useEffect(() => {
    register({ name });
    return () => unregister(name);
  }, [register, unregister, name]);
  return (
    <>
      <input hidden readOnly name={name} ref={register} value={value} />
      <Input
        size="lg"
        aria-label={placeholder}
        name="query_target_display"
        bg={bg[colorMode]}
        onBlur={handleBlur}
        onFocus={handleBlur}
        onKeyDown={handleKeyDown}
        value={displayValue}
        borderRadius="0.25rem"
        onChange={handleChange}
        color={color[colorMode]}
        placeholder={placeholder}
        borderColor={border[colorMode]}
        _placeholder={{
          color: placeholderColor[colorMode],
        }}
      />
    </>
  );
};
