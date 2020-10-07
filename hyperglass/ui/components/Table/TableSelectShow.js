import * as React from 'react';
import { Select } from '@chakra-ui/core';

export const TableSelectShow = ({ value, onChange, children, ...props }) => (
  <Select size="sm" onChange={onChange} {...props}>
    {[5, 10, 20, 30, 40, 50].map(value => (
      <option key={value} value={value}>
        Show {value}
      </option>
    ))}
    {children}
  </Select>
);
