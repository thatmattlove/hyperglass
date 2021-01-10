import { useQuery } from 'react-query';
import { useConfig } from '~/context';
import { fetchWithTimeout } from '~/util';
import { useGoogleAnalytics } from './useGoogleAnalytics';

import type { QueryObserverResult } from 'react-query';
import type { DnsOverHttps } from '~/types';
import type { TUseDNSQueryFn } from './types';

/**
 * Perform a DNS over HTTPS query using the application/dns-json MIME type.
 */
async function dnsQuery(ctx: TUseDNSQueryFn): Promise<DnsOverHttps.Response | undefined> {
  const [url, { target, family }] = ctx.queryKey;

  const controller = new AbortController();

  let json;
  const type = family === 4 ? 'A' : family === 6 ? 'AAAA' : '';

  if (url !== null) {
    const res = await fetchWithTimeout(
      `${url}?name=${target}&type=${type}`,
      {
        headers: { accept: 'application/dns-json' },
        mode: 'cors',
      },
      5000,
      controller,
    );

    json = await res.json();
  }

  return json;
}

/**
 * Query the configured DNS over HTTPS provider for the provided target. If `family` is `4`, only
 * an A record will be queried. If `family` is `6`, only a AAAA record will be queried.
 */
export function useDNSQuery(
  /**
   * Hostname for DNS query.
   */
  target: string | null,
  /**
   * Address family, e.g. IPv4 or IPv6.
   */
  family: 4 | 6,
): QueryObserverResult<DnsOverHttps.Response> {
  const { cache, web } = useConfig();
  const { trackEvent } = useGoogleAnalytics();

  if (typeof target === 'string') {
    trackEvent({ category: 'DNS', action: 'Query', label: target, dimension1: `IPv${family}` });
  }

  return useQuery([web.dns_provider.url, { target, family }], dnsQuery, {
    cacheTime: cache.timeout * 1000,
  });
}
