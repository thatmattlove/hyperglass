import { useQuery } from 'react-query';
import type { TASNDetails } from '~/types';

async function query(asn: string): Promise<TASNDetails> {
  const res = await fetch(`https://api.bgpview.io/asn/${asn}`, { mode: 'cors' });
  return await res.json();
}

export function useASNDetail(asn: string) {
  return useQuery(asn, query);
}
