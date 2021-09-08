import { useMemo } from 'react';
import { Select } from '~/components';
import { useLGMethods, useLGState } from '~/hooks';

import type { TSelectOption } from '~/types';
import type { TQueryGroup } from './types';

export const QueryGroup: React.FC<TQueryGroup> = (props: TQueryGroup) => {
  const { onChange, label } = props;
  const { selections, availableGroups, queryLocation } = useLGState();
  const { exportState } = useLGMethods();

  const options = useMemo<TSelectOption[]>(
    () => availableGroups.map(g => ({ label: g.value, value: g.value })),
    [availableGroups.length, queryLocation.length],
  );

  function handleChange(e: TSelectOption | TSelectOption[]): void {
    let value = '';
    if (!Array.isArray(e) && e !== null) {
      selections.queryGroup.set(e);
      value = e.value;
    } else {
      selections.queryGroup.set(null);
    }
    onChange({ field: 'query_group', value });
  }

  return (
    <Select
      size="lg"
      name="query_group"
      options={options}
      aria-label={label}
      onChange={handleChange}
      value={exportState(selections.queryGroup.value)}
    />
  );
};
