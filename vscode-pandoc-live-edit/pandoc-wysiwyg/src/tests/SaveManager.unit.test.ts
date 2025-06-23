import { expect } from 'chai';
import { SaveManager } from '../services/FileBroker/SaveManager';
import * as fs from 'fs/promises';
import * as path from 'path';

describe('SaveManager (Unit)', () => {
  const testFile = path.join('/tmp', `save-manager-unit-${Date.now()}.md`);

  afterEach(async () => {
    try { await fs.unlink(testFile); } catch {}
    const dir = path.dirname(testFile);
    const files = await fs.readdir(dir);
    for (const f of files) {
      if (f.startsWith('.backup-') && f.includes(path.basename(testFile))) {
        try { await fs.unlink(path.join(dir, f)); } catch {}
      }
    }
  });

  it('should be a singleton', () => {
    const mgr1 = SaveManager.getInstance();
    const mgr2 = SaveManager.getInstance();
    expect(mgr1).to.equal(mgr2);
  });

  it('should queue and save the latest content', (done) => {
    const mgr = SaveManager.getInstance();
    mgr.requestSave(testFile, 'first');
    mgr.requestSave(testFile, 'second');
    setTimeout(async () => {
      const content = await fs.readFile(testFile, 'utf8');
      expect(content).to.equal('second');
      done();
    }, 1000);
  });

  it('should create at most 5 backups', async function () {
    this.timeout(5000);
    const mgr = SaveManager.getInstance();
    await fs.writeFile(testFile, 'original', 'utf8');
    for (let i = 0; i < 7; ++i) {
      mgr.requestSave(testFile, `content${i}`);
      await new Promise(res => setTimeout(res, 600));
    }
    const dir = path.dirname(testFile);
    const files = await fs.readdir(dir);
    const backups = files.filter(f => f.startsWith('.backup-') && f.includes(path.basename(testFile)));
    expect(backups.length).to.be.at.most(5);
  });
}); 