module.exports = {
  version: '1.0.0',
  workspace: {
    getConfiguration: () => ({ get: () => 'INFO' }),
    applyEdit: async () => true,
    onDidChangeTextDocument: () => ({ dispose: () => {} }),
  },
  window: {
    registerCustomEditorProvider: () => ({}),
    showErrorMessage: () => {},
    showInformationMessage: () => {},
  },
  Range: class {},
  WorkspaceEdit: class {
    replace() {}
  },
  Uri: {
    file: (path) => ({ fsPath: path, toString: () => path })
  },
  TextDocument: class {
    constructor() {
      this.isUntitled = false;
      this.uri = { fsPath: '/tmp/mock.md', toString: () => '/tmp/mock.md', scheme: 'file' };
      this.version = 1;
      this.isDirty = false;
      this.fileName = '/tmp/mock.md';
      this.languageId = 'markdown';
      this.isClosed = false;
    }
    getText() { return '# Mock'; }
    save() { return Promise.resolve(true); }
  },
  ExtensionContext: class {
    constructor() {
      this.globalStorageUri = { fsPath: '/tmp' };
      this.extensionPath = '/tmp';
    }
  },
}; 