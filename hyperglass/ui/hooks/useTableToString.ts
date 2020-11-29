import { useCallback } from 'react';
import dayjs from 'dayjs';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import utcPlugin from 'dayjs/plugin/utc';
import { useConfig } from '~/context';

import { TStringTableData } from './types';

dayjs.extend(relativeTimePlugin);
dayjs.extend(utcPlugin);

type TFormatter = (v: any) => string;

type TFormatted = {
  age: (v: number) => string;
  active: (v: boolean) => string;
  as_path: (v: number[]) => string;
  communities: (v: string[]) => string;
  rpki_state: (v: number, n: TRPKIStates) => string;
};

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

export function useTableToString(
  target: string,
  data: TStringTableData,
  ...deps: any
): () => string {
  const { web, parsed_data_fields } = useConfig();

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

  function isFormatted(key: string): key is keyof TFormatted {
    return key in tableFormatMap;
  }

  function getFmtFunc(accessor: keyof TRoute): TFormatter {
    if (isFormatted(accessor)) {
      return tableFormatMap[accessor];
    } else {
      return String;
    }
  }

  function doFormat(target: string, data: TStringTableData): string {
    try {
      let tableStringParts = [`Routes For: ${target}`, `Timestamp: ${data.timestamp} UTC`];

      data.output.routes.map(route => {
        parsed_data_fields.map(field => {
          const [header, accessor, align] = field;
          if (align !== null) {
            let value = route[accessor];
            const fmtFunc = getFmtFunc(accessor);
            value = fmtFunc(value);
            if (accessor === 'prefix') {
              tableStringParts.push(`  - ${header}: ${value}`);
            } else {
              tableStringParts.push(`    - ${header}: ${value}`);
            }
          }
        });
      });
      return tableStringParts.join('\n');
    } catch (err) {
      console.error(err);
      return `An error occurred while parsing the output: '${err.message}'`;
    }
  }
  return useCallback(() => doFormat(target, data), deps);
}
