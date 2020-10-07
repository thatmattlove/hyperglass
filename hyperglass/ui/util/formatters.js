import dayjs from 'dayjs';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import utcPlugin from 'dayjs/plugin/utc';

dayjs.extend(relativeTimePlugin);
dayjs.extend(utcPlugin);

const formatAsPath = path => {
  return path.join(' → ');
};

const formatCommunities = comms => {
  const commsStr = comms.map(c => `      - ${c}`);
  return '\n' + commsStr.join('\n');
};

const formatBool = val => {
  let fmt = '';
  if (val === true) {
    fmt = 'yes';
  } else if (val === false) {
    fmt = 'no';
  }
  return fmt;
};

const formatTime = val => {
  const now = dayjs.utc();
  const then = now.subtract(val, 'seconds');
  const timestamp = then.toString().replace('GMT', 'UTC');
  const relative = now.to(then, true);
  return `${relative} (${timestamp})`;
};

export const tableToString = (target, data, config) => {
  try {
    const formatRpkiState = val => {
      const rpkiStateNames = [
        config.web.text.rpki_invalid,
        config.web.text.rpki_valid,
        config.web.text.rpki_unknown,
        config.web.text.rpki_unverified,
      ];
      return rpkiStateNames[val];
    };

    const tableFormatMap = {
      age: formatTime,
      active: formatBool,
      as_path: formatAsPath,
      communities: formatCommunities,
      rpki_state: formatRpkiState,
    };

    let tableStringParts = [`Routes For: ${target}`, `Timestamp: ${data.timestamp} UTC`];

    data.output.routes.map(route => {
      config.parsed_data_fields.map(field => {
        const [header, accessor, align] = field;
        if (align !== null) {
          let value = route[accessor];
          const fmtFunc = tableFormatMap[accessor] ?? String;
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
};
