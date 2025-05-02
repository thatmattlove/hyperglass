import { Badge, chakra, HStack } from '@chakra-ui/react';
import { components } from 'react-select';

import type { OptionProps, GroupBase } from 'react-select';
import type { SingleOption } from '~/types';

export const Option = <Opt extends SingleOption, IsMulti extends boolean>(
  props: OptionProps<Opt, IsMulti>,
): JSX.Element => {
  const { label, data } = props;
  const tags = Array.isArray(data.tags) ? (data.tags as string[]) : [];
  return (
    <components.Option<Opt, IsMulti, GroupBase<Opt>> {...props}>
      <chakra.span display={{ base: 'block', lg: 'inline' }}>{label}</chakra.span>
      {tags.length > 0 && (
        <HStack
          alignItems="center"
          ms={{ base: 0, lg: 2 }}
          display={{ base: 'flex', lg: 'inline-flex' }}
        >
          {tags.map(tag => (
            <Badge fontSize="xs" variant="subtle" key={tag} colorScheme="gray" textTransform="none">
              {tag}
            </Badge>
          ))}
        </HStack>
      )}
    </components.Option>
  );
};
