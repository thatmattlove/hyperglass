import { expect, describe, it } from 'vitest';
import '@testing-library/jest-dom';
import { render } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { useGreeting } from './use-greeting';

const TRUE = JSON.stringify(true);
const FALSE = JSON.stringify(false);

const TestComponent = (): JSX.Element => {
  const { ack, open, close, isAck, isOpen, greetingReady } = useGreeting();
  return (
    <div>
      <table>
        <tbody>
          <tr>
            <td id="isAck">{JSON.stringify(isAck)}</td>
            <td id="isOpen">{JSON.stringify(isOpen)}</td>
            <td id="greetingReady">{JSON.stringify(greetingReady)}</td>
          </tr>
        </tbody>
      </table>
      <button id="open" type="button" onClick={open}>
        Open
      </button>
      <button id="close" type="button" onClick={close}>
        Close
      </button>
      <button id="ack-false-required" type="button" onClick={() => ack(false, true)}>
        Don't acknowledge, is required
      </button>
      <button id="ack-true-required" type="button" onClick={() => ack(true, true)}>
        Acknowledge, is required
      </button>
      <button id="ack-false-not-required" type="button" onClick={() => ack(false, false)}>
        Don't Acknowledge, not required
      </button>
      <button id="ack-true-not-required" type="button" onClick={() => ack(true, false)}>
        Acknowledge, not required
      </button>
    </div>
  );
};

describe('useGreeting Hook', () => {
  it('should open and close when toggled', async () => {
    const { container } = render(<TestComponent />);
    const open = container.querySelector('#open');
    const close = container.querySelector('#close');
    const isOpen = container.querySelector('#isOpen');

    if (open !== null && close !== null && isOpen !== null) {
      expect(isOpen).toHaveTextContent(FALSE);
      await userEvent.click(open);
      expect(isOpen).toHaveTextContent(TRUE);
      await userEvent.click(close);
      expect(isOpen).toHaveTextContent(FALSE);
    } else {
      throw new Error('Test render error');
    }
  });

  it('should properly update acknowledgement state', async () => {
    const { container } = render(<TestComponent />);
    const open = container.querySelector('#open');
    const close = container.querySelector('#close');
    const isOpen = container.querySelector('#isOpen');
    const isAck = container.querySelector('#isAck');
    const greetingReady = container.querySelector('#greetingReady');
    const ackFalseRequired = container.querySelector('#ack-false-required');
    const ackTrueRequired = container.querySelector('#ack-true-required');
    const ackFalseNotRequired = container.querySelector('#ack-false-not-required');
    const ackTrueNotRequired = container.querySelector('#ack-true-not-required');

    if (
      open !== null &&
      close !== null &&
      isOpen !== null &&
      isAck !== null &&
      greetingReady !== null &&
      ackFalseRequired !== null &&
      ackTrueRequired !== null &&
      ackFalseNotRequired !== null &&
      ackTrueNotRequired !== null
    ) {
      await userEvent.click(open);
      expect(isOpen).toHaveTextContent(TRUE);
      expect(isAck).toHaveTextContent(FALSE);
      expect(greetingReady).toHaveTextContent(FALSE);

      await userEvent.click(open);
      await userEvent.click(ackFalseRequired);
      expect(isOpen).toHaveTextContent(FALSE);
      expect(isAck).toHaveTextContent(FALSE);
      expect(greetingReady).toHaveTextContent(FALSE);

      await userEvent.click(open);
      await userEvent.click(ackTrueRequired);
      expect(isOpen).toHaveTextContent(FALSE);
      expect(isAck).toHaveTextContent(TRUE);
      expect(greetingReady).toHaveTextContent(TRUE);

      await userEvent.click(open);
      await userEvent.click(ackFalseNotRequired);
      expect(isOpen).toHaveTextContent(FALSE);
      expect(isAck).toHaveTextContent(FALSE);
      expect(greetingReady).toHaveTextContent(TRUE);

      await userEvent.click(open);
      await userEvent.click(ackTrueNotRequired);
      expect(isOpen).toHaveTextContent(FALSE);
      expect(isAck).toHaveTextContent(TRUE);
      expect(greetingReady).toHaveTextContent(TRUE);
    } else {
      throw new Error('Test render error');
    }
  });
});
