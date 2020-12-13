import { useCallback, useMemo } from 'react';
import { useConfig } from '~/context';
import { flatten } from '~/util';

import type { TDevice } from '~/types';

export function useDevice(): (i: string) => TDevice {
  const { networks } = useConfig();
  const devices = useMemo(() => flatten<TDevice>(networks.map(n => n.locations)), []);

  function getDevice(id: string): TDevice {
    return devices.filter(dev => dev.name === id)[0];
  }
  return useCallback(getDevice, []);
}
