import type * as ReactGA from 'react-ga';

export type GAEffect = (ga: typeof ReactGA) => void;

export interface GAReturn {
  ga: typeof ReactGA;
  initialize(trackingId: string | null, debug: boolean): void;
  trackPage(path: string): void;
  trackModal(path: string): void;
  trackEvent(event: ReactGA.EventArgs): void;
}
