import * as React from 'react';
import { ChakraSelect } from 'app/components';

export const QueryType = ({ queryTypes, onChange, label }) => {
  const queries = queryTypes
    .filter(q => q.enable === true)
    .map(q => {
      return { value: q.name, label: q.display_name };
    });
  return (
    <ChakraSelect
      size="lg"
      name="query_type"
      onChange={e => onChange({ field: 'query_type', value: e.value })}
      options={queries}
      aria-label={label}
    />
  );
};
