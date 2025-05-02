import { Badge, Tooltip, useStyleConfig } from '@chakra-ui/react';
import React, { memo } from 'react';
import isEqual from 'react-fast-compare';
import replace from 'react-string-replace';

import type { TooltipProps } from '@chakra-ui/react';
import type { Highlight as HighlightConfig } from '~/types';

interface HighlightedProps {
  patterns: HighlightConfig[];
  children: string;
}

interface HighlightProps {
  label: string | null;
  colorScheme: string;
  children: React.ReactNode;
}

const Highlight = (props: HighlightProps): JSX.Element => {
  const { colorScheme, label, children } = props;
  const { bg, color } = useStyleConfig('Button', { colorScheme }) as TooltipProps;
  return (
    <Tooltip label={label} bg={bg} color={color} hasArrow>
      <Badge colorScheme={colorScheme}>{children}</Badge>
    </Tooltip>
  );
};

const _Highlighted = (props: HighlightedProps): JSX.Element => {
  const { patterns, children } = props;
  let result: React.ReactNode[] = [];
  let times: number = 0;

  if (patterns.length === 0) {
    result = [children];
  } else {
    for (const config of patterns) {
      let toReplace: string | React.ReactNode[] = children;
      if (times !== 0) {
        toReplace = result;
      }
      result = replace(toReplace, new RegExp(`(${config.pattern})`, 'gm'), (m, i) => (
        <Highlight key={`${m + i}`} label={config.label} colorScheme={config.color}>
          {m}
        </Highlight>
      ));
      times++;
    }
  }

  return <>{result}</>;
};

export const Highlighted = memo(_Highlighted, isEqual);
