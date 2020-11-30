import dynamic from 'next/dynamic';
import {
  Icon,
  Text,
  Popover,
  Tooltip,
  PopoverArrow,
  PopoverContent,
  PopoverTrigger,
} from '@chakra-ui/react';
import { MdLastPage } from '@meronex/icons/md';
import dayjs from 'dayjs';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import utcPlugin from 'dayjs/plugin/utc';
import { useConfig, useColorValue } from '~/context';
import { If } from '~/components';

import type {
  TAge,
  TActive,
  TWeight,
  TASPath,
  TMonoField,
  TRPKIState,
  TCommunities,
} from './types';

dayjs.extend(relativeTimePlugin);
dayjs.extend(utcPlugin);

const Check = dynamic<MeronexIcon>(() => import('@meronex/icons/fa').then(i => i.FaCheckCircle));
const More = dynamic<MeronexIcon>(() => import('@meronex/icons/cg').then(i => i.CgMoreO));
const NotAllowed = dynamic<MeronexIcon>(() =>
  import('@meronex/icons/md').then(i => i.MdNotInterested),
);
const Question = dynamic<MeronexIcon>(() =>
  import('@meronex/icons/bs').then(i => i.BsQuestionCircleFill),
);
const Warning = dynamic<MeronexIcon>(() => import('@meronex/icons/bi').then(i => i.BisError));
const ChevronRight = dynamic<MeronexIcon>(() =>
  import('@meronex/icons/fa').then(i => i.FaChevronRight),
);

export const MonoField = (props: TMonoField) => {
  const { v, ...rest } = props;
  return (
    <Text as="span" fontSize="sm" fontFamily="mono" {...rest}>
      {v}
    </Text>
  );
};

export const Active = (props: TActive) => {
  const { isActive } = props;
  const color = useColorValue(['gray.500', 'green.500'], ['whiteAlpha.300', 'blackAlpha.500']);
  return (
    <>
      <If c={isActive}>
        <Icon color={color[+isActive]} as={Check} />
      </If>
      <If c={!isActive}>
        <Icon color={color[+isActive]} as={NotAllowed} />
      </If>
    </>
  );
};

export const Age = (props: TAge) => {
  const { inSeconds, ...rest } = props;
  const now = dayjs.utc();
  const then = now.subtract(inSeconds, 'second');
  return (
    <Tooltip hasArrow label={then.toString().replace('GMT', 'UTC')} placement="right">
      <Text fontSize="sm" {...rest}>
        {now.to(then, true)}
      </Text>
    </Tooltip>
  );
};

export const Weight = (props: TWeight) => {
  const { weight, winningWeight, ...rest } = props;
  const fixMeText =
    winningWeight === 'low' ? 'Lower Weight is Preferred' : 'Higher Weight is Preferred';
  return (
    <Tooltip hasArrow label={fixMeText} placement="right">
      <Text fontSize="sm" fontFamily="mono" {...rest}>
        {weight}
      </Text>
    </Tooltip>
  );
};

export const ASPath = (props: TASPath) => {
  const { path, active } = props;
  const color = useColorValue(
    ['blackAlpha.500', 'blackAlpha.500'],
    ['blackAlpha.500', 'whiteAlpha.300'],
  );

  if (path.length === 0) {
    return <Icon as={MdLastPage} />;
  }

  let paths = [] as JSX.Element[];

  path.map((asn, i) => {
    const asnStr = String(asn);
    i !== 0 && paths.push(<Icon as={ChevronRight} key={`separator-${i}`} color={color[+active]} />);
    paths.push(
      <Text fontSize="sm" as="span" whiteSpace="pre" fontFamily="mono" key={`as-${asnStr}-${i}`}>
        {asnStr}
      </Text>,
    );
  });

  return <>{paths}</>;
};

export const Communities = (props: TCommunities) => {
  const { communities } = props;
  const color = useColorValue('black', 'white');
  return (
    <>
      <If c={communities.length === 0}>
        <Tooltip placement="right" hasArrow label="No Communities">
          <Icon as={Question} />
        </Tooltip>
      </If>
      <If c={communities.length !== 0}>
        <Popover trigger="hover" placement="right">
          <PopoverTrigger>
            <Icon as={More} />
          </PopoverTrigger>
          <PopoverContent
            p={4}
            width="unset"
            color={color}
            textAlign="left"
            fontFamily="mono"
            fontWeight="normal"
            whiteSpace="pre-wrap">
            <PopoverArrow />
            {communities.join('\n')}
          </PopoverContent>
        </Popover>
      </If>
    </>
  );
};

export const RPKIState = (props: TRPKIState) => {
  const { state, active } = props;
  const { web } = useConfig();
  const color = useColorValue(
    [
      ['red.400', 'green.500', 'yellow.400', 'gray.500'],
      ['red.500', 'green.500', 'yellow.500', 'gray.600'],
    ],
    [
      ['red.300', 'green.300', 'yellow.300', 'gray.300'],
      ['red.500', 'green.600', 'yellow.500', 'gray.800'],
    ],
  );
  const icon = [NotAllowed, Check, Warning, Question];

  const text = [
    web.text.rpki_invalid,
    web.text.rpki_valid,
    web.text.rpki_unknown,
    web.text.rpki_unverified,
  ];

  return (
    <Tooltip hasArrow placement="right" label={text[state] ?? text[3]}>
      <Icon icon={icon[state]} color={color[+active][state]} />
    </Tooltip>
  );
};
