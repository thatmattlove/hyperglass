import create from 'zustand';
import { useCallback } from 'react';
import * as ReactGA from 'react-ga';

import type { GAEffect, GAReturn } from './types';

interface EnabledState {
  enabled: boolean;
  enable(): void;
  disable(): void;
}

const useEnabled = create<EnabledState>(set => ({
  enabled: false,
  enable() {
    set({ enabled: true });
  },
  disable() {
    set({ enabled: false });
  },
}));

export function useGoogleAnalytics(): GAReturn {
  const { enabled, enable } = useEnabled(({ enable, enabled }) => ({ enable, enabled }));

  const runEffect = useCallback(
    (effect: GAEffect): void => {
      if (typeof window !== 'undefined' && enabled) {
        if (typeof effect === 'function') {
          effect(ReactGA);
        }
      }
    },
    [enabled],
  );

  const trackEvent = useCallback(
    (e: ReactGA.EventArgs) => {
      runEffect(ga => {
        if (process.env.NODE_ENV === 'production') {
          ga.event(e);
        } else {
          console.log(
            `%cEvent %c${JSON.stringify(e)}`,
            'background: green; color: black; padding: 0.5rem; font-size: 0.75rem;',
            'background: black; color: green; padding: 0.5rem; font-size: 0.75rem; font-weight: bold;',
          );
        }
      });
    },
    [runEffect],
  );

  const trackPage = useCallback(
    (path: string) => {
      runEffect(ga => {
        if (process.env.NODE_ENV === 'production') {
          ga.pageview(path);
        } else {
          console.log(
            `%cPage View %c${path}`,
            'background: blue; color: white; padding: 0.5rem; font-size: 0.75rem;',
            'background: white; color: blue; padding: 0.5rem; font-size: 0.75rem; font-weight: bold;',
          );
        }
      });
    },
    [runEffect],
  );

  const trackModal = useCallback(
    (path: string) => {
      runEffect(ga => {
        if (process.env.NODE_ENV === 'production') {
          ga.modalview(path);
        } else {
          console.log(
            `%cModal View %c${path}`,
            'background: red; color: white; padding: 0.5rem; font-size: 0.75rem;',
            'background: white; color: red; padding: 0.5rem; font-size: 0.75rem; font-weight: bold;',
          );
        }
      });
    },
    [runEffect],
  );

  const initialize = useCallback(
    (trackingId: string, debug: boolean) => {
      if (typeof trackingId !== 'string') {
        return;
      }

      enable();

      const initializeOpts = { titleCase: false } as ReactGA.InitializeOptions;

      if (debug) {
        initializeOpts.debug = true;
      }

      runEffect(ga => {
        ga.initialize(trackingId, initializeOpts);
      });
    },
    [runEffect, enable],
  );

  return { trackEvent, trackModal, trackPage, initialize, ga: ReactGA };
}
