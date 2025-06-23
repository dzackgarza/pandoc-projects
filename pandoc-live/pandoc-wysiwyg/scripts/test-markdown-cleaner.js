// Simple test runner for markdown cleaner
const { spawn } = require('child_process');
const path = require('path');

// Path to the test file
const testFile = path.join(__dirname, '../src/utils/markdownCleaner.test.ts');

// Use ts-node to run TypeScript tests directly
const testProcess = spawn('npx', ['ts-node', testFile], {
  stdio: 'inherit',
  shell: true
});

testProcess.on('close', (code) => {
  process.exit(code || 0);
});
