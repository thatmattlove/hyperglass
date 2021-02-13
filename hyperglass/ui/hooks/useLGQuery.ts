import { useEffect } from 'react';
import { useQuery } from 'react-query';
import { useConfig } from '~/context';
import { useGoogleAnalytics } from './useGoogleAnalytics';
import { fetchWithTimeout } from '~/util';

import type { QueryObserverResult } from 'react-query';
import type { TFormQuery } from '~/types';
import type { TUseLGQueryFn } from './types';

/**
 * Custom hook handle submission of a query to the hyperglass backend.
 */
export function useLGQuery(query: TFormQuery): QueryObserverResult<TQueryResponse> {
  const { request_timeout, cache } = useConfig();
  const controller = new AbortController();

  const { trackEvent } = useGoogleAnalytics();

  trackEvent({
    category: 'Query',
    action: 'submit',
    dimension1: query.queryLocation,
    dimension2: query.queryTarget,
    dimension3: query.queryType,
    dimension4: query.queryVrf,
  });

  async function runQuery(ctx: TUseLGQueryFn): Promise<TQueryResponse> {
    const [url, data] = ctx.queryKey;
    const { queryLocation, queryTarget, queryType, queryVrf } = data;
    const res = await fetchWithTimeout(
      url,
      {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          query_location: queryLocation,
          query_target: queryTarget,
          query_type: queryType,
          query_vrf: queryVrf,
        }),
        mode: 'cors',
      },
      request_timeout * 1000,
      controller,
    );
    try {
      return await res.json();
    } catch (err) {
      throw new Error(res.statusText);
    }
  }

  // Cancel any still-running queries on unmount.
  useEffect(
    () => () => {
      controller.abort();
    },
    [],
  );

  return useQuery<TQueryResponse, Response | TQueryResponse | Error>(
    ['/api/query/', query],
    runQuery,
    {
      // Invalidate react-query's cache just shy of the configured cache timeout.
      cacheTime: cache.timeout * 1000 * 0.95,
      // Don't refetch when window refocuses.
      refetchOnWindowFocus: false,
      // Don't automatically refetch query data (queries should be on-off).
      refetchInterval: false,
      // Don't refetch on component remount.
      refetchOnMount: false,
    },
  );
}
