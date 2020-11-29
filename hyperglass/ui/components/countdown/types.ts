import type { CountdownRenderProps } from 'react-countdown';

export interface IRenderer extends CountdownRenderProps {
  text: string;
}

export interface ICountdown {
  timeout: number;
  text: string;
}
