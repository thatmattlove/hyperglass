import { useMemo } from 'react';
import { Select } from '~/components';
import { useConfig } from '~/context';

import type { TQuery, TSelectOption } from '~/types';
import type { TQuerySelectField } from './types';

function buildOptions(queryTypes: TQuery[]): TSelectOption[] {
  return queryTypes
    .filter(q => q.enable === true)
    .map(q => ({ value: q.name, label: q.display_name }));
}

export const QueryType = (props: TQuerySelectField) => {
  const { onChange, label } = props;
  const { queries } = useConfig();

  const options = useMemo(() => buildOptions(queries.list), [queries.list.length]);

  function handleChange(e: TSelectOption | TSelectOption[]): void {
    if (!Array.isArray(e) && e !== null) {
      onChange({ field: 'query_type', value: e.value });
    }
  }

  return (
    <Select
      size="lg"
      name="query_type"
      options={options}
      aria-label={label}
      onChange={handleChange}
    />
  );
};
