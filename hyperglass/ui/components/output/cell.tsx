import { MonoField, Active, Weight, Age, Communities, RPKIState, ASPath } from './fields';

import type { TCell } from './types';

export const Cell: React.FC<TCell> = (props: TCell) => {
  const { data, rawData } = props;
  const cellId = data.column.id as keyof TRoute;
  const component = {
    med: <MonoField v={data.value} />,
    age: <Age inSeconds={data.value} />,
    prefix: <MonoField v={data.value} />,
    next_hop: <MonoField v={data.value} />,
    peer_rid: <MonoField v={data.value} />,
    source_as: <MonoField v={data.value} />,
    active: <Active isActive={data.value} />,
    source_rid: <MonoField v={data.value} />,
    local_preference: <MonoField v={data.value} />,
    communities: <Communities communities={data.value} />,
    as_path: <ASPath path={data.value} active={data.row.values.active} />,
    rpki_state: <RPKIState state={data.value} active={data.row.values.active} />,
    weight: <Weight weight={data.value} winningWeight={rawData.winning_weight} />,
  };
  return component[cellId] ?? <> </>;
};
