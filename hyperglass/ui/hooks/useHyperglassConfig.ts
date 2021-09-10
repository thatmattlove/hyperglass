import { useState } from 'react';
import { useQuery } from 'react-query';
import { getHyperglassConfig } from '~/util';

import type { UseQueryResult } from 'react-query';
import type { ConfigLoadError } from '~/util';
import type { IConfig } from '~/types';

type UseHyperglassConfig = UseQueryResult<IConfig, ConfigLoadError> & {
  /**
   * Initial configuration load has failed.
   */
  initFailed: boolean;

  /**
   * If `true`, the initial loading component should be rendered.
   */
  isLoadingInitial: boolean;

  /**
   * If `true`, an error component should be rendered.
   */
  showError: boolean;

  /**
   * Data has been loaded and there are no errors.
   */
  ready: boolean;
};

/**
 * Retrieve and cache hyperglass's UI configuration from the hyperglass API.
 */
export function useHyperglassConfig(): UseHyperglassConfig {
  // Track whether or not the initial configuration load has failed. If it has not (default), the
  // UI will display the `<Loading/>` component. If it has failed, the `<LoadError/>` component
  // will be displayed, which will also show the loading state.
  const [initFailed, setInitFailed] = useState<boolean>(false);

  const query = useQuery<IConfig, ConfigLoadError>({
    queryKey: 'hyperglass-ui-config',
    queryFn: getHyperglassConfig,
    refetchOnWindowFocus: false,
    refetchInterval: 10000,
    cacheTime: Infinity,
    onError: () => {
      if (!initFailed) {
        setInitFailed(true);
      }
    },
    onSuccess: () => {
      if (initFailed) {
        setInitFailed(false);
      }
    },
  });
  const isLoadingInitial = !initFailed && query.isLoading && !query.isError;
  const showError = query.isError || (initFailed && query.isLoading);
  const ready = query.isSuccess && !query.isLoading;
  return { initFailed, isLoadingInitial, showError, ready, ...query };
}
