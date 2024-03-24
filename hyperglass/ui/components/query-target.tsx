import { Input, InputGroup, InputRightElement, Text } from '@chakra-ui/react';
import { useMemo } from 'react';
import { components } from 'react-select';
import { Select } from '~/components';
import { isSingleValue } from '~/components/select';
import { useDirective, useFormState } from '~/hooks';
import { isSelectDirective } from '~/types';
import { UserIP } from './user-ip';

import { type UseFormRegister, useForm } from 'react-hook-form';
import type { GroupBase, OptionProps } from 'react-select';
import type { SelectOnChange } from '~/components/select';
import type { Directive, FormData, OnChangeArgs, SingleOption } from '~/types';

type OptionWithDescription = SingleOption<{ description: string | null }>;

interface QueryTargetProps {
  name: string;
  placeholder: string;
  onChange(e: OnChangeArgs): void;
  register: UseFormRegister<FormData>;
}

function buildOptions(directive: Nullable<Directive>): OptionWithDescription[] {
  if (directive !== null && isSelectDirective(directive)) {
    return directive.options.map(o => ({
      value: o.value,
      label: o.name,
      data: { description: o.description },
    }));
  }
  return [];
}

const Option = (props: OptionProps<OptionWithDescription, false>) => {
  const { label, data } = props;
  return (
    <components.Option<OptionWithDescription, false, GroupBase<OptionWithDescription>> {...props}>
      <Text as="span">{label}</Text>
      <br />
      <Text fontSize="xs" as="span">
        {data.data?.description}
      </Text>
    </components.Option>
  );
};

export const QueryTarget = (props: QueryTargetProps): JSX.Element => {
  const { name, register, onChange, placeholder } = props;

  const displayTarget = useFormState(s => s.target.display);
  const setTarget = useFormState(s => s.setTarget);
  const queryTarget = useFormState(s => s.form.queryTarget);
  const directive = useDirective();

  const options = useMemo(() => buildOptions(directive), [directive]);
  const isSelect = useMemo(() => directive !== null && isSelectDirective(directive), [directive]);

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>): void {
    setTarget({ display: e.target.value });
    onChange({ field: name, value: [e.target.value] });
  }

  const handleSelectChange: SelectOnChange<OptionWithDescription> = e => {
    if (isSingleValue(e)) {
      onChange({ field: name, value: e.value });
      setTarget({ display: e.value });
    }
  };

  const handleUserIPChange = (target: string): void => {
    setTarget({ display: target });
    onChange({ field: name, value: target });
  };

  return (
    <>
      <input {...register('queryTarget')} hidden readOnly value={queryTarget} />
      {isSelect ? (
        <Select<OptionWithDescription, false>
          name={name}
          options={options}
          components={{ Option }}
          onChange={handleSelectChange}
        />
      ) : (
        <InputGroup size="lg">
          <Input
            bg="white"
            color="gray.400"
            borderRadius="md"
            borderColor="gray.100"
            value={displayTarget}
            aria-label={placeholder}
            placeholder={placeholder}
            name="queryTargetDisplay"
            onChange={handleInputChange}
            _placeholder={{ color: 'gray.600' }}
            _dark={{
              bg: 'blackSolid.800',
              color: 'whiteAlpha.800',
              borderColor: 'whiteAlpha.50',
              _placeholder: { color: 'whiteAlpha.700' },
            }}
          />
          <InputRightElement w="max-content" pr={2}>
            <UserIP setTarget={handleUserIPChange} />
          </InputRightElement>
        </InputGroup>
      )}
    </>
  );
};
