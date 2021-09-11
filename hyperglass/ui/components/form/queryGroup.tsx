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
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [availableGroups, queryLocation],
  );

  function handleChange(e: TSelectOption | TSelectOption[]): void {
    let value = '';
    if (!Array.isArray(e) && e !== null) {
      selections.queryGroup.set(e);
      value = e.value;
    } else {
      selections.queryGroup.set(null);
    }
    onChange({ field: 'queryGroup', value });
  }

  return (
    <Select
      size="lg"
      name="queryGroup"
      options={options}
      aria-label={label}
      onChange={handleChange}
      value={exportState(selections.queryGroup.value)}
    />
  );
};
