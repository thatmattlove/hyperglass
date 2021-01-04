import { useMemo } from 'react';
import { Select } from '~/components';
import { useLGMethods, useLGState } from '~/hooks';

import { TDeviceVrf, TSelectOption } from '~/types';
import type { TQueryVrf } from './types';

function buildOptions(queryVrfs: TDeviceVrf[]): TSelectOption[] {
  return queryVrfs.map(q => ({ value: q.id, label: q.display_name }));
}

export const QueryVrf: React.FC<TQueryVrf> = (props: TQueryVrf) => {
  const { vrfs, onChange, label } = props;
  const { selections } = useLGState();
  const { exportState } = useLGMethods();

  const options = useMemo(() => buildOptions(vrfs), [vrfs.length]);

  function handleChange(e: TSelectOption | TSelectOption[]): void {
    if (!Array.isArray(e) && e !== null) {
      selections.queryVrf.set(e);
      onChange({ field: 'query_vrf', value: e.value });
    } else {
      selections.queryVrf.set(null);
    }
  }

  return (
    <Select
      size="lg"
      name="query_vrf"
      options={options}
      aria-label={label}
      onChange={handleChange}
      value={exportState(selections.queryVrf.value)}
    />
  );
};
