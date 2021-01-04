import type { CountdownRenderProps } from 'react-countdown';

export interface TRenderer extends CountdownRenderProps {
  text: string;
}

export interface TCountdown {
  timeout: number;
  text: string;
}
