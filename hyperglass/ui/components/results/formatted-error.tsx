import { chakra } from '@chakra-ui/react';

interface FormattedErrorProps {
  keywords: string[];
  message: string;
}

type FormatError = string | JSX.Element;

function formatError(text: string, values: string[], regex: RegExp): FormatError[] | FormatError {
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
  }, [] as FormatError[]);
}

export const FormattedError = (props: FormattedErrorProps): JSX.Element => {
  const { keywords, message } = props;
  const pattern = new RegExp(keywords.map(kw => `(${kw})`).join('|'), 'gi');
  const things = formatError(message, keywords, pattern);
  return (
    <chakra.span fontWeight={keywords.length === 0 ? 'bold' : undefined}>
      {keywords.length !== 0 ? things : message}
    </chakra.span>
  );
};
