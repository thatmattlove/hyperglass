import { Text } from '@chakra-ui/react';
import strReplace from 'react-string-replace';

import type { TFormattedError } from './types';

export const FormattedError = (props: TFormattedError) => {
  const { keywords, message } = props;
  const patternStr = keywords.map(kw => `(${kw})`).join('|');
  const pattern = new RegExp(patternStr, 'gi');
  let errorFmt;
  try {
    errorFmt = strReplace(message, pattern, match => (
      <Text key={match} as="strong">
        {match}
      </Text>
    ));
  } catch (err) {
    errorFmt = <Text as="span">{message}</Text>;
  }
  return <Text as="span">{keywords.length !== 0 ? errorFmt : message}</Text>;
};
