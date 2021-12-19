import { useMemo, useState } from 'react';
import { Flex, Box, Avatar, chakra } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { useColorValue } from '~/context';
import { useOpposingColor } from '~/hooks';

import type { SingleOption } from '~/types';
import type { LocationOption } from './query-location';

interface LocationCardProps {
  option: SingleOption;
  defaultChecked: boolean;
  onChange(a: 'add' | 'remove', v: SingleOption): void;
  hasError: boolean;
}

const MotionBox = motion(Box);

export const LocationCard = (props: LocationCardProps): JSX.Element => {
  const { option, onChange, defaultChecked, hasError } = props;
  const { label } = option;
  const [isChecked, setChecked] = useState(defaultChecked);

  function handleChange(value: LocationOption) {
    if (isChecked) {
      setChecked(false);
      onChange('remove', value);
    } else {
      setChecked(true);
      onChange('add', value);
    }
  }

  const bg = useColorValue('white', 'blackSolid.800');
  const imageBorder = useColorValue('gray.600', 'whiteAlpha.800');
  const fg = useOpposingColor(bg);
  const checkedBorder = useColorValue('blue.400', 'blue.300');
  const errorBorder = useColorValue('red.500', 'red.300');

  const borderColor = useMemo(
    () =>
      hasError && isChecked
        ? // Highlight red when there are no overlapping query types for the locations selected.
          errorBorder
        : isChecked && !hasError
        ? // Highlight blue when any location is selected and there is no error.
          checkedBorder
        : // Otherwise, no border.
          'transparent',

    [hasError, isChecked, checkedBorder, errorBorder],
  );
  return (
    <MotionBox
      py={4}
      px={6}
      bg={bg}
      w="100%"
      minW="xs"
      maxW="sm"
      mx="auto"
      shadow="sm"
      key={label}
      rounded="lg"
      cursor="pointer"
      borderWidth="1px"
      borderStyle="solid"
      whileHover={{ scale: 1.05 }}
      borderColor={borderColor}
      onClick={(e: React.MouseEvent) => {
        e.preventDefault();
        handleChange(option);
      }}
    >
      <Flex justifyContent="space-between" alignItems="center">
        <chakra.h2
          color={fg}
          fontWeight="bold"
          mt={{ base: 2, md: 0 }}
          fontSize={{ base: 'lg', md: 'xl' }}
        >
          {label}
        </chakra.h2>
        <Avatar
          color={fg}
          fit="cover"
          alt={label}
          name={label}
          boxSize={12}
          rounded="full"
          borderWidth={1}
          bg="whiteAlpha.300"
          borderStyle="solid"
          borderColor={imageBorder}
          src={(option.data?.avatar as string) ?? undefined}
        />
      </Flex>

      {option?.data?.description && (
        <chakra.p mt={2} color={fg} opacity={0.6} fontSize="sm">
          {option.data.description as string}
        </chakra.p>
      )}
    </MotionBox>
  );
};
