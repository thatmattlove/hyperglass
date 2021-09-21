import { createContext, useContext, useMemo } from 'react';
import ReactSelect from 'react-select';
import { chakra, useDisclosure } from '@chakra-ui/react';
import { useColorMode } from '~/context';
import { Option } from './option';
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

import type { SingleOption } from '~/types';
import type { TSelectBase, TSelectContext, TReactSelectChakra } from './types';

const SelectContext = createContext<TSelectContext>({} as TSelectContext);
export const useSelectContext = (): TSelectContext => useContext(SelectContext);

const ReactSelectChakra = chakra<typeof ReactSelect, TReactSelectChakra>(ReactSelect);

export const Select: React.FC<TSelectBase> = (props: TSelectBase) => {
  const { options, multi, onSelect, isError = false, components, ...rest } = props;
  const { isOpen, onOpen, onClose } = useDisclosure();

  const { colorMode } = useColorMode();

  const selectContext = useMemo<TSelectContext>(
    () => ({ colorMode, isOpen, isError }),
    [colorMode, isError, isOpen],
  );

  const defaultOnChange = (changed: SingleOption | SingleOption[]) => {
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
  const menuPortal = useMenuPortal();
  const rsTheme = useRSTheme();

  return (
    <SelectContext.Provider value={selectContext}>
      <ReactSelectChakra
        onChange={defaultOnChange}
        onMenuClose={onClose}
        onMenuOpen={onOpen}
        isClearable={true}
        options={options}
        isMulti={multi}
        theme={rsTheme}
        components={{ Option, ...components }}
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
