import { useMemo } from 'react';
import { Input, Text } from '@chakra-ui/react';
import { components } from 'react-select';
import { If, Select } from '~/components';
import { useConfig, useColorValue } from '~/context';
import { useLGState } from '~/hooks';

import type { OptionProps } from 'react-select';
import type { TBGPCommunity, TSelectOption } from '~/types';
import type { TQueryTarget } from './types';

function buildOptions(communities: TBGPCommunity[]): TSelectOption[] {
  return communities.map(c => ({
    value: c.community,
    label: c.display_name,
    description: c.description,
  }));
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

  const { queryType, queryTarget, displayTarget } = useLGState();

  const { queries } = useConfig();

  const options = useMemo(() => buildOptions(queries.bgp_community.communities), []);

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
      <input hidden readOnly name={name} ref={register} value={queryTarget.value} />
      <If c={queryType.value === 'bgp_community' && queries.bgp_community.mode === 'select'}>
        <Select
          size="lg"
          name={name}
          options={options}
          innerRef={register}
          components={{ Option }}
          onChange={handleSelectChange}
        />
      </If>
      <If c={!(queryType.value === 'bgp_community' && queries.bgp_community.mode === 'select')}>
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
