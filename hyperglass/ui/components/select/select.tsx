import { useDisclosure } from '@chakra-ui/react';
import { createContext, forwardRef, useContext } from 'react';
import ReactSelect from 'react-select';
import { useColorMode } from '~/hooks';
import { Option } from './option';
import {
  useContainerStyle,
  useControlStyle,
  useIndicatorSeparatorStyle,
  useMenuListStyle,
  useMenuPortal,
  useMenuStyle,
  useMultiValueLabelStyle,
  useMultiValueRemoveStyle,
  useMultiValueStyle,
  useOptionStyle,
  usePlaceholderStyle,
  useRSTheme,
  useSingleValueStyle,
} from './styles';
import { isSingleValue } from './types';

import type {
  MultiValue,
  OnChangeValue,
  Props as ReactSelectProps,
  SelectInstance,
} from 'react-select';
import type { SingleOption } from '~/types';
import type { SelectContextProps, SelectProps } from './types';

const SelectContext = createContext<SelectContextProps>({} as SelectContextProps);
export const useSelectContext = (): SelectContextProps => useContext(SelectContext);

export const Select = forwardRef(
  <Opt extends SingleOption = SingleOption, IsMulti extends boolean = boolean>(
    props: SelectProps<Opt, IsMulti>,
    ref: React.Ref<SelectInstance<Opt, IsMulti>>,
  ): JSX.Element => {
    const { options, isMulti, onSelect, isError = false, components, ...rest } = props;

    const { isOpen, onOpen, onClose } = useDisclosure();

    const { colorMode } = useColorMode();

    const defaultOnChange: ReactSelectProps<Opt, IsMulti>['onChange'] = changed => {
      if (isSingleValue<Opt>(changed)) {
        changed = [changed] as unknown as OnChangeValue<Opt, IsMulti>;
      }
      if (typeof onSelect === 'function') {
        onSelect(changed as MultiValue<Opt>);
      }
    };

    const container = useContainerStyle<Opt, IsMulti>({ colorMode });
    const menu = useMenuStyle<Opt, IsMulti>({ colorMode });
    const menuList = useMenuListStyle<Opt, IsMulti>({ colorMode });
    const control = useControlStyle<Opt, IsMulti>({ colorMode });
    const option = useOptionStyle<Opt, IsMulti>({ colorMode });
    const singleValue = useSingleValueStyle<Opt, IsMulti>({ colorMode });
    const multiValue = useMultiValueStyle<Opt, IsMulti>({ colorMode });
    const multiValueLabel = useMultiValueLabelStyle<Opt, IsMulti>({ colorMode });
    const multiValueRemove = useMultiValueRemoveStyle<Opt, IsMulti>({ colorMode });
    const menuPortal = useMenuPortal<Opt, IsMulti>();
    const placeholder = usePlaceholderStyle<Opt, IsMulti>({ colorMode });
    const indicatorSeparator = useIndicatorSeparatorStyle<Opt, IsMulti>({ colorMode });
    const rsTheme = useRSTheme();

    return (
      <SelectContext.Provider value={{ colorMode, isOpen, isError }}>
        <ReactSelect<Opt, IsMulti>
          onChange={defaultOnChange}
          onMenuClose={onClose}
          onMenuOpen={onOpen}
          isClearable={true}
          options={options}
          isMulti={isMulti}
          theme={rsTheme}
          components={{ Option, ...components }}
          menuPortalTarget={typeof document !== 'undefined' ? document.body : undefined}
          ref={ref}
          styles={{
            container,
            menu,
            option,
            control,
            menuList,
            menuPortal,
            multiValue,
            singleValue,
            placeholder,
            multiValueLabel,
            multiValueRemove,
            indicatorSeparator,
          }}
          {...rest}
        />
      </SelectContext.Provider>
    );
  },
);
