import { useMemo } from 'react';
import { useFormContext } from 'react-hook-form';
import { Select } from '~/components';
import { useLGState, useLGMethods } from '~/hooks';

import type { TSelectOption } from '~/types';
import type { TQuerySelectField } from './types';

export const QueryType: React.FC<TQuerySelectField> = (props: TQuerySelectField) => {
  const { onChange, label } = props;
  const {
    formState: { errors },
  } = useFormContext();
  const { selections, availableTypes, queryType } = useLGState();
  const { exportState } = useLGMethods();

  const options = useMemo(
    () => availableTypes.map(t => ({ label: t.name.value, value: t.id.value })),
    [availableTypes],
  );

  function handleChange(e: TSelectOption | TSelectOption[]): void {
    let value = '';
    if (!Array.isArray(e) && e !== null) {
      selections.queryType.set(e);
      value = e.value;
    } else {
      selections.queryType.set(null);
      queryType.set('');
    }
    onChange({ field: 'query_type', value });
  }

  return (
    <Select
      size="lg"
      name="query_type"
      options={options}
      aria-label={label}
      onChange={handleChange}
      value={exportState(selections.queryType.value)}
      isError={'query_type' in errors}
    />
  );
};
