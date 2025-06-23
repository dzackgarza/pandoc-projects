import * as vscode from 'vscode';
/**
 * Log levels for the logger
 */
export declare enum LogLevel {
    /**
     * Debug level for detailed debugging information
     */
    DEBUG = "DEBUG",
    /**
     * Info level for general operational messages
     */
    INFO = "INFO",
    /**
     * Warning level for potentially harmful situations
     */
    WARN = "WARN",
    /**
     * Error level for error events that might still allow the application to continue running
     */
    ERROR = "ERROR"
}
export declare class Logger {
    private context?;
    private static instance;
    private logFile;
    private logStream;
    private logLevel;
    private readonly maxFileSize;
    private readonly maxBackupFiles;
    private initialized;
    private pendingLogs;
    /**
     * Initializes a new instance of the Logger class.
     * If a context is provided, the logger is immediately initialized.
     * @param context - Optional VS Code extension context for storing logs.
     */
    private constructor();
    /**
     * Gets the single instance of the Logger class.
     * If a context is provided and the logger has not been initialized, it will be initialized.
     * @param context - Optional VS Code extension context for storing logs.
     * @returns The single instance of the Logger class.
     */
    static getInstance(context?: vscode.ExtensionContext): Logger;
    /**
     * Initializes the logger by setting up the log directory and log file stream.
     * Ensures that any pending logs are processed once the logger is initialized.
     * Throws an error if the VS Code extension context is not provided.
     * This method is intended to be called when the logger needs to be set up
     * with a valid context for storing logs.
     * Handles errors during initialization and logs them to the console.
     * @private
     */
    private initialize;
    setLogLevel(level: LogLevel): void;
    private getLogLevelNumber;
    private shouldLog;
    /**
     * Initializes the log file stream
     * @private
     */
    private initializeLogStream;
    /**
     * Rotates log files to prevent them from growing too large
     * @private
     */
    private rotateLogs;
    /**
     * Writes a log message with the specified level
     * @param level - The log level
     * @param message - The message to log
     * @param args - Additional data to include in the log
     * @private
     */
    private writeToLog;
    /**
     * Writes directly to the log stream
     * @param logMessage - The message to write
     * @private
     */
    private writeToLogDirectly;
    private sanitizeForJson;
    debug(message: string, ...args: any[]): void;
    info(message: string, ...args: any[]): void;
    warn(message: string, ...args: any[]): void;
    error(message: string, ...args: any[]): void;
    /**
     * Logs an error with additional context
     * @param error - The error to log
     * @param context - Additional context about where the error occurred
     * @param extra - Any extra data to include in the log
     */
    logError(error: Error, context?: string, extra?: Record<string, any>): void;
    /**
     * Disposes the logger, ensuring all pending writes are completed
     * @returns A promise that resolves when the logger is fully disposed
     */
    dispose(): Promise<void>;
}
