import { useMemo } from 'react';
import { useFormContext } from 'react-hook-form';
import { uniqBy } from 'lodash';
import { Select } from '~/components';
import { useConfig } from '~/context';
import { useLGState, useLGMethods } from '~/hooks';

import type { TNetwork, TSelectOption } from '~/types';
import type { TQuerySelectField } from './types';

// function buildOptions(queryTypes: TQuery[]): TSelectOption[] {
//   return queryTypes
//     .filter(q => q.enable === true)
//     .map(q => ({ value: q.name, label: q.display_name }));
// }

// function* buildOptions(networks: TNetwork[]): Generator<TSelectOption> {
//   for (const net of networks) {
//     for (const loc of net.locations) {
//       for (const directive of loc.directives) {
//         const { name } = directive;
//         yield { value: name, label: name };
//       }
//     }
//   }
// }

export const QueryType: React.FC<TQuerySelectField> = (props: TQuerySelectField) => {
  const { onChange, label } = props;
  // const {
  //   queries,
  //   networks,
  // } = useConfig();
  const {
    formState: { errors },
  } = useFormContext();
  const { selections, availableTypes, queryType } = useLGState();
  const { exportState } = useLGMethods();

  // const options = useMemo(() => buildOptions(queries.list), [queries.list.length]);
  // const options = useMemo(() => Array.from(buildOptions(networks)), []);
  // const options = useMemo(
  //   () => uniqBy<TSelectOption>(Array.from(buildOptions(networks)), opt => opt?.label),
  //   [],
  // );
  const options = useMemo(() => availableTypes.map(t => ({ label: t.value, value: t.value })), [
    availableTypes.length,
  ]);

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
      // isError={typeof errors.query_type !== 'undefined'}
      isError={'query_type' in errors}
    />
  );
};
