import { useMemo } from 'react';
import { useFormContext } from 'react-hook-form';
import { Select } from '~/components';
import { useConfig } from '~/context';
import { useLGState, useLGMethods } from '~/hooks';

import type { TNetwork, TSelectOption } from '~/types';
import type { TQuerySelectField } from './types';

function buildOptions(networks: TNetwork[]) {
  return networks
    .map(net => {
      const label = net.display_name;
      const options = net.locations
        .map(loc => ({
          label: loc.name,
          value: loc._id,
          group: net.display_name,
        }))
        .sort((a, b) => (a.label < b.label ? -1 : a.label > b.label ? 1 : 0));
      return { label, options };
    })
    .sort((a, b) => (a.label < b.label ? -1 : a.label > b.label ? 1 : 0));
}

export const QueryLocation: React.FC<TQuerySelectField> = (props: TQuerySelectField) => {
  const { onChange, label } = props;

  const { networks } = useConfig();
  const {
    formState: { errors },
  } = useFormContext();
  const { selections } = useLGState();
  const { exportState } = useLGMethods();

  const options = useMemo(() => buildOptions(networks), [networks.length]);

  function handleChange(e: TSelectOption | TSelectOption[]): void {
    if (e === null) {
      e = [];
    } else if (typeof e === 'string') {
      e = [e];
    }
    if (Array.isArray(e)) {
      const value = e.map(sel => sel!.value);
      onChange({ field: 'query_location', value });
      selections.queryLocation.set(e);
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
      value={exportState(selections.queryLocation.value)}
      isError={typeof errors.query_location !== 'undefined'}
    />
  );
};
