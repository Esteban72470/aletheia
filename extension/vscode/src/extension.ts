/**
 * Aletheia VS Code Extension
 *
 * Main entry point for the extension.
 */

import * as vscode from 'vscode';
import { insertBlockCommand } from './commands/insertBlock';
import { parseFileCommand } from './commands/parseFile';
import { previewCommand } from './commands/preview';
import { SidecarClient } from './sidecar/client';
import { getConfig } from './utils/config';

let sidecarClient: SidecarClient | undefined;

/**
 * Called when the extension is activated.
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('Aletheia extension is now active');

    // Initialize sidecar client
    const config = getConfig();
    sidecarClient = new SidecarClient(
        config.get<string>('sidecar.host', '127.0.0.1'),
        config.get<number>('sidecar.port', 8420)
    );

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('aletheia.parseFile', () =>
            parseFileCommand(sidecarClient!)
        ),
        vscode.commands.registerCommand('aletheia.preview', () =>
            previewCommand(context, sidecarClient!)
        ),
        vscode.commands.registerCommand('aletheia.insertBlock', () =>
            insertBlockCommand()
        ),
        vscode.commands.registerCommand('aletheia.startSidecar', () =>
            startSidecar()
        ),
        vscode.commands.registerCommand('aletheia.stopSidecar', () =>
            stopSidecar()
        )
    );

    // Auto-start sidecar if configured
    if (config.get<boolean>('sidecar.autoStart', true)) {
        checkSidecarHealth();
    }
}

/**
 * Called when the extension is deactivated.
 */
export function deactivate() {
    console.log('Aletheia extension is now deactivated');
    sidecarClient = undefined;
}

/**
 * Check sidecar health and notify user if unavailable.
 */
async function checkSidecarHealth(): Promise<void> {
    if (!sidecarClient) {
        return;
    }

    try {
        await sidecarClient.health();
        console.log('Aletheia sidecar is healthy');
    } catch (error) {
        vscode.window.showWarningMessage(
            'Aletheia sidecar is not running. Start it with "Aletheia: Start Sidecar Service".'
        );
    }
}

/**
 * Start the sidecar service.
 */
async function startSidecar(): Promise<void> {
    const terminal = vscode.window.createTerminal('Aletheia Sidecar');
    terminal.sendText('aletheia serve');
    terminal.show();

    vscode.window.showInformationMessage('Starting Aletheia sidecar service...');
}

/**
 * Stop the sidecar service.
 */
async function stopSidecar(): Promise<void> {
    vscode.window.showInformationMessage('Stopping Aletheia sidecar service...');
    // TODO: Implement proper shutdown
}
