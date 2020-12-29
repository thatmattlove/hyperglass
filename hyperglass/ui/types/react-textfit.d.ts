declare module 'react-textfit' {
  type RenderFunction = (text: string) => React.ReactNode;
  interface TextfitProps {
    children: React.ReactNode | RenderFunction;
    text?: string;
    /**
     * @default number 1
     */
    min?: number;
    /**
     * @default number 100
     */
    max?: number;
    /**
     * @default single|multi multi
     */
    mode?: 'single' | 'multi';
    /**
     * @default boolean true
     */
    forceSingleModeWidth?: boolean;
    /**
     * @default number 50
     */
    throttle?: number;
    onReady?: (mid: number) => void;
  }
  class Textfit extends React.Component<TextfitProps> {}
}
