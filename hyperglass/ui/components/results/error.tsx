import { Text } from '@chakra-ui/react';

import type { TFormattedError } from './types';

type TFormatError = string | JSX.Element;

function formatError(text: string, values: string[], regex: RegExp): TFormatError[] | TFormatError {
  if (!values.length) {
    return text;
  }

  const parts = text.split(regex);

  return parts.reduce((prev, current, i) => {
    if (!i) {
      return [current];
    }

    return prev.concat(
      values.includes(current) ? <strong key={i + current}>{current}</strong> : current,
    );
  }, [] as TFormatError[]);
}

export const FormattedError: React.FC<TFormattedError> = (props: TFormattedError) => {
  const { keywords, message } = props;
  const pattern = new RegExp(keywords.map(kw => `(${kw})`).join('|'), 'gi');
  const things = formatError(message, keywords, pattern);
  return (
    <Text as="span" fontWeight={keywords.length === 0 ? 'bold' : undefined}>
      {keywords.length !== 0 ? things : message}
    </Text>
  );
};
