import * as vscode from 'vscode';
import { SidebarProvider } from './sidebarProvider';

export function activate(context: vscode.ExtensionContext): void {
  const sidebarProvider = new SidebarProvider(context.extensionUri);
  const sidebar = vscode.window.registerWebviewViewProvider(
    'codeforge.askPanel',
    sidebarProvider,
    { webviewOptions: { retainContextWhenHidden: true } }
  );

  const openPanel = vscode.commands.registerCommand('codeforge.ask', () => {
    vscode.commands.executeCommand('workbench.view.sidebar');
  });

  context.subscriptions.push(sidebar, openPanel);
}

export function deactivate(): void {}
