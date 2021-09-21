import { Badge, Box, HStack } from '@chakra-ui/react';
import { components } from 'react-select';

import type { TOption } from './types';

export const Option = (props: TOption): JSX.Element => {
  const { label, data } = props;
  const tags = Array.isArray(data.tags) ? (data.tags as string[]) : [];
  return (
    <components.Option {...props}>
      <Box as="span" d={{ base: 'block', lg: 'inline' }}>
        {label}
      </Box>
      {tags.length > 0 && (
        <HStack d={{ base: 'flex', lg: 'inline-flex' }} ms={{ base: 0, lg: 2 }} alignItems="center">
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
