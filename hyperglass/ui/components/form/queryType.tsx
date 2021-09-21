import { useMemo } from 'react';
import create from 'zustand';
import { Box, Button, HStack, useRadio, useRadioGroup } from '@chakra-ui/react';
import { useFormContext } from 'react-hook-form';
import { components } from 'react-select';
import { Select } from '~/components';
import { useFormState } from '~/hooks';

import type { UseRadioProps } from '@chakra-ui/react';
import type { MenuListComponentProps } from 'react-select';
import type { SingleOption, OptionGroup, SelectOption } from '~/types';
import type { TOptions } from '~/components/select';
import type { TQuerySelectField } from './types';

function sorter<T extends SingleOption | OptionGroup>(a: T, b: T): number {
  return a.label < b.label ? -1 : a.label > b.label ? 1 : 0;
}

type UserFilter = {
  selected: string;
  setSelected(n: string): void;
  filter(candidate: SelectOption<{ group: string | null }>, input: string): boolean;
};

const useFilter = create<UserFilter>((set, get) => ({
  selected: '',
  setSelected(newValue: string) {
    set(() => ({ selected: newValue }));
  },
  filter(candidate, input): boolean {
    const {
      label,
      data: { group },
    } = candidate;
    if (input && (label || group)) {
      const search = input.toLowerCase();
      if (group) {
        return label.toLowerCase().indexOf(search) > -1 || group.toLowerCase().indexOf(search) > -1;
      }
      return label.toLowerCase().indexOf(search) > -1;
    }
    const { selected } = get();
    if (selected !== '' && selected === group) {
      return true;
    }
    if (selected === '') {
      return true;
    }
    return false;
  },
}));

function useOptions() {
  const filtered = useFormState(s => s.filtered);
  return useMemo((): TOptions => {
    const groupNames = new Set(
      filtered.types
        .filter(t => t.groups.length > 0)
        .map(t => t.groups)
        .flat(),
    );
    const optGroups: OptionGroup[] = Array.from(groupNames).map(group => ({
      label: group,
      options: filtered.types
        .filter(t => t.groups.includes(group))
        .map(t => ({ label: t.name, value: t.id, group }))
        .sort(sorter),
    }));

    const noGroups: OptionGroup = {
      label: '',
      options: filtered.types
        .filter(t => t.groups.length === 0)
        .map(t => ({ label: t.name, value: t.id, group: '' }))
        .sort(sorter),
    };

    return [noGroups, ...optGroups].sort(sorter);
  }, [filtered.types]);
}

const GroupFilter = (props: React.PropsWithChildren<UseRadioProps>): JSX.Element => {
  const { children, ...rest } = props;
  const {
    getInputProps,
    getCheckboxProps,
    getLabelProps,
    htmlProps,
    state: { isChecked },
  } = useRadio(rest);
  const label = getLabelProps();
  const input = getInputProps();
  const checkbox = getCheckboxProps();

  return (
    <Box as="label" {...label}>
      <input {...input} />
      <Button
        {...checkbox}
        {...htmlProps}
        variant={isChecked ? 'solid' : 'outline'}
        colorScheme="gray"
        size="sm"
      >
        {children}
      </Button>
    </Box>
  );
};

const MenuList = (props: MenuListComponentProps<TOptions, false>) => {
  const { children, ...rest } = props;
  const filtered = useFormState(s => s.filtered);
  const selected = useFilter(state => state.selected);
  const setSelected = useFilter(state => state.setSelected);

  const { getRadioProps, getRootProps } = useRadioGroup({
    name: 'queryGroup',
    value: selected,
  });

  function handleClick(value: string): void {
    setSelected(value);
  }
  return (
    <components.MenuList {...rest}>
      <HStack pt={4} px={2} zIndex={2} {...getRootProps()}>
        <GroupFilter {...getRadioProps({ value: '', onClick: () => handleClick('') })}>
          None
        </GroupFilter>
        {filtered.groups.map(value => {
          return (
            <GroupFilter
              key={value}
              {...getRadioProps({ value, onClick: () => handleClick(value) })}
            >
              {value}
            </GroupFilter>
          );
        })}
      </HStack>
      {children}
    </components.MenuList>
  );
};

export const QueryType = (props: TQuerySelectField): JSX.Element => {
  const { onChange, label } = props;
  const {
    formState: { errors },
  } = useFormContext();
  const setSelection = useFormState(s => s.setSelection);
  const selections = useFormState(s => s.selections);
  const setFormValue = useFormState(s => s.setFormValue);
  const options = useOptions();
  const { filter } = useFilter(); // Intentionally re-render on any changes

  function handleChange(e: SingleOption | SingleOption[]): void {
    let value = '';
    if (!Array.isArray(e) && e !== null) {
      // setFormValue('queryType', e.value);
      setSelection('queryType', e);
      value = e.value;
    } else {
      setFormValue('queryType', '');
      setSelection('queryType', null);
    }
    onChange({ field: 'queryType', value });
  }

  return (
    <Select
      size="lg"
      name="queryType"
      options={options}
      aria-label={label}
      filterOption={filter}
      onChange={handleChange}
      components={{ MenuList }}
      isError={'queryType' in errors}
      value={selections.queryType}
    />
  );
};
