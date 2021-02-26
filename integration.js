const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');

const integrationPath = process.env.INTEGRATION_PATH;

const inFile = path.join(integrationPath, 'text-in.txt');
const outFile = path.join(integrationPath, 'text-out.txt');
const scriptPath = path.join(__dirname, 'venv', 'bin', 'python');
const readInterval = 50; // read interval in ms

const runScript = () => {
  execFile(scriptPath, ['interact.py', '-i', inFile, '-if', '-o', outFile], (err) => {
    if (err) {
      console.error(err);
    }
  });
}

fs.watchFile(inFile, { interval: readInterval }, (curr, prev) => {
  if (curr.mtime === prev.mtime) return;

  runScript();
})
