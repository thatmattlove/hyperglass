import { useEffect, useMemo } from 'react';
import { useQuery } from 'react-query';
import { useConfig } from '~/context';
import { fetchWithTimeout } from '~/util';

import type { QueryFunction, QueryFunctionContext, QueryObserverResult } from 'react-query';
import type { TFormQuery } from '~/types';
import type { LGQueryKey, LGQueryOptions } from './types';

/**
 * Custom hook handle submission of a query to the hyperglass backend.
 */
export function useLGQuery(
  query: TFormQuery,
  options: LGQueryOptions = {} as LGQueryOptions,
): QueryObserverResult<QueryResponse> {
  const { requestTimeout, cache } = useConfig();
  const controller = useMemo(() => new AbortController(), []);

  const runQuery: QueryFunction<QueryResponse, LGQueryKey> = async (
    ctx: QueryFunctionContext<LGQueryKey>,
  ): Promise<QueryResponse> => {
    const [url, data] = ctx.queryKey;
    const { queryLocation, queryTarget, queryType } = data;
    const res = await fetchWithTimeout(
      url,
      {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          queryLocation,
          queryTarget,
          queryType,
        }),
        mode: 'cors',
      },
      requestTimeout * 1000,
      controller,
    );
    try {
      return await res.json();
    } catch (err) {
      throw new Error(res.statusText);
    }
  };

  // Cancel any still-running queries on unmount.
  useEffect(
    () => () => {
      controller.abort();
    },
    [controller],
  );

  return useQuery<QueryResponse, Response | QueryResponse | Error, QueryResponse, LGQueryKey>({
    queryKey: ['/api/query/', query],
    queryFn: runQuery,
    // Invalidate react-query's cache just shy of the configured cache timeout.
    cacheTime: cache.timeout * 1000 * 0.95,
    // Don't refetch when window refocuses.
    refetchOnWindowFocus: false,
    // Don't automatically refetch query data (queries should be on-off).
    refetchInterval: false,
    // Don't refetch on component remount.
    refetchOnMount: false,
    ...options,
  });
}
