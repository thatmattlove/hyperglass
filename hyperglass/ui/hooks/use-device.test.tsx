import { expect, describe, it } from 'vitest';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useDevice } from './use-device';
import { HyperglassContext } from '~/context';

import type { DeviceGroup, Config } from '~/types';

interface TestComponentProps {
  deviceId: string;
}

const DEVICES = [
  {
    group: 'Test Group',
    locations: [{ id: 'test1', name: 'Test 1' }],
  },
] as DeviceGroup[];

const TestComponent = (props: TestComponentProps): JSX.Element => {
  const { deviceId } = props;
  const getDevice = useDevice();
  const device = getDevice(deviceId);

  return <div>{device?.name}</div>;
};

describe('useDevice Hook', () => {
  it('should get the device by ID', () => {
    const { queryByText } = render(
      <HyperglassContext.Provider value={{ devices: DEVICES } as unknown as Config}>
        <TestComponent deviceId="test1" />
      </HyperglassContext.Provider>,
    );
    expect(queryByText('Test 1')).toBeInTheDocument();
  });
});
