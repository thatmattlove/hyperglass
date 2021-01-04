import { Select } from '@chakra-ui/react';
import { SelectProps } from '@chakra-ui/react';

export const TableSelectShow: React.FC<SelectProps> = (props: SelectProps) => {
  const { value, ...rest } = props;
  return (
    <Select size="sm" {...rest}>
      {[5, 10, 20, 30, 40, 50].map(value => (
        <option key={value} value={value}>
          Show {value}
        </option>
      ))}
    </Select>
  );
};
