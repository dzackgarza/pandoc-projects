module.exports = {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'node',
  testMatch: ['**/src/**/*.test.ts'],
  moduleNameMapper: {
    '^vscode$': '<rootDir>/src/test/__mocks__/vscode.js',
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      useESM: true,
      tsconfig: 'tsconfig.test.json',
    }],
  },
  testPathIgnorePatterns: ['/node_modules/'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/test/**',
    '!**/node_modules/**',
    '!**/__mocks__/**',
  ],
  coverageReporters: ['text', 'lcov'],
  setupFilesAfterEnv: ['<rootDir>/src/test/setupTests.ts'],
  globals: {
    'ts-jest': {
      useESM: true,
    },
  },
  extensionsToTreatAsEsm: ['.ts'],
};
