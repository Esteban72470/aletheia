/**
 * Configuration Utilities
 */

import * as vscode from 'vscode';

/**
 * Get Aletheia configuration.
 */
export function getConfig(): vscode.WorkspaceConfiguration {
    return vscode.workspace.getConfiguration('aletheia');
}

/**
 * Get sidecar configuration.
 */
export function getSidecarConfig(): {
    host: string;
    port: number;
    autoStart: boolean;
} {
    const config = getConfig();
    return {
        host: config.get<string>('sidecar.host', '127.0.0.1'),
        port: config.get<number>('sidecar.port', 8420),
        autoStart: config.get<boolean>('sidecar.autoStart', true)
    };
}

/**
 * Get preview configuration.
 */
export function getPreviewConfig(): {
    showOverlay: boolean;
    theme: string;
} {
    const config = getConfig();
    return {
        showOverlay: config.get<boolean>('preview.showOverlay', true),
        theme: config.get<string>('preview.theme', 'auto')
    };
}
