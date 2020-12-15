import { useMemo } from 'react';
import { Select } from '~/components';
import { useConfig } from '~/context';

import type { TNetwork, TSelectOptionMulti } from '~/types';
import type { TQuerySelectField } from './types';

function buildOptions(networks: TNetwork[]) {
  return networks.map(net => {
    const label = net.display_name;
    const options = net.locations.map(loc => ({
      label: loc.display_name,
      value: loc.name,
      group: net.display_name,
    }));
    return { label, options };
  });
}

export const QueryLocation = (props: TQuerySelectField) => {
  const { onChange, label } = props;

  const { networks } = useConfig();
  const options = useMemo(() => buildOptions(networks), [networks.length]);

  function handleChange(e: TSelectOptionMulti): void {
    if (e === null) {
      e = [];
    }
    const value = e.map(sel => sel.value);
    onChange({ field: 'query_location', value });
  }

  return (
    <Select
      isMulti
      size="lg"
      options={options}
      aria-label={label}
      name="query_location"
      onChange={handleChange}
      closeMenuOnSelect={false}
    />
  );
};