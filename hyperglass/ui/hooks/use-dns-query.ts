import { useQuery } from '@tanstack/react-query';
import { useConfig } from '~/context';
import { fetchWithTimeout } from '~/util';

import type {
  QueryFunction,
  QueryFunctionContext,
  QueryObserverResult,
} from '@tanstack/react-query';
import type { DnsOverHttps } from '~/types';

type DNSQueryKey = [string, { target: string | null; family: 4 | 6 }];

/**
 * Perform a DNS over HTTPS query using the application/dns-json MIME type.
 */
const query: QueryFunction<DnsOverHttps.Response, DNSQueryKey> = async (
  ctx: QueryFunctionContext<DNSQueryKey>,
) => {
  const [url, { target, family }] = ctx.queryKey;

  const controller = new AbortController();

  let json = undefined;
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
};

/**
 * Query the configured DNS over HTTPS provider for the provided target. If `family` is `4`, only
 * an A record will be queried. If `family` is `6`, only a AAAA record will be queried.
 */
export function useDNSQuery(
  /** Hostname for DNS query. */
  target: string | null,
  /** Address family, e.g. IPv4 or IPv6. */
  family: 4 | 6,
): QueryObserverResult<DnsOverHttps.Response> {
  const { cache, web } = useConfig();

  return useQuery<DnsOverHttps.Response, unknown, DnsOverHttps.Response, DNSQueryKey>({
    queryKey: [web.dnsProvider.url, { target, family }],
    queryFn: query,
    cacheTime: cache.timeout * 1000,
  });
}
