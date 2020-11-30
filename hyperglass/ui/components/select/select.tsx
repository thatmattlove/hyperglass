import { createContext, useContext, useMemo, useState } from 'react';
import ReactSelect from 'react-select';
import { Box } from '@chakra-ui/react';
import { useColorMode } from '~/context';
import {
  useRSTheme,
  useMenuStyle,
  useMenuPortal,
  useOptionStyle,
  useControlStyle,
  useMenuListStyle,
  useMultiValueStyle,
  usePlaceholderStyle,
  useSingleValueStyle,
  useMultiValueLabelStyle,
  useMultiValueRemoveStyle,
  useIndicatorSeparatorStyle,
} from './styles';

import type { TSelect, TSelectOption, TSelectContext, TBoxAsReactSelect } from './types';

const SelectContext = createContext<TSelectContext>(Object());
export const useSelectContext = () => useContext(SelectContext);

const ReactSelectAsBox = (props: TBoxAsReactSelect) => <Box as={ReactSelect} {...props} />;

export const Select = (props: TSelect) => {
  const { ctl, options, multi, onSelect, ...rest } = props;
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const { colorMode } = useColorMode();

  const selectContext = useMemo<TSelectContext>(() => ({ colorMode, isOpen }), [colorMode, isOpen]);

  const handleChange = (changed: TSelectOption | TSelectOption[]) => {
    if (!Array.isArray(changed)) {
      changed = [changed];
    }
    if (typeof onSelect === 'function') {
      onSelect(changed);
    }
  };

  const multiValue = useMultiValueStyle({ colorMode });
  const multiValueLabel = useMultiValueLabelStyle({ colorMode });
  const multiValueRemove = useMultiValueRemoveStyle({ colorMode });
  const menuPortal = useMenuPortal({ colorMode });
  const rsTheme = useRSTheme({ colorMode });

  return (
    <SelectContext.Provider value={selectContext}>
      <ReactSelectAsBox
        as={ReactSelect}
        options={options}
        isMulti={multi}
        onChange={handleChange}
        ref={ctl}
        onMenuClose={() => {
          isOpen && setIsOpen(false);
        }}
        onMenuOpen={() => {
          !isOpen && setIsOpen(true);
        }}
        theme={rsTheme}
        styles={{
          menuPortal,
          multiValue,
          multiValueLabel,
          multiValueRemove,
          menu: useMenuStyle,
          option: useOptionStyle,
          control: useControlStyle,
          menuList: useMenuListStyle,
          singleValue: useSingleValueStyle,
          placeholder: usePlaceholderStyle,
          indicatorSeparator: useIndicatorSeparatorStyle,
        }}
        {...rest}
      />
    </SelectContext.Provider>
  );
};
