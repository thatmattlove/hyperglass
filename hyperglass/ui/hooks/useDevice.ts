import { useCallback, useMemo } from 'react';
import { useConfig } from '~/context';
import { flatten } from '~/util';

import type { TDevice } from '~/types';
import type { TUseDevice } from './types';

/**
 * Get a device's configuration from the global configuration context based on its name.
 */
export function useDevice(): TUseDevice {
  const { networks } = useConfig();

  const devices = useMemo(() => flatten<TDevice>(networks.map(n => n.locations)), []);

  function getDevice(id: string): TDevice {
    return devices.filter(dev => dev.name === id)[0];
  }

  return useCallback(getDevice, []);
}
