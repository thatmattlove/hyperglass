import { useCallback, useMemo } from 'react';
import { useConfig } from '~/context';

import type { TDeviceVrf } from '~/types';
import type { TUseVrf } from './types';

/**
 * Get a VRF configuration from the global configuration context based on its name.
 */
export function useVrf(): TUseVrf {
  const { networks } = useConfig();

  const vrfs = useMemo(() => networks.map(n => n.locations.map(l => l.vrfs).flat()).flat(), []);

  function getVrf(id: string): TDeviceVrf {
    const matching = vrfs.find(vrf => vrf._id === id);
    if (typeof matching === 'undefined') {
      if (id === '__hyperglass_default') {
        const anyDefault = vrfs.find(vrf => vrf.default === true);
        if (typeof anyDefault !== 'undefined') {
          return anyDefault;
        } else {
          throw new Error(`No matching VRF found for '${id}'`);
        }
      } else {
        throw new Error(`No matching VRF found for '${id}'`);
      }
    }
    return matching;
  }

  return useCallback(getVrf, []);
}
