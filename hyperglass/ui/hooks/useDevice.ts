import { useCallback, useMemo } from 'react';
import { useConfig } from '~/context';

import type { TDevice } from '~/types';
import type { TUseDevice } from './types';

/**
 * Get a device's configuration from the global configuration context based on its name.
 */
export function useDevice(): TUseDevice {
  const { networks } = useConfig();

  const devices = useMemo(() => networks.map(n => n.locations).flat(), []);

  function getDevice(id: string): TDevice {
    return devices.filter(dev => dev._id === id)[0];
  }

  return useCallback(getDevice, []);
}
