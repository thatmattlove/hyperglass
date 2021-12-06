import { forwardRef } from 'react';
import { Text, Box, Tooltip, Menu, MenuButton, MenuList, Link } from '@chakra-ui/react';
import dayjs from 'dayjs';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import utcPlugin from 'dayjs/plugin/utc';
import { If, DynamicIcon } from '~/components';
import { useConfig, useColorValue } from '~/context';
import { useOpposingColor } from '~/hooks';

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

export const MonoField: React.FC<TMonoField> = (props: TMonoField) => {
  const { v, ...rest } = props;
  return (
    <Text as="span" fontSize="sm" fontFamily="mono" {...rest}>
      {v}
    </Text>
  );
};

export const Active: React.FC<TActive> = (props: TActive) => {
  const { isActive } = props;
  const color = useColorValue(['gray.500', 'green.500'], ['whiteAlpha.300', 'blackAlpha.500']);
  return (
    <>
      <If c={isActive}>
        <DynamicIcon color={color[+isActive]} icon={{ fa: 'FaCheckCircle' }} />
      </If>
      <If c={!isActive}>
        <DynamicIcon color={color[+isActive]} icon={{ md: 'MdCancel' }} />
      </If>
    </>
  );
};

export const Age: React.FC<TAge> = (props: TAge) => {
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

export const Weight: React.FC<TWeight> = (props: TWeight) => {
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

export const ASPath: React.FC<TASPath> = (props: TASPath) => {
  const { path, active } = props;
  const color = useColorValue(
    // light: inactive, active
    ['blackAlpha.500', 'blackAlpha.500'],
    // dark: inactive, active
    ['whiteAlpha.600', 'blackAlpha.700'],
  );

  if (path.length === 0) {
    return <DynamicIcon icon={{ ri: 'RiHome2Fill' }} />;
  }

  const paths = [] as JSX.Element[];

  path.map((asn, i) => {
    const asnStr = String(asn);
    i !== 0 &&
      paths.push(
        <DynamicIcon
          icon={{ fa: 'FaChevronRight' }}
          key={`separator-${i}`}
          color={color[+active]}
          boxSize={5}
          px={2}
        />,
      );
    paths.push(
      <Text fontSize="sm" as="span" whiteSpace="pre" fontFamily="mono" key={`as-${asnStr}-${i}`}>
        {asnStr}
      </Text>,
    );
  });

  return <>{paths}</>;
};

export const Communities: React.FC<TCommunities> = (props: TCommunities) => {
  const { communities } = props;
  const { web } = useConfig();
  const bg = useColorValue('white', 'gray.900');
  const color = useOpposingColor(bg);
  return (
    <>
      <If c={communities.length === 0}>
        <Tooltip placement="right" hasArrow label={web.text.noCommunities}>
          <Link>
            <DynamicIcon icon={{ bs: 'BsQuestionCircleFill' }} />
          </Link>
        </Tooltip>
      </If>
      <If c={communities.length !== 0}>
        <Menu preventOverflow>
          <MenuButton>
            <DynamicIcon icon={{ cg: 'CgMoreO' }} />
          </MenuButton>
          <MenuList
            p={3}
            bg={bg}
            minW={32}
            width="unset"
            color={color}
            boxShadow="2xl"
            textAlign="left"
            fontFamily="mono"
            fontWeight="normal"
            whiteSpace="pre-wrap"
          >
            {communities.join('\n')}
          </MenuList>
        </Menu>
      </If>
    </>
  );
};

const _RPKIState: React.ForwardRefRenderFunction<HTMLDivElement, TRPKIState> = (
  props: TRPKIState,
  ref,
) => {
  const { state, active } = props;
  const { web } = useConfig();
  const bg = useColorValue(
    [
      ['red.400', 'green.500', 'yellow.400', 'gray.500'],
      ['red.500', 'green.500', 'yellow.600', 'gray.600'],
    ],
    [
      ['red.300', 'green.300', 'yellow.300', 'gray.300'],
      ['red.500', 'green.600', 'yellow.600', 'gray.800'],
    ],
  );
  const color = useOpposingColor(bg[+active][state]);

  const icon = [
    { md: 'MdCancel' },
    { fa: 'FaCheckCircle' },
    { bi: 'BisError' },
    { bs: 'BsQuestionCircleFill' },
  ] as Record<string, string>[];

  const text = [
    web.text.rpkiInvalid,
    web.text.rpkiValid,
    web.text.rpkiUnknown,
    web.text.rpkiUnverified,
  ];

  return (
    <Tooltip
      hasArrow
      placement="right"
      label={text[state] ?? text[3]}
      bg={bg[+active][state]}
      color={color}
    >
      <Box ref={ref} boxSize={5}>
        <DynamicIcon icon={icon[state]} color={bg[+active][state]} />
      </Box>
    </Tooltip>
  );
};

export const RPKIState = forwardRef<HTMLDivElement, TRPKIState>(_RPKIState);
