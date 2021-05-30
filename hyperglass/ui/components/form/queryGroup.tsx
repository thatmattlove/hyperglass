import { useMemo } from 'react';
import { Select } from '~/components';
import { useLGMethods, useLGState } from '~/hooks';

import type { TNetwork, TSelectOption } from '~/types';
import type { TQueryGroup } from './types';

// function buildOptions(queryVrfs: TDeviceVrf[]): TSelectOption[] {
//   return queryVrfs.map(q => ({ value: q._id, label: q.display_name }));
// }

type QueryGroups = Record<string, string[]>;

function buildOptions(networks: TNetwork[]): QueryGroups {
  const options = {} as QueryGroups;
  for (const net of networks) {
    for (const loc of net.locations) {
      for (const directive of loc.directives) {
        for (const group of directive.groups) {
          if (Object.keys(options).includes(group)) {
            options[group] = [...options[group], loc.name];
          } else {
            options[group] = [loc.name];
          }
        }
      }
    }
  }
  return options;
}

export const QueryGroup: React.FC<TQueryGroup> = (props: TQueryGroup) => {
  const { groups, onChange, label } = props;
  const { selections, availableGroups, queryLocation, queryGroup } = useLGState();
  const { exportState } = useLGMethods();

  // const groups = useMemo(() => buildOptions(networks), []);
  // const options = useMemo<TSelectOption[]>(
  //   () => Object.keys(groups).map(key => ({ label: key, value: key })),
  //   [groups],
  // );
  // const options = useMemo<TSelectOption[]>(() => groups.map(g => ({ label: g, value: g })), [
  //   groups,
  // ]);
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
