import { expect } from 'chai';
import { convertWebviewHtmlToMarkdown, convertMarkdownToWebviewHtml } from '../utils/pandocPipeline';

describe('PandocPipeline (Unit)', () => {
  it('should convert Markdown to HTML and back (round-trip, math)', async () => {
    const md = 'Euler: $e^{i\pi} + 1 = 0$';
    const html = await convertMarkdownToWebviewHtml(md);
    const roundtrip = await convertWebviewHtmlToMarkdown(html);
    expect(roundtrip).to.include('$e^{i');
  });

  it('should strip editor artifacts from HTML', async () => {
    const html = '<div contenteditable="true">Hello <span data-pos="1">world</span></div>';
    const md = await convertWebviewHtmlToMarkdown(html);
    expect(md).to.include('Hello world');
    expect(md).to.not.include('data-pos');
  });

  it('should handle empty input gracefully', async () => {
    const md = await convertWebviewHtmlToMarkdown('');
    expect(md).to.equal('');
  });
}); 