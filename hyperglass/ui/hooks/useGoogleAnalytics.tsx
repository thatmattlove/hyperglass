import { useCallback } from 'react';
import { createState, useState } from '@hookstate/core';
import * as ReactGA from 'react-ga';

import type { GAEffect, GAReturn } from './types';

const enabledState = createState<boolean>(false);

export function useGoogleAnalytics(): GAReturn {
  const enabled = useState<boolean>(enabledState);

  const useAnalytics = useCallback((effect: GAEffect): void => {
    if (typeof window !== 'undefined' && enabled.value) {
      if (typeof effect === 'function') {
        effect(ReactGA);
      }
    }
  }, []);

  const trackEvent = useCallback((e: ReactGA.EventArgs) => {
    useAnalytics(ga => {
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
  }, []);

  const trackPage = useCallback((path: string) => {
    useAnalytics(ga => {
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
  }, []);

  const trackModal = useCallback((path: string) => {
    useAnalytics(ga => {
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
  }, []);

  const initialize = useCallback((trackingId: string, debug: boolean) => {
    if (typeof trackingId !== 'string') {
      return;
    }

    enabled.set(true);

    const initializeOpts = { titleCase: false } as ReactGA.InitializeOptions;

    if (debug) {
      initializeOpts.debug = true;
    }

    useAnalytics(ga => {
      ga.initialize(trackingId, initializeOpts);
    });
  }, []);

  return { trackEvent, trackModal, trackPage, initialize, ga: ReactGA };
}
