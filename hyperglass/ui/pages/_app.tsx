import { QueryClient, QueryClientProvider } from 'react-query';

import type { AppProps } from 'next/app';

const queryClient = new QueryClient();

const App = (props: AppProps): JSX.Element => {
  const { Component, pageProps } = props;

  return (
    <QueryClientProvider client={queryClient}>
      <Component {...pageProps} />
    </QueryClientProvider>
  );
};

export default App;
