import { expect } from 'chai';
import { PandocHandler } from '../services/PandocHandler/PandocHandler';

describe('PandocHandler (Unit)', () => {
  it('should be a singleton', () => {
    const handler1 = PandocHandler.getInstance();
    const handler2 = PandocHandler.getInstance();
    expect(handler1).to.equal(handler2);
  });

  it('should have an initialize method', async () => {
    const handler = PandocHandler.getInstance();
    expect(handler.initialize).to.be.a('function');
    await handler.initialize(); // Should not throw
  });

  it('should have a convertFile method', async () => {
    const handler = PandocHandler.getInstance();
    expect(handler.convertFile).to.be.a('function');
    await handler.convertFile('/tmp/in.md', '/tmp/out.html'); // Should not throw (stub)
  });

  it('should have a convertString method', async () => {
    const handler = PandocHandler.getInstance();
    expect(handler.convertString).to.be.a('function');
    await handler.convertString('# Test', 'markdown', 'html'); // Should not throw (stub)
  });

  it('should have a renderMath method', async () => {
    const handler = PandocHandler.getInstance();
    expect(handler.renderMath).to.be.a('function');
    await handler.renderMath('E=mc^2'); // Should not throw (stub)
  });

  it('should have a processCitations method', async () => {
    const handler = PandocHandler.getInstance();
    expect(handler.processCitations).to.be.a('function');
    await handler.processCitations('text', 'refs.bib'); // Should not throw (stub)
  });

  it('should have a renderDiagram method', async () => {
    const handler = PandocHandler.getInstance();
    expect(handler.renderDiagram).to.be.a('function');
    await handler.renderDiagram('diagram code'); // Should not throw (stub)
  });

  it('should have config management methods', () => {
    const handler = PandocHandler.getInstance();
    expect(handler.updateConfig).to.be.a('function');
    expect(handler.resetConfig).to.be.a('function');
  });

  it('should handle file system errors in convertFile (stub)', async () => {
    // Simulate file system error (stub)
  });

  it('should handle conversion errors in convertString (stub)', async () => {
    // Simulate Pandoc conversion error (stub)
  });
}); 