import { recoverMarkdownFromCorrupted } from '../utils/recoverMarkdownFromCorrupted';
import * as fs from 'fs';
import * as path from 'path';

describe('recoverMarkdownFromCorrupted', () => {
  it('recovers a standard markdown document from corrupted PRIORITIES.md', () => {
    const corrupted = fs.readFileSync(path.join(__dirname, 'corrupted_PRIORITIES.md'), 'utf8');
    const recovered = recoverMarkdownFromCorrupted(corrupted);
    // The recovered document should contain at least a recognizable heading and bullet list
    expect(recovered).toMatch(/#|\*|\-/); // crude check for markdown structure
    // Optionally, check for specific known phrases
    expect(recovered).toMatch(/roadmap components/);
    expect(recovered).toMatch(/MVP Features/);
  });
}); 