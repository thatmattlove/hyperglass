import * as React from 'react';
import { ChakraSelect } from 'app/components';

export const QueryVrf = ({ vrfs, onChange, label }) => (
  <ChakraSelect
    size="lg"
    options={vrfs}
    name="query_vrf"
    aria-label={label}
    onChange={e => onChange({ field: 'query_vrf', value: e.value })}
  />
);
