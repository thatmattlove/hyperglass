import { Text, Tooltip, Badge } from '@chakra-ui/react';
import { Else, If, Then } from 'react-if';
import { useColorValue } from '~/hooks';

import type { TextProps } from '@chakra-ui/react';

interface MonoFieldProps extends TextProps {
  v: React.ReactNode;
}

interface ASNFieldProps extends TextProps {
  asn: string | null;
  org: string | null;
}

interface HostnameFieldProps extends TextProps {
  hostname: string | null;
}

interface LatencyFieldProps extends TextProps {
  rtt: number | null;
}

interface LossFieldProps extends TextProps {
  loss: number | null;
}

export const MonoField = (props: MonoFieldProps): JSX.Element => {
  const { v, ...rest } = props;
  
  // Handle empty, null, undefined values and timeout indicators
  if (v === null || v === undefined || (typeof v === 'string' && (v.trim() === '' || v === 'None'))) {
    return (
      <Text as="span" fontSize="sm" fontFamily="mono" color="gray.500" {...rest}>
        —
      </Text>
    );
  }
  
  return (
    <Text as="span" fontSize="sm" fontFamily="mono" {...rest}>
      {v}
    </Text>
  );
};

export const ASNField = (props: ASNFieldProps): JSX.Element => {
  const { asn, org, ...rest } = props;
  
  if (!asn || asn === 'None' || asn === 'null') {
    return (
      <Text as="span" fontSize="sm" color="gray.500" {...rest}>
        —
      </Text>
    );
  }
  
  // Display ASN as-is (no prefix added since backend now sends clean format)
  const asnDisplay = asn; // Just use the value directly: "12345" or "IXP"
  const tooltipLabel = org && org !== 'None' ? `${asnDisplay} - ${org}` : asnDisplay;
  
  return (
    <Tooltip hasArrow label={tooltipLabel} placement="top">
      <Text 
        as="span" 
        fontSize="sm" 
        fontFamily="mono" 
        cursor="help"
        {...rest}
      >
        {asnDisplay}
      </Text>
    </Tooltip>
  );
};

export const HostnameField = (props: HostnameFieldProps): JSX.Element => {
  const { hostname, ...rest } = props;
  
  if (!hostname || hostname === 'None' || hostname === 'null') {
    return (
      <Text as="span" fontSize="sm" color="gray.500" {...rest}>
        —
      </Text>
    );
  }
  
  return (
    <Tooltip hasArrow label={hostname} placement="top">
      <Text 
        as="span" 
        fontSize="sm" 
        fontFamily="mono"
        noOfLines={1} 
        maxW="350px"
        {...rest}
      >
        {hostname}
      </Text>
    </Tooltip>
  );
};

export const LatencyField = (props: LatencyFieldProps): JSX.Element => {
  const { rtt, ...rest } = props;
  
  if (rtt === null || rtt === undefined) {
    return (
      <Text as="span" fontSize="sm" color="gray.500" {...rest}>
        *
      </Text>
    );
  }
  
  // Color-code latency: green < 50ms, yellow < 200ms, red >= 200ms
  const getLatencyColor = (latency: number) => {
    if (latency < 50) return 'green.500';
    if (latency < 200) return 'yellow.500';
    return 'red.500';
  };
  
  return (
    <Text 
      as="span" 
      fontSize="sm" 
      fontFamily="mono"
      color={getLatencyColor(rtt)}
      {...rest}
    >
      {rtt.toFixed(1)}ms
    </Text>
  );
};

export const LossField = (props: LossFieldProps): JSX.Element => {
  const { loss, ...rest } = props;
  
  if (loss === null || loss === undefined) {
    return (
      <Text as="span" fontSize="sm" color="gray.500" {...rest}>
        —
      </Text>
    );
  }
  
  // Color-code loss: green = 0%, yellow < 50%, red >= 50%
  const getLossColor = (lossPercent: number) => {
    if (lossPercent === 0) return 'green.500';
    if (lossPercent < 50) return 'yellow.500';
    return 'red.500';
  };
  
  const bgColor = useColorValue(
    loss === 0 ? 'green.50' : loss < 50 ? 'yellow.50' : 'red.50',
    loss === 0 ? 'green.900' : loss < 50 ? 'yellow.900' : 'red.900'
  );
  
  return (
    <Badge
      fontSize="sm"
      fontFamily="mono"
      variant="solid"
      colorScheme={loss === 0 ? 'green' : loss < 50 ? 'yellow' : 'red'}
      {...rest}
    >
      {loss}%
    </Badge>
  );
};