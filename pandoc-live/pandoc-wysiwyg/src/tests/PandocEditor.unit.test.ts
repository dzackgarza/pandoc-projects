import { expect } from 'chai';
import * as sinon from 'sinon';
import * as vscode from 'vscode';
import { PandocEditor } from '../alpha/AlphaPandocEditor';
import 'mocha';

describe('PandocEditor (Unit)', () => {
  let context: vscode.ExtensionContext;

  beforeEach(() => {
    context = { extensionUri: {}, subscriptions: [] } as any;
  });

  it('should construct with context', () => {
    const editor = new PandocEditor(context);
    expect(editor).to.be.an('object');
  });

  it('should have a static viewType', () => {
    expect(PandocEditor.viewType).to.be.a('string');
  });

  it('should have core methods', () => {
    const editor = new PandocEditor(context);
    expect(editor).to.have.property('resolveCustomTextEditor');
    expect(editor).to.have.property('updateWebview');
    expect(editor).to.have.property('updateDocument');
  });

  it('should generate a nonce', () => {
    const editor = new PandocEditor(context);
    const nonce = (editor as any).getNonce();
    expect(nonce).to.be.a('string');
    expect(nonce.length).to.be.greaterThan(0);
  });
}); 