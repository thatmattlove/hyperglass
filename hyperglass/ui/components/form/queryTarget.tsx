import { useEffect } from 'react';
import { Input } from '@chakra-ui/react';
import { useColorValue } from '~/context';

import type { TQueryTarget } from './types';

const fqdnPattern = /^(?!:\/\/)([a-zA-Z0-9-]+\.)?[a-zA-Z0-9-][a-zA-Z0-9-]+\.[a-zA-Z-]{2,6}?$/gim;

export const QueryTarget = (props: TQueryTarget) => {
  const {
    name,
    value,
    setFqdn,
    register,
    setTarget,
    unregister,
    placeholder,
    displayValue,
    resolveTarget,
    setDisplayValue,
  } = props;

  const bg = useColorValue('white', 'whiteAlpha.100');
  const color = useColorValue('gray.400', 'whiteAlpha.800');
  const border = useColorValue('gray.100', 'whiteAlpha.50');
  const placeholderColor = useColorValue('gray.600', 'whiteAlpha.700');

  function handleBlur(): void {
    if (resolveTarget && displayValue && fqdnPattern.test(displayValue)) {
      setFqdn(displayValue);
    } else if (resolveTarget && !displayValue) {
      setFqdn(null);
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>): void {
    setDisplayValue(e.target.value);
    setTarget({ field: name, value: e.target.value });
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>): void {
    if (['Tab', 'NumpadEnter'].includes(e.key)) {
      handleBlur();
    }
  }

  useEffect(() => {
    register({ name });
    return () => unregister(name);
  }, [register, unregister, name]);

  return (
    <>
      <input hidden readOnly name={name} ref={register} value={value} />
      <Input
        bg={bg}
        size="lg"
        color={color}
        borderRadius="md"
        onBlur={handleBlur}
        onFocus={handleBlur}
        value={displayValue}
        borderColor={border}
        onChange={handleChange}
        aria-label={placeholder}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        name="query_target_display"
        _placeholder={{ color: placeholderColor }}
      />
    </>
  );
};
