import { useCallback, useMemo } from 'react';
import { useConfig } from '~/context';

import type { Device } from '~/types';

export type UseDeviceReturn = (
  /** Device's ID, e.g. the device.name field.*/
  deviceId: string,
) => Nullable<Device>;

/**
 * Get a device's configuration from the global configuration context based on its name.
 */
export function useDevice(): UseDeviceReturn {
  const { devices } = useConfig();

  const locations = useMemo<Device[]>(() => devices.flatMap(group => group.locations), [devices]);

  function getDevice(id: string): Nullable<Device> {
    return locations.find(device => device.id === id) ?? null;
  }

  return useCallback<UseDeviceReturn>(getDevice, [locations]);
}
