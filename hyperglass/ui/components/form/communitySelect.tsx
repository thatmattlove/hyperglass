import { useEffect, useMemo } from 'react';
import { Text } from '@chakra-ui/react';
import { components } from 'react-select';
import { Select } from '~/components';

import type { OptionProps } from 'react-select';
import type { TBGPCommunity, TSelectOption } from '~/types';
import type { TCommunitySelect } from './types';

function buildOptions(communities: TBGPCommunity[]): TSelectOption[] {
  return communities.map(c => ({
    value: c.community,
    label: c.display_name,
    description: c.description,
  }));
}

const Option = (props: OptionProps<Dict>) => {
  const { label, data } = props;
  return (
    <components.Option {...props}>
      <Text as="span">{label}</Text>
      <Text fontSize="xs" as="span">
        {data.description}
      </Text>
    </components.Option>
  );
};

export const CommunitySelect = (props: TCommunitySelect) => {
  const { name, communities, onChange, register, unregister } = props;

  const options = useMemo(() => buildOptions(communities), [communities.length]);

  function handleChange(e: TSelectOption | TSelectOption[]): void {
    if (!Array.isArray(e)) {
      onChange({ field: name, value: e.value });
    }
  }

  useEffect(() => {
    register({ name });
    return () => unregister(name);
  }, [name, register, unregister]);

  return (
    <Select
      size="lg"
      name={name}
      options={options}
      innerRef={register}
      onChange={handleChange}
      components={{ Option }}
    />
  );
};
