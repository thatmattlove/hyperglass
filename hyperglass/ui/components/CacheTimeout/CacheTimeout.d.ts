namespace ReactCountdown {
  type CountdownRender = import('react-countdown').CountdownRenderProps;
}

interface IRenderer extends ReactCountdown.CountdownRender {
  text: string;
}

interface ICountdown {
  timeout: number;
  text: string;
}
