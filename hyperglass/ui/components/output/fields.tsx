import { Box, Flex, Link, Menu, MenuButton, MenuList, Text, Tooltip } from '@chakra-ui/react';
import dayjs from 'dayjs';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import utcPlugin from 'dayjs/plugin/utc';
import { forwardRef } from 'react';
import { Else, If, Then } from 'react-if';
import { useConfig } from '~/context';
import { DynamicIcon } from '~/elements';
import { useColorValue, useOpposingColor } from '~/hooks';

import type { TextProps } from '@chakra-ui/react';

interface ActiveProps {
  isActive: boolean;
}

interface MonoFieldProps extends TextProps {
  v: React.ReactNode;
}

interface AgeProps extends TextProps {
  inSeconds: number;
}

interface WeightProps extends TextProps {
  weight: number;
  winningWeight: 'low' | 'high';
}

interface ASPathProps {
  path: number[];
  active: boolean;
}

interface CommunitiesProps {
  communities: string[];
}

interface RPKIStateProps {
  state:
    | 0 // Invalid
    | 1 // Valid
    | 2 // Unknown
    | 3; // Unverified
  active: boolean;
}

dayjs.extend(relativeTimePlugin);
dayjs.extend(utcPlugin);

export const MonoField = (props: MonoFieldProps): JSX.Element => {
  const { v, ...rest } = props;
  return (
    <Text as="span" fontSize="sm" fontFamily="mono" {...rest}>
      {v}
    </Text>
  );
};

export const Active = (props: ActiveProps): JSX.Element => {
  const { isActive } = props;
  const color = useColorValue(['gray.500', 'green.500'], ['whiteAlpha.300', 'blackAlpha.500']);
  return (
    <If condition={isActive}>
      <Then>
        <DynamicIcon color={color[+isActive]} icon={{ fa: 'FaCheckCircle' }} />
      </Then>
      <Else>
        <DynamicIcon color={color[+isActive]} icon={{ md: 'MdCancel' }} />
      </Else>
    </If>
  );
};

export const Age = (props: AgeProps): JSX.Element => {
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

export const Weight = (props: WeightProps): JSX.Element => {
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

export const ASPath = (props: ASPathProps): JSX.Element => {
  const { path, active } = props;
  const color = useColorValue(
    // light: inactive, active
    ['blackAlpha.500', 'blackAlpha.500'],
    // dark: inactive, active
    ['whiteAlpha.600', 'blackAlpha.700'],
  );

  if (path.length === 0) {
    return (
      <Tooltip hasArrow label="Internal" placement="right">
        <Link>
          <DynamicIcon icon={{ ri: 'RiHome2Fill' }} />
        </Link>
      </Tooltip>
    );
  }

  const paths = [] as JSX.Element[];

  path.map((asn, i) => {
    const asnStr = String(asn);
    i !== 0 &&
      paths.push(
        <DynamicIcon
          icon={{ fa: 'FaChevronRight' }}
          // biome-ignore lint/suspicious/noArrayIndexKey: index makes sense in this case.
          key={`separator-${i}`}
          color={color[+active]}
          boxSize={5}
          px={2}
          display="inline-flex"
        />,
      );
    paths.push(
      // biome-ignore lint/suspicious/noArrayIndexKey: index makes sense in this case.
      <Text fontSize="sm" as="span" whiteSpace="pre" fontFamily="mono" key={`as-${asnStr}-${i}`}>
        {asnStr}
      </Text>,
    );
  });

  return <Flex>{paths}</Flex>;
};

export const Communities = (props: CommunitiesProps): JSX.Element => {
  const { communities } = props;
  const { web } = useConfig();
  const bg = useColorValue('white', 'gray.900');
  const color = useOpposingColor(bg);
  return (
    <If condition={communities.length === 0}>
      <Then>
        <Tooltip placement="right" hasArrow label={web.text.noCommunities}>
          <Link>
            <DynamicIcon icon={{ bs: 'BsQuestionCircleFill' }} />
          </Link>
        </Tooltip>
      </Then>
      <Else>
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
      </Else>
    </If>
  );
};

const _RPKIState: React.ForwardRefRenderFunction<HTMLDivElement, RPKIStateProps> = (
  props: RPKIStateProps,
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
    { bi: 'BiError' },
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

export const RPKIState = forwardRef<HTMLDivElement, RPKIStateProps>(_RPKIState);
