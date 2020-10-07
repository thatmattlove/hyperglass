import * as React from 'react';
import Countdown, { zeroPad } from 'react-countdown';
import { Text, useColorMode } from '@chakra-ui/core';

const bg = { dark: 'white', light: 'black' };

const Renderer = ({ hours, minutes, seconds, completed, props }) => {
  if (completed) {
    return <Text fontSize="xs" />;
  } else {
    let time = [zeroPad(seconds)];
    minutes !== 0 && time.unshift(zeroPad(minutes));
    hours !== 0 && time.unshift(zeroPad(hours));
    return (
      <Text fontSize="xs" color="gray.500">
        {props.text}
        <Text as="span" fontSize="xs" color={bg[props.colorMode]}>
          {time.join(':')}
        </Text>
      </Text>
    );
  }
};

export const CacheTimeout = ({ timeout, text }) => {
  const then = timeout * 1000;
  const { colorMode } = useColorMode();
  return (
    <Countdown
      date={Date.now() + then}
      renderer={Renderer}
      daysInHours
      text={text}
      colorMode={colorMode}
    />
  );
};
