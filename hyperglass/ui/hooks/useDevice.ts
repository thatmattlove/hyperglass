import { useCallback, useMemo } from 'react';
import { useConfig } from '~/context';

import type { Device } from '~/types';
import type { UseDevice } from './types';

/**
 * Get a device's configuration from the global configuration context based on its name.
 */
export function useDevice(): UseDevice {
  const { devices } = useConfig();

  const locations = useMemo(() => devices.map(group => group.locations).flat(), [devices]);

  function getDevice(id: string): Device | null {
    return locations.find(device => device.id === id) ?? null;
  }

  return useCallback(getDevice, [locations]);
}
