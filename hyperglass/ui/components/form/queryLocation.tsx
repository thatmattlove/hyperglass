import { useMemo, useState } from 'react';
import { Wrap, VStack, Flex, Box, Avatar, chakra } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { useFormContext } from 'react-hook-form';
import { Select } from '~/components';
import { useConfig, useColorValue } from '~/context';
import { useOpposingColor, useFormState } from '~/hooks';

import type { DeviceGroup, SingleOption, OptionGroup, FormData } from '~/types';
import type { TQuerySelectField, LocationCardProps } from './types';

function buildOptions(devices: DeviceGroup[]): OptionGroup[] {
  return devices
    .map(group => {
      const label = group.group;
      const options = group.locations
        .map(
          loc =>
            ({
              label: loc.name,
              value: loc.id,
              group: loc.group,
              data: {
                avatar: loc.avatar,
                description: loc.description,
              },
            } as SingleOption),
        )
        .sort((a, b) => (a.label < b.label ? -1 : a.label > b.label ? 1 : 0));
      return { label, options };
    })
    .sort((a, b) => (a.label < b.label ? -1 : a.label > b.label ? 1 : 0));
}

const MotionBox = motion(Box);

const LocationCard = (props: LocationCardProps): JSX.Element => {
  const { option, onChange, defaultChecked, hasError } = props;
  const { label } = option;
  const [isChecked, setChecked] = useState(defaultChecked);

  function handleChange(value: SingleOption) {
    if (isChecked) {
      setChecked(false);
      onChange('remove', value);
    } else {
      setChecked(true);
      onChange('add', value);
    }
  }

  const bg = useColorValue('whiteAlpha.300', 'blackSolid.700');
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
      shadow="lg"
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

export const QueryLocation = (props: TQuerySelectField): JSX.Element => {
  const { onChange, label } = props;

  const { devices } = useConfig();
  const {
    formState: { errors },
  } = useFormContext<FormData>();
  const selections = useFormState(s => s.selections);
  const setSelection = useFormState(s => s.setSelection);
  const { form, filtered } = useFormState(({ form, filtered }) => ({ form, filtered }));
  const options = useMemo(() => buildOptions(devices), [devices]);
  const element = useMemo(() => {
    const groups = options.length;
    const maxOptionsPerGroup = Math.max(...options.map(opt => opt.options.length));
    const showCards = groups < 5 && maxOptionsPerGroup < 6;
    return showCards ? 'cards' : 'select';
  }, [options]);

  const noOverlap = useMemo(
    () => form.queryLocation.length > 1 && filtered.types.length === 0,
    [form, filtered],
  );

  /**
   * Update form and state when a card selections change.
   *
   * @param action Add or remove the option.
   * @param option Full option object.
   */
  function handleCardChange(action: 'add' | 'remove', option: SingleOption) {
    const exists = selections.queryLocation.map(q => q.value).includes(option.value);
    if (action === 'add' && !exists) {
      const toAdd = [...form.queryLocation, option.value];
      const newSelections = [...selections.queryLocation, option];
      setSelection('queryLocation', newSelections);
      onChange({ field: 'queryLocation', value: toAdd });
    } else if (action === 'remove' && exists) {
      const index = selections.queryLocation.findIndex(v => v.value === option.value);
      const toRemove = [...form.queryLocation.filter(v => v !== option.value)];
      setSelection(
        'queryLocation',
        selections.queryLocation.filter((_, i) => i !== index),
      );
      onChange({ field: 'queryLocation', value: toRemove });
    }
  }

  /**
   * Update form and state when select element values change.
   *
   * @param options Final value. React-select determines if an option is being added or removed and
   * only sends back the final value.
   */
  function handleSelectChange(options: SingleOption[] | SingleOption): void {
    if (Array.isArray(options)) {
      onChange({ field: 'queryLocation', value: options.map(o => o.value) });
      setSelection('queryLocation', options);
    } else {
      onChange({ field: 'queryLocation', value: options.value });
      setSelection('queryLocation', [options]);
    }
  }

  if (element === 'cards') {
    return (
      <Wrap align="flex-start" justify={{ base: 'center', lg: 'space-between' }} shouldWrapChildren>
        {options.map(group => (
          <VStack key={group.label} align="center">
            <chakra.h3 fontSize={{ base: 'sm', md: 'md' }} alignSelf="flex-start" opacity={0.5}>
              {group.label}
            </chakra.h3>
            {group.options.map(opt => {
              return (
                <LocationCard
                  key={opt.label}
                  option={opt}
                  onChange={handleCardChange}
                  hasError={noOverlap}
                  defaultChecked={form.queryLocation.includes(opt.value)}
                />
              );
            })}
          </VStack>
        ))}
      </Wrap>
    );
  } else if (element === 'select') {
    return (
      <Select
        isMulti
        size="lg"
        options={options}
        aria-label={label}
        name="queryLocation"
        onChange={handleSelectChange}
        closeMenuOnSelect={false}
        value={selections.queryLocation}
        isError={typeof errors.queryLocation !== 'undefined'}
      />
    );
  }
  return <Flex>No Locations</Flex>;
};
