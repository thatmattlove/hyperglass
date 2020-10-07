import * as React from 'react';
import {
  Flex,
  Icon,
  Popover,
  PopoverArrow,
  PopoverContent,
  PopoverTrigger,
  Text,
  Tooltip,
  useColorMode,
} from '@chakra-ui/core';
import { MdLastPage } from '@meronex/icons/md';
import dayjs from 'dayjs';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import utcPlugin from 'dayjs/plugin/utc';
import { useConfig } from 'app/context';
import { Table } from 'app/components';

dayjs.extend(relativeTimePlugin);
dayjs.extend(utcPlugin);

const isActiveColor = {
  true: { dark: 'green.300', light: 'green.500' },
  false: { dark: 'gray.300', light: 'gray.500' },
};

const arrowColor = {
  true: { dark: 'blackAlpha.500', light: 'blackAlpha.500' },
  false: { dark: 'whiteAlpha.300', light: 'blackAlpha.500' },
};

const rpkiIcon = ['not-allowed', 'check-circle', 'warning', 'question'];

const rpkiColor = {
  true: {
    dark: ['red.500', 'green.600', 'yellow.500', 'gray.800'],
    light: ['red.500', 'green.500', 'yellow.500', 'gray.600'],
  },
  false: {
    dark: ['red.300', 'green.300', 'yellow.300', 'gray.300'],
    light: ['red.400', 'green.500', 'yellow.400', 'gray.500'],
  },
};

const makeColumns = fields => {
  return fields.map(pair => {
    const [header, accessor, align] = pair;
    let columnConfig = {
      Header: header,
      accessor: accessor,
      align: align,
      hidden: false,
    };
    if (align === null) {
      columnConfig.hidden = true;
    }
    return columnConfig;
  });
};

const MonoField = ({ v, ...props }) => (
  <Text fontSize="sm" fontFamily="mono" {...props}>
    {v}
  </Text>
);

const Active = ({ isActive }) => {
  const { colorMode } = useColorMode();
  return (
    <Icon name={isActive ? 'check-circle' : 'warning'} color={isActiveColor[isActive][colorMode]} />
  );
};

const Age = ({ inSeconds }) => {
  const now = dayjs.utc();
  const then = now.subtract(inSeconds, 'seconds');
  return (
    <Tooltip hasArrow label={then.toString().replace('GMT', 'UTC')} placement="right">
      <Text fontSize="sm">{now.to(then, true)}</Text>
    </Tooltip>
  );
};

const Weight = ({ weight, winningWeight }) => {
  const fixMeText =
    winningWeight === 'low' ? 'Lower Weight is Preferred' : 'Higher Weight is Preferred';
  return (
    <Tooltip hasArrow label={fixMeText} placement="right">
      <Text fontSize="sm" fontFamily="mono">
        {weight}
      </Text>
    </Tooltip>
  );
};

const ASPath = ({ path, active }) => {
  const { colorMode } = useColorMode();
  if (path.length === 0) {
    return <Icon as={MdLastPage} />;
  }
  let paths = [];
  path.map((asn, i) => {
    const asnStr = String(asn);
    i !== 0 &&
      paths.push(
        <Icon name="chevron-right" key={`separator-${i}`} color={arrowColor[active][colorMode]} />,
      );
    paths.push(
      <Text fontSize="sm" as="span" whiteSpace="pre" fontFamily="mono" key={`as-${asnStr}-${i}`}>
        {asnStr}
      </Text>,
    );
  });
  return paths;
};

const Communities = ({ communities }) => {
  const { colorMode } = useColorMode();
  let component;
  communities.length === 0
    ? (component = (
        <Tooltip placement="right" hasArrow label="No Communities">
          <Icon name="question-outline" />
        </Tooltip>
      ))
    : (component = (
        <Popover trigger="hover" placement="right">
          <PopoverTrigger>
            <Icon name="view" />
          </PopoverTrigger>
          <PopoverContent
            textAlign="left"
            p={4}
            width="unset"
            color={colorMode === 'dark' ? 'white' : 'black'}
            fontFamily="mono"
            fontWeight="normal"
            whiteSpace="pre-wrap">
            <PopoverArrow />
            {communities.join('\n')}
          </PopoverContent>
        </Popover>
      ));
  return component;
};

const RPKIState = ({ state, active }) => {
  const { web } = useConfig();
  const { colorMode } = useColorMode();
  const stateText = [
    web.text.rpki_invalid,
    web.text.rpki_valid,
    web.text.rpki_unknown,
    web.text.rpki_unverified,
  ];
  return (
    <Tooltip hasArrow placement="right" label={stateText[state] ?? stateText[3]}>
      <Icon name={rpkiIcon[state]} color={rpkiColor[active][colorMode][state]} />
    </Tooltip>
  );
};

const Cell = ({ data, rawData, longestASN }) => {
  const component = {
    prefix: <MonoField v={data.value} />,
    active: <Active isActive={data.value} />,
    age: <Age inSeconds={data.value} />,
    weight: <Weight weight={data.value} winningWeight={rawData.winning_weight} />,
    med: <MonoField v={data.value} />,
    local_preference: <MonoField v={data.value} />,
    as_path: <ASPath path={data.value} active={data.row.values.active} longestASN={longestASN} />,
    communities: <Communities communities={data.value} />,
    next_hop: <MonoField v={data.value} />,
    source_as: <MonoField v={data.value} />,
    source_rid: <MonoField v={data.value} />,
    peer_rid: <MonoField v={data.value} />,
    rpki_state: <RPKIState state={data.value} active={data.row.values.active} />,
  };
  return component[data.column.id] ?? <> </>;
};

export const BGPTable = ({ children: data, ...props }) => {
  const config = useConfig();
  const columns = makeColumns(config.parsed_data_fields);

  return (
    <Flex my={8} maxW={['100%', '100%', '100%', '100%']} w="100%" {...props}>
      <Table
        columns={columns}
        data={data.routes}
        rowHighlightProp="active"
        cellRender={d => <Cell data={d} rawData={data} />}
        bordersHorizontal
        rowHighlightBg="green"
      />
    </Flex>
  );
};
