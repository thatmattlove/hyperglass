/**
 * Jest Testing Configuration
 *
 * @see https://nextjs.org/docs/testing
 * @type {import('@jest/types').Config.InitialOptions}
 */
const jestConfig = {
  collectCoverageFrom: ['**/*.{ts,tsx}', '!**/*.d.ts', '!**/node_modules/**'],
  testPathIgnorePatterns: ['<rootDir>/node_modules/', '<rootDir>/.next/'],
  testEnvironment: 'jsdom',
  transform: { '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }] },
  transformIgnorePatterns: ['/node_modules/', '^.+\\.module\\.(css|sass|scss)$'],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/components/(.*)$': '<rootDir>/components/$1',
    '^~/components': ['components/index'],
    '^~/components/(.*)$': '<rootDir>/components/$1',
    '^~/context': '<rootDir>/context/index',
    '^~/context/(.*)$': '<rootDir>/context/$1',
    '^~/hooks': '<rootDir>/hooks/index',
    '^~/hooks/(.*)$': '<rootDir>/hooks/$1',
    '^~/state': '<rootDir>/state/index',
    '^~/state/(.*)$': '<rootDir>/state/$1',
    '^~/types': '<rootDir>/types/index',
    '^~/types/(.*)$': '<rootDir>/types/$1',
    '^~/util': '<rootDir>/util/index',
    '^~/util/(.*)$': '<rootDir>/util/$1',
  },
};

module.exports = jestConfig;
