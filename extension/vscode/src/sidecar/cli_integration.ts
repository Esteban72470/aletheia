/**
 * CLI Integration
 *
 * Utilities for interacting with the Aletheia CLI.
 */

import { ChildProcess, spawn } from 'child_process';
import * as vscode from 'vscode';

let sidecarProcess: ChildProcess | undefined;

/**
 * Start the sidecar process via CLI.
 */
export function startSidecarProcess(port: number = 8420): void {
    if (sidecarProcess) {
        vscode.window.showWarningMessage('Sidecar is already running');
        return;
    }

    sidecarProcess = spawn('aletheia', ['serve', '--port', String(port)], {
        stdio: 'pipe',
        detached: false
    });

    sidecarProcess.stdout?.on('data', (data) => {
        console.log(`Sidecar: ${data}`);
    });

    sidecarProcess.stderr?.on('data', (data) => {
        console.error(`Sidecar error: ${data}`);
    });

    sidecarProcess.on('close', (code) => {
        console.log(`Sidecar exited with code ${code}`);
        sidecarProcess = undefined;
    });
}

/**
 * Stop the sidecar process.
 */
export function stopSidecarProcess(): void {
    if (sidecarProcess) {
        sidecarProcess.kill();
        sidecarProcess = undefined;
    }
}

/**
 * Check if sidecar process is running.
 */
export function isSidecarRunning(): boolean {
    return sidecarProcess !== undefined;
}
