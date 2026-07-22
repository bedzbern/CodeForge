import * as vscode from 'vscode';
import * as os from 'os';
import { askQuestion } from './apiClient';
import { getStudentIp } from './getStudentIp';

export class SidebarProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = 'codeforge.askPanel';
  private _view?: vscode.WebviewView;

  constructor(private readonly _extensionUri: vscode.Uri) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    _context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ): void {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri],
    };

    webviewView.webview.html = this._getHtml();

    webviewView.webview.onDidReceiveMessage(async (message) => {
      switch (message.type) {
        case 'ask':
          await this._handleAsk(message.question, message.codeSnapshot);
          break;
        case 'grabSelection':
          this._handleGrabSelection();
          break;
      }
    });
  }

  private async _handleAsk(question: string, codeSnapshot: string): Promise<void> {
    if (!this._view) { return; }

    const config = vscode.workspace.getConfiguration('codeforge');
    const serverUrl = config.get<string>('serverUrl', 'http://192.168.1.1:8000');

    const editor = vscode.window.activeTextEditor;
    const fileName = editor?.document.fileName ?? 'untitled';
    const lineNumber = editor?.selection.active.line ?? 0;
    const studentIp = getStudentIp();

    this._view.webview.postMessage({ type: 'loading' });

    try {
      const result = await askQuestion(
        serverUrl,
        studentIp,
        question,
        codeSnapshot,
        fileName,
        lineNumber
      );

      this._view.webview.postMessage({
        type: 'response',
        level: result.level,
        levelName: result.level_name,
        response: result.response,
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      this._view.webview.postMessage({ type: 'error', message: msg });
    }
  }

  private _handleGrabSelection(): void {
    const editor = vscode.window.activeTextEditor;
    if (!editor || !this._view) { return; }

    const selection = editor.document.getText(editor.selection);
    this._view.webview.postMessage({ type: 'fillCode', code: selection });
  }

  private _getHtml(): string {
    return /*html*/ `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CodeForge</title>
  <style>
    :root {
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --bg: #ffffff;
      --bg-secondary: #f8fafc;
      --border: #e2e8f0;
      --text: #1e293b;
      --text-muted: #64748b;
      --radius: 6px;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #1e1e1e;
        --bg-secondary: #252526;
        --border: #3e3e3e;
        --text: #d4d4d4;
        --text-muted: #9e9e9e;
      }
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--vscode-font-family, system-ui, sans-serif);
      font-size: 13px;
      color: var(--text);
      background: var(--bg);
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    label {
      font-weight: 600;
      font-size: 12px;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    textarea {
      width: 100%;
      min-height: 80px;
      resize: vertical;
      padding: 8px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      background: var(--bg-secondary);
      color: var(--text);
      font-family: var(--vscode-editor-font-family, monospace);
      font-size: 13px;
    }
    textarea:focus {
      outline: none;
      border-color: var(--accent);
    }
    .btn {
      padding: 6px 12px;
      border: none;
      border-radius: var(--radius);
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
    }
    .btn-primary {
      background: var(--accent);
      color: #fff;
      width: 100%;
      padding: 8px;
    }
    .btn-primary:hover { background: var(--accent-hover); }
    .btn-primary:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    .btn-secondary {
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      color: var(--text);
      font-size: 12px;
    }
    .btn-secondary:hover { background: var(--border); }
    .row {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .response-area {
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 10px;
      white-space: pre-wrap;
      line-height: 1.5;
      max-height: 400px;
      overflow-y: auto;
    }
    .level-badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 11px;
      font-weight: 600;
      background: var(--accent);
      color: #fff;
      margin-bottom: 6px;
    }
    .error {
      color: #ef4444;
      font-size: 12px;
    }
    .hidden { display: none; }
    .status {
      font-size: 12px;
      color: var(--text-muted);
      text-align: center;
      padding: 16px;
    }
  </style>
</head>
<body>
  <label for="question">Your Question</label>
  <textarea id="question" placeholder="What do you need help with?"></textarea>

  <div class="row">
    <button class="btn btn-secondary" id="grabBtn">Grab Selected Code</button>
  </div>

  <label for="code">Code Snapshot</label>
  <textarea id="code" placeholder="Selected code appears here..." style="min-height:60px"></textarea>

  <button class="btn btn-primary" id="askBtn">Ask CodeForge</button>

  <div id="loading" class="status hidden">Thinking...</div>
  <div id="error" class="error hidden"></div>

  <div id="responseArea" class="response-area hidden">
    <div id="levelBadge" class="level-badge"></div>
    <div id="responseText"></div>
  </div>

  <script>
    const vscode = acquireVsCodeApi();

    document.getElementById('askBtn').addEventListener('click', () => {
      const question = document.getElementById('question').value.trim();
      if (!question) { return; }
      const codeSnapshot = document.getElementById('code').value;
      vscode.postMessage({ type: 'ask', question, codeSnapshot });
    });

    document.getElementById('grabBtn').addEventListener('click', () => {
      vscode.postMessage({ type: 'grabSelection' });
    });

    window.addEventListener('message', (event) => {
      const msg = event.data;
      const loading = document.getElementById('loading');
      const error = document.getElementById('error');
      const responseArea = document.getElementById('responseArea');

      switch (msg.type) {
        case 'loading':
          loading.classList.remove('hidden');
          error.classList.add('hidden');
          responseArea.classList.add('hidden');
          document.getElementById('askBtn').disabled = true;
          break;

        case 'response':
          loading.classList.add('hidden');
          error.classList.add('hidden');
          responseArea.classList.remove('hidden');
          document.getElementById('levelBadge').textContent =
            'Level ' + msg.level + ' — ' + msg.levelName;
          document.getElementById('responseText').textContent = msg.response;
          document.getElementById('askBtn').disabled = false;
          break;

        case 'error':
          loading.classList.add('hidden');
          responseArea.classList.add('hidden');
          error.classList.remove('hidden');
          error.textContent = msg.message;
          document.getElementById('askBtn').disabled = false;
          break;

        case 'fillCode':
          document.getElementById('code').value = msg.code;
          break;
      }
    });
  </script>
</body>
</html>`;
  }
}
