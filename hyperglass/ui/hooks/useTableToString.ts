import { useCallback } from 'react';
import dayjs from 'dayjs';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import utcPlugin from 'dayjs/plugin/utc';
import { useConfig } from '~/context';
import { isStructuredOutput } from '~/types';

import type { TTableToStringFormatter, TTableToStringFormatted } from './types';

dayjs.extend(relativeTimePlugin);
dayjs.extend(utcPlugin);

function formatAsPath(path: number[]): string {
  return path.join(' → ');
}

function formatCommunities(comms: string[]): string {
  const commsStr = comms.map(c => `      - ${c}`);
  return '\n' + commsStr.join('\n');
}

function formatBool(val: boolean): string {
  let fmt = '';
  if (val === true) {
    fmt = 'yes';
  } else if (val === false) {
    fmt = 'no';
  }
  return fmt;
}

function formatTime(val: number): string {
  const now = dayjs.utc();
  const then = now.subtract(val, 'second');
  const timestamp = then.toString().replace('GMT', 'UTC');
  const relative = now.to(then, true);
  return `${relative} (${timestamp})`;
}

/**
 * Get a function to convert table data to string, for use in the copy button component.
 */
export function useTableToString(
  target: string,
  data: TQueryResponse | undefined,
  ...deps: unknown[]
): () => string {
  const { web, parsed_data_fields, messages } = useConfig();

  function formatRpkiState(val: number): string {
    const rpkiStates = [
      web.text.rpki_invalid,
      web.text.rpki_valid,
      web.text.rpki_unknown,
      web.text.rpki_unverified,
    ];
    return rpkiStates[val];
  }

  const tableFormatMap = {
    age: formatTime,
    active: formatBool,
    as_path: formatAsPath,
    communities: formatCommunities,
    rpki_state: formatRpkiState,
  };

  function isFormatted(key: string): key is keyof TTableToStringFormatted {
    return key in tableFormatMap;
  }

  function getFmtFunc(accessor: keyof TRoute): TTableToStringFormatter {
    if (isFormatted(accessor)) {
      return tableFormatMap[accessor];
    } else {
      return String;
    }
  }

  function doFormat(target: string, data: TQueryResponse | undefined): string {
    let result = messages.no_output;
    try {
      if (typeof data !== 'undefined' && isStructuredOutput(data)) {
        const tableStringParts = [`Routes For: ${target}`, `Timestamp: ${data.timestamp} UTC`];
        for (const route of data.output.routes) {
          for (const field of parsed_data_fields) {
            const [header, accessor, align] = field;
            if (align !== null) {
              let value = route[accessor];
              const fmtFunc = getFmtFunc(accessor) as (v: typeof value) => string;
              value = fmtFunc(value);
              if (accessor === 'prefix') {
                tableStringParts.push(`  - ${header}: ${value}`);
              } else {
                tableStringParts.push(`    - ${header}: ${value}`);
              }
            }
          }
        }
        result = tableStringParts.join('\n');
      }
      return result;
    } catch (err) {
      console.error(err);
      return `An error occurred while parsing the output: '${err.message}'`;
    }
  }
  return useCallback(() => doFormat(target, data), deps);
}
