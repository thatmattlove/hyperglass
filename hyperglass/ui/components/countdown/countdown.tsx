import { Text } from '@chakra-ui/react';
import ReactCountdown, { zeroPad } from 'react-countdown';
import { If } from '~/components';
import { useColorValue } from '~/context';

import type { TCountdown, TRenderer } from './types';

const Renderer: React.FC<TRenderer> = (props: TRenderer) => {
  const { hours, minutes, seconds, completed, text } = props;
  const time = [zeroPad(seconds)];
  minutes !== 0 && time.unshift(zeroPad(minutes));
  hours !== 0 && time.unshift(zeroPad(hours));
  const bg = useColorValue('black', 'white');
  return (
    <>
      <If c={completed}>
        <Text fontSize="xs" />
      </If>
      <If c={!completed}>
        <Text fontSize="xs" color="gray.500">
          {text}
          <Text as="span" fontSize="xs" color={bg}>
            {time.join(':')}
          </Text>
        </Text>
      </If>
    </>
  );
};

export const Countdown: React.FC<TCountdown> = (props: TCountdown) => {
  const { timeout, text } = props;
  const then = timeout * 1000;
  return (
    <ReactCountdown
      date={Date.now() + then}
      daysInHours
      renderer={renderProps => <Renderer {...renderProps} text={text} />}
    />
  );
};
