import { useMemo } from 'react';
import { Input, Text } from '@chakra-ui/react';
import { components } from 'react-select';
import { If, Select } from '~/components';
import { useColorValue } from '~/context';
import { useLGState, useDirective } from '~/hooks';
import { isSelectDirective } from '~/types';

import type { OptionProps } from 'react-select';
import type { TSelectOption, TDirective } from '~/types';
import type { TQueryTarget } from './types';

function buildOptions(directive: Nullable<TDirective>): TSelectOption[] {
  if (directive !== null && isSelectDirective(directive)) {
    return directive.options.map(o => ({
      value: o.value,
      label: o.name,
      description: o.description,
    }));
  }
  return [];
}

const Option = (props: OptionProps<Dict, false>) => {
  const { label, data } = props;
  return (
    <components.Option {...props}>
      <Text as="span">{label}</Text>
      <br />
      <Text fontSize="xs" as="span">
        {data.description}
      </Text>
    </components.Option>
  );
};

export const QueryTarget: React.FC<TQueryTarget> = (props: TQueryTarget) => {
  const { name, register, onChange, placeholder } = props;

  const bg = useColorValue('white', 'whiteAlpha.100');
  const color = useColorValue('gray.400', 'whiteAlpha.800');
  const border = useColorValue('gray.100', 'whiteAlpha.50');
  const placeholderColor = useColorValue('gray.600', 'whiteAlpha.700');

  const { queryTarget, displayTarget } = useLGState();
  const directive = useDirective();

  const options = useMemo(() => buildOptions(directive), [directive]);

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>): void {
    displayTarget.set(e.target.value);
    onChange({ field: name, value: e.target.value });
  }

  function handleSelectChange(e: TSelectOption | TSelectOption[]): void {
    if (!Array.isArray(e) && e !== null) {
      onChange({ field: name, value: e.value });
      displayTarget.set(e.value);
    }
  }

  return (
    <>
      <input {...register('query_target')} hidden readOnly value={queryTarget.value} />
      <If c={directive !== null && isSelectDirective(directive)}>
        <Select
          size="lg"
          name={name}
          options={options}
          innerRef={register}
          components={{ Option }}
          onChange={handleSelectChange}
        />
      </If>
      <If c={directive === null || !isSelectDirective(directive)}>
        <Input
          bg={bg}
          size="lg"
          color={color}
          borderRadius="md"
          borderColor={border}
          aria-label={placeholder}
          placeholder={placeholder}
          value={displayTarget.value}
          name="query_target_display"
          onChange={handleInputChange}
          _placeholder={{ color: placeholderColor }}
        />
      </If>
    </>
  );
};
