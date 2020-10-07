import * as React from 'react';
import { useEffect } from 'react';
import { Text } from '@chakra-ui/core';
import { components } from 'react-select';
import { ChakraSelect } from 'app/components';

export const CommunitySelect = ({ name, communities, onChange, register, unregister }) => {
  const communitySelections = communities.map(c => {
    return {
      value: c.community,
      label: c.display_name,
      description: c.description,
    };
  });
  const Option = ({ label, data, ...props }) => {
    return (
      <components.Option {...props}>
        <Text>{label}</Text>
        <Text fontSize="xs" as="span">
          {data.description}
        </Text>
      </components.Option>
    );
  };
  useEffect(() => {
    register({ name });
    return () => unregister(name);
  }, [name, register, unregister]);
  return (
    <ChakraSelect
      innerRef={register}
      size="lg"
      name={name}
      onChange={e => {
        onChange({ field: name, value: e.value || '' });
      }}
      options={communitySelections}
      components={{ Option }}
    />
  );
};
