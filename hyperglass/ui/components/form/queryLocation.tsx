import { useMemo } from 'react';
import { Select } from '~/components';

import type { TNetwork } from '~/types';
import type { TQueryLocation, OnChangeArgs } from './types';

function isOnChangeArgsArray(e: OnChangeArgs | OnChangeArgs[]): e is OnChangeArgs[] {
  return Array.isArray(e);
}

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

export const QueryLocation = (props: TQueryLocation) => {
  const { locations, onChange, label } = props;

  const options = useMemo(() => buildOptions(locations), [locations.length]);

  function handleChange(e: OnChangeArgs | OnChangeArgs[]): void {
    if (isOnChangeArgsArray(e)) {
      const value = e.map(sel => sel.value as string);
      onChange({ label: 'query_location', value });
    }
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
