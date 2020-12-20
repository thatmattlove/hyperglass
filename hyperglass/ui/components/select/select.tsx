import { createContext, useContext, useMemo } from 'react';
import ReactSelect from 'react-select';
import { Box, useDisclosure } from '@chakra-ui/react';
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

import type { TSelectOption } from '~/types';
import type { TSelectBase, TSelectContext, TBoxAsReactSelect } from './types';

const SelectContext = createContext<TSelectContext>(Object());
export const useSelectContext = () => useContext(SelectContext);

const ReactSelectAsBox = (props: TBoxAsReactSelect) => <Box as={ReactSelect} {...props} />;

export const Select = (props: TSelectBase) => {
  const { ctl, options, multi, onSelect, isError = false, ...rest } = props;
  const { isOpen, onOpen, onClose } = useDisclosure();

  const { colorMode } = useColorMode();

  const selectContext = useMemo<TSelectContext>(() => ({ colorMode, isOpen, isError }), [
    colorMode,
    isError,
    isOpen,
  ]);

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
        onChange={handleChange}
        onMenuClose={onClose}
        onMenuOpen={onOpen}
        options={options}
        as={ReactSelect}
        isMulti={multi}
        theme={rsTheme}
        ref={ctl}
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
