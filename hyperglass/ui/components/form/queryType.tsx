import { useMemo } from 'react';
import { useFormContext } from 'react-hook-form';
import { Select } from '~/components';
import { useConfig } from '~/context';
import { useLGState, useLGMethods } from '~/hooks';

import type { TQuery, TSelectOption } from '~/types';
import type { TQuerySelectField } from './types';

function buildOptions(queryTypes: TQuery[]): TSelectOption[] {
  return queryTypes
    .filter(q => q.enable === true)
    .map(q => ({ value: q.name, label: q.display_name }));
}

export const QueryType: React.FC<TQuerySelectField> = (props: TQuerySelectField) => {
  const { onChange, label } = props;
  const { queries } = useConfig();
  const { errors } = useFormContext();
  const { selections } = useLGState();
  const { exportState } = useLGMethods();

  const options = useMemo(() => buildOptions(queries.list), [queries.list.length]);

  function handleChange(e: TSelectOption | TSelectOption[]): void {
    if (!Array.isArray(e) && e !== null) {
      selections.queryType.set(e);
      onChange({ field: 'query_type', value: e.value });
    } else {
      selections.queryType.set(null);
    }
  }

  return (
    <Select
      size="lg"
      name="query_type"
      options={options}
      aria-label={label}
      onChange={handleChange}
      value={exportState(selections.queryType.value)}
      isError={typeof errors.query_type !== 'undefined'}
    />
  );
};
