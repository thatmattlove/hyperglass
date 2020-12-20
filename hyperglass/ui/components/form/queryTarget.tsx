import { Input } from '@chakra-ui/react';
import { useColorValue } from '~/context';
import { useLGState } from '~/hooks';

import type { TQueryTarget } from './types';

const fqdnPattern = /^(?!:\/\/)([a-zA-Z0-9-]+\.)?[a-zA-Z0-9-][a-zA-Z0-9-]+\.[a-zA-Z-]{2,6}?$/gim;

export const QueryTarget = (props: TQueryTarget) => {
  const { name, register, setTarget, placeholder, resolveTarget } = props;

  const bg = useColorValue('white', 'whiteAlpha.100');
  const color = useColorValue('gray.400', 'whiteAlpha.800');
  const border = useColorValue('gray.100', 'whiteAlpha.50');
  const placeholderColor = useColorValue('gray.600', 'whiteAlpha.700');

  const { queryTarget, fqdnTarget, displayTarget } = useLGState();

  function handleChange(e: React.ChangeEvent<HTMLInputElement>): void {
    displayTarget.set(e.target.value);
    setTarget({ field: name, value: e.target.value });

    if (resolveTarget && displayTarget.value && fqdnPattern.test(displayTarget.value)) {
      fqdnTarget.set(displayTarget.value);
    }
  }

  return (
    <>
      <input hidden readOnly name={name} ref={register} value={queryTarget.value} />
      <Input
        bg={bg}
        size="lg"
        color={color}
        borderRadius="md"
        value={displayTarget.value}
        borderColor={border}
        onChange={handleChange}
        aria-label={placeholder}
        placeholder={placeholder}
        name="query_target_display"
        _placeholder={{ color: placeholderColor }}
      />
    </>
  );
};
