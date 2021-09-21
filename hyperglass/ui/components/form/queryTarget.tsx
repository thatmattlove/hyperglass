import { useMemo } from 'react';
import { Input, Text } from '@chakra-ui/react';
import { components } from 'react-select';
import { If, Select } from '~/components';
import { useColorValue } from '~/context';
import { useDirective, useFormState } from '~/hooks';
import { isSelectDirective } from '~/types';
import type { OptionProps } from 'react-select';
import type { Directive, SingleOption } from '~/types';
import type { TQueryTarget } from './types';

function buildOptions(directive: Nullable<Directive>): SingleOption[] {
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
  const displayTarget = useFormState(s => s.target.display);
  const setTarget = useFormState(s => s.setTarget);
  const form = useFormState(s => s.form);
  const directive = useDirective();

  const options = useMemo(() => buildOptions(directive), [directive]);

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>): void {
    setTarget({ display: e.target.value });
    onChange({ field: name, value: e.target.value });
  }

  function handleSelectChange(e: SingleOption | SingleOption[]): void {
    if (!Array.isArray(e) && e !== null) {
      onChange({ field: name, value: e.value });
      setTarget({ display: e.value });
    }
  }

  return (
    <>
      <input {...register('queryTarget')} hidden readOnly value={form.queryTarget} />
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
          value={displayTarget}
          name="queryTargetDisplay"
          onChange={handleInputChange}
          _placeholder={{ color: placeholderColor }}
        />
      </If>
    </>
  );
};
