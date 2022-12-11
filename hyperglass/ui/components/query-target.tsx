import { useMemo } from 'react';
import { Input, InputGroup, InputRightElement, Text } from '@chakra-ui/react';
import { components } from 'react-select';
import { If, Then, Else } from 'react-if';
import { Select } from '~/components';
import { isSingleValue } from '~/components/select';
import { useColorValue, useDirective, useFormState } from '~/hooks';
import { isSelectDirective } from '~/types';
import { UserIP } from './user-ip';

import type { OptionProps, GroupBase } from 'react-select';
import type { UseFormRegister } from 'react-hook-form';
import type { SelectOnChange } from '~/components/select';
import type { Directive, SingleOption, OnChangeArgs, FormData } from '~/types';

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

  const bg = useColorValue('white', 'blackSolid.800');
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
    onChange({ field: name, value: [e.target.value] });
  }

  const handleSelectChange: SelectOnChange<OptionWithDescription> = e => {
    if (isSingleValue(e)) {
      onChange({ field: name, value: e.value });
      setTarget({ display: e.value });
    }
  };

  return (
    <>
      <input {...register('queryTarget')} hidden readOnly value={form.queryTarget} />
      <If condition={directive !== null && isSelectDirective(directive)}>
        <Then>
          <Select<OptionWithDescription, false>
            name={name}
            options={options}
            components={{ Option }}
            onChange={handleSelectChange}
          />
        </Then>
        <Else>
          <InputGroup size="lg">
            <Input
              bg={bg}
              color={color}
              borderRadius="md"
              borderColor={border}
              value={displayTarget}
              aria-label={placeholder}
              placeholder={placeholder}
              name="queryTargetDisplay"
              onChange={handleInputChange}
              _placeholder={{ color: placeholderColor }}
            />
            <InputRightElement w="max-content" pr={2}>
              <UserIP
                setTarget={(target: string) => {
                  setTarget({ display: target });
                  onChange({ field: name, value: target });
                }}
              />
            </InputRightElement>
          </InputGroup>
        </Else>
      </If>
    </>
  );
};
