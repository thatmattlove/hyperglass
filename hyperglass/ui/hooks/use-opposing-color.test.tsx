import { expect, describe, it } from 'vitest';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import { userEvent } from '@testing-library/user-event';
import { ChakraProvider, useColorMode, useColorModeValue, extendTheme } from '@chakra-ui/react';
import { useOpposingColor } from './use-opposing-color';

const TestComponent = (): JSX.Element => {
  const { toggleColorMode } = useColorMode();
  const bg1 = useColorModeValue('#ffffff', '#000000');
  const bg2 = useColorModeValue('blue.50', 'blue.900');
  const fg1 = useOpposingColor(bg1);
  const fg2 = useOpposingColor(bg2);

  return (
    <div>
      <span id="test1" style={{ color: fg1 }} />
      <span id="test2" style={{ color: fg2 }} />
      <button type="button" onClick={toggleColorMode}>
        Toggle Color Mode
      </button>
    </div>
  );
};

describe('useOpposingColor Hook', () => {
  it('should change foreground color', async () => {
    const { getByRole, container } = render(
      <ChakraProvider theme={extendTheme({ initialColorMode: 'light', useSystemColorMode: false })}>
        <TestComponent />
      </ChakraProvider>,
    );
    const test1 = container.querySelector('#test1');
    const test2 = container.querySelector('#test2');

    expect(test1).toHaveStyle('color: rgb(0, 0, 0);');
    expect(test2).toHaveStyle('color: rgb(0, 0, 0);');

    await userEvent.click(getByRole('button'));

    expect(test1).toHaveStyle('color: rgb(255, 255, 255);');
    expect(test2).toHaveStyle('color: rgb(255, 255, 255);');

    await userEvent.click(getByRole('button'));

    expect(test1).toHaveStyle('color: rgb(0, 0, 0);');
    expect(test2).toHaveStyle('color: rgb(0, 0, 0);');
  });
});
