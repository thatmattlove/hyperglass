import { useQuery } from 'react-query';
import { useConfig } from '~/context';
import { fetchWithTimeout } from '~/util';

import type { DnsOverHttps } from '~/types';
import type { TUseDNSQueryFn } from './types';

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

export function useDNSQuery(target: string | null, family: 4 | 6) {
  const { cache, web } = useConfig();
  return useQuery([web.dns_provider.url, { target, family }], dnsQuery, {
    cacheTime: cache.timeout * 1000,
  });
}
