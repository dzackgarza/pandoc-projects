"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Logger = exports.LogLevel = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const vscode = __importStar(require("vscode"));
const os = __importStar(require("os"));
const util_1 = require("util");
const writeFile = (0, util_1.promisify)(fs.writeFile);
const rename = (0, util_1.promisify)(fs.rename);
const unlink = (0, util_1.promisify)(fs.unlink);
const stat = (0, util_1.promisify)(fs.stat);
const mkdir = (0, util_1.promisify)(fs.mkdir);
const appendFile = (0, util_1.promisify)(fs.appendFile);
/**
 * Log levels for the logger
 */
var LogLevel;
(function (LogLevel) {
    /**
     * Debug level for detailed debugging information
     */
    LogLevel["DEBUG"] = "DEBUG";
    /**
     * Info level for general operational messages
     */
    LogLevel["INFO"] = "INFO";
    /**
     * Warning level for potentially harmful situations
     */
    LogLevel["WARN"] = "WARN";
    /**
     * Error level for error events that might still allow the application to continue running
     */
    LogLevel["ERROR"] = "ERROR";
})(LogLevel || (exports.LogLevel = LogLevel = {}));
class Logger {
    /**
     * Initializes a new instance of the Logger class.
     * If a context is provided, the logger is immediately initialized.
     * @param context - Optional VS Code extension context for storing logs.
     */
    constructor(context) {
        this.context = context;
        this.logFile = '';
        this.logStream = null;
        this.logLevel = LogLevel.INFO;
        this.maxFileSize = 5 * 1024 * 1024; // 5MB
        this.maxBackupFiles = 5;
        this.initialized = false;
        this.pendingLogs = [];
        if (context) {
            this.initialize();
        }
    }
    /**
     * Gets the single instance of the Logger class.
     * If a context is provided and the logger has not been initialized, it will be initialized.
     * @param context - Optional VS Code extension context for storing logs.
     * @returns The single instance of the Logger class.
     */
    static getInstance(context) {
        if (!Logger.instance) {
            Logger.instance = new Logger(context);
        }
        else if (context && !Logger.instance.initialized) {
            Logger.instance.context = context;
            Logger.instance.initialize();
        }
        return Logger.instance;
    }
    /**
     * Initializes the logger by setting up the log directory and log file stream.
     * Ensures that any pending logs are processed once the logger is initialized.
     * Throws an error if the VS Code extension context is not provided.
     * This method is intended to be called when the logger needs to be set up
     * with a valid context for storing logs.
     * Handles errors during initialization and logs them to the console.
     * @private
     */
    initialize() {
        try {
            if (!this.context) {
                throw new Error('Context not provided for logger initialization');
            }
            const logDir = path.join(this.context.globalStorageUri.fsPath, 'logs');
            if (!fs.existsSync(logDir)) {
                fs.mkdirSync(logDir, { recursive: true });
            }
            this.logFile = path.join(logDir, 'pandoc-wysiwyg.log');
            this.initializeLogStream();
            this.initialized = true;
            // Process any pending logs
            if (this.pendingLogs.length > 0) {
                this.pendingLogs.forEach(log => {
                    this.writeToLogDirectly(log);
                });
                this.pendingLogs = [];
            }
        }
        catch (error) {
            console.error('Failed to initialize logger:', error);
        }
    }
    setLogLevel(level) {
        this.logLevel = level;
    }
    getLogLevelNumber(level) {
        var _a;
        const levels = {
            [LogLevel.DEBUG]: 0,
            [LogLevel.INFO]: 1,
            [LogLevel.WARN]: 2,
            [LogLevel.ERROR]: 3
        };
        return (_a = levels[level]) !== null && _a !== void 0 ? _a : 1;
    }
    shouldLog(level) {
        return this.getLogLevelNumber(level) >= this.getLogLevelNumber(this.logLevel);
    }
    /**
     * Initializes the log file stream
     * @private
     */
    initializeLogStream() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                // Close existing stream if it exists
                if (this.logStream) {
                    yield new Promise((resolve) => {
                        if (this.logStream) {
                            this.logStream.end(() => resolve());
                        }
                        else {
                            resolve();
                        }
                    });
                }
                // Check file size and rotate if needed
                try {
                    const stats = yield stat(this.logFile).catch(() => null);
                    if (stats && stats.size > this.maxFileSize) {
                        yield this.rotateLogs();
                    }
                }
                catch (error) {
                    // File might not exist yet, which is fine
                }
                // Ensure directory exists
                yield mkdir(path.dirname(this.logFile), { recursive: true });
                // Create a new write stream
                this.logStream = fs.createWriteStream(this.logFile, {
                    flags: 'a',
                    encoding: 'utf8',
                    mode: 0o666 // rw-rw-rw- permissions
                });
                // Handle stream errors
                this.logStream.on('error', (err) => {
                    console.error('Log stream error:', err);
                    this.logStream = null;
                });
                // Write initialization message
                this.writeToLogDirectly(`\n${'-'.repeat(80)}\n` +
                    `Log initialized at ${new Date().toISOString()}\n` +
                    `Process ID: ${process.pid}\n` +
                    `Node.js: ${process.version}\n` +
                    `VSCode: ${vscode.version}\n` +
                    `Platform: ${process.platform} ${process.arch}\n` +
                    `Log level: ${this.logLevel}\n` +
                    `Log file: ${this.logFile}\n` +
                    `${'-'.repeat(80)}\n`);
            }
            catch (error) {
                console.error('Failed to initialize log stream:', error);
            }
        });
    }
    /**
     * Rotates log files to prevent them from growing too large
     * @private
     */
    rotateLogs() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                // Create backup files in reverse order to avoid overwriting
                for (let i = this.maxBackupFiles - 1; i >= 0; i--) {
                    const source = i === 0 ? this.logFile : `${this.logFile}.${i}`;
                    const target = `${this.logFile}.${i + 1}`;
                    try {
                        if (fs.existsSync(source)) {
                            if (fs.existsSync(target)) {
                                yield unlink(target);
                            }
                            yield rename(source, target);
                        }
                    }
                    catch (err) {
                        console.error(`Error rotating log file ${source}:`, err);
                        // Continue with next file even if one fails
                    }
                }
                // Create a new empty log file
                yield writeFile(this.logFile, '', 'utf8');
            }
            catch (error) {
                console.error('Log rotation failed:', error);
                throw error; // Re-throw to allow callers to handle the error
            }
        });
    }
    /**
     * Writes a log message with the specified level
     * @param level - The log level
     * @param message - The message to log
     * @param args - Additional data to include in the log
     * @private
     */
    writeToLog(level, message, ...args) {
        if (!this.shouldLog(level)) {
            return;
        }
        const timestamp = new Date().toISOString();
        let formattedMessage = `[${timestamp}] [${level}] ${message}`;
        // Format arguments if present
        if (args.length > 0) {
            try {
                const formattedArgs = args.map(arg => {
                    if (arg instanceof Error) {
                        return Object.assign({ message: arg.message, name: arg.name, stack: arg.stack }, arg.details);
                    }
                    return arg;
                });
                // Only add newline if we have complex objects to format
                const needsNewline = formattedArgs.some(arg => typeof arg === 'object' && arg !== null && Object.keys(arg).length > 0);
                if (needsNewline) {
                    formattedMessage += '\n';
                }
                formattedMessage += JSON.stringify(formattedArgs.length === 1 ? formattedArgs[0] : formattedArgs, this.sanitizeForJson, 2);
            }
            catch (error) {
                formattedMessage += ` [Error stringifying args: ${error}]`;
            }
        }
        formattedMessage += os.EOL;
        if (this.initialized && this.logStream) {
            this.writeToLogDirectly(formattedMessage);
        }
        else {
            // Store logs until logger is initialized
            this.pendingLogs.push(formattedMessage);
            // Fallback to console with appropriate log level
            const consoleMethod = console[level.toLowerCase()] || console.log;
            consoleMethod(`[PandocWYSIWYG] ${formattedMessage.trim()}`);
            // Keep pending logs from growing too large
            if (this.pendingLogs.length > 100) {
                this.pendingLogs.shift(); // Remove oldest log
            }
        }
    }
    /**
     * Writes directly to the log stream
     * @param logMessage - The message to write
     * @private
     */
    writeToLogDirectly(logMessage) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.logStream) {
                try {
                    yield this.initializeLogStream();
                    if (!this.logStream) {
                        console.error('Log stream not available after initialization');
                        return;
                    }
                }
                catch (error) {
                    console.error('Failed to initialize log stream:', error);
                    return;
                }
            }
            try {
                if (this.logStream) {
                    const canWrite = this.logStream.write(logMessage, (err) => {
                        if (err) {
                            console.error('Error writing to log file:', err);
                            // Attempt to recover by reinitializing the stream
                            this.logStream = null;
                        }
                    });
                    // Handle backpressure
                    if (!canWrite) {
                        yield new Promise((resolve) => {
                            if (this.logStream) {
                                this.logStream.once('drain', resolve);
                            }
                            else {
                                resolve();
                            }
                        });
                    }
                }
            }
            catch (error) {
                console.error('Failed to write to log:', error);
                this.logStream = null; // Force reinitialization on next write attempt
            }
        });
    }
    // Helper to handle circular references in JSON.stringify
    sanitizeForJson(key, value) {
        if (value instanceof Error) {
            const error = {};
            Object.getOwnPropertyNames(value).forEach(k => {
                error[k] = value[k];
            });
            return error;
        }
        return value;
    }
    debug(message, ...args) {
        this.writeToLog(LogLevel.DEBUG, message, ...args);
    }
    info(message, ...args) {
        this.writeToLog(LogLevel.INFO, message, ...args);
    }
    warn(message, ...args) {
        this.writeToLog(LogLevel.WARN, message, ...args);
    }
    error(message, ...args) {
        this.writeToLog(LogLevel.ERROR, message, ...args);
    }
    /**
     * Logs an error with additional context
     * @param error - The error to log
     * @param context - Additional context about where the error occurred
     * @param extra - Any extra data to include in the log
     */
    logError(error, context = '', extra = {}) {
        const errorInfo = Object.assign(Object.assign({ name: error.name, message: error.message, stack: error.stack }, error.details), extra);
        // Remove undefined values
        Object.keys(errorInfo).forEach(key => errorInfo[key] === undefined && delete errorInfo[key]);
        this.error(`Error${context ? ` in ${context}` : ''}: ${error.message}`, errorInfo);
    }
    /**
     * Disposes the logger, ensuring all pending writes are completed
     * @returns A promise that resolves when the logger is fully disposed
     */
    dispose() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                if (this.logStream) {
                    yield new Promise((resolve) => {
                        if (this.logStream) {
                            this.logStream.end(() => resolve());
                        }
                        else {
                            resolve();
                        }
                    });
                    this.logStream = null;
                }
                // Process any remaining pending logs
                if (this.pendingLogs.length > 0) {
                    try {
                        yield appendFile(this.logFile, this.pendingLogs.join(''), 'utf8');
                        this.pendingLogs = [];
                    }
                    catch (error) {
                        console.error('Failed to write pending logs during dispose:', error);
                    }
                }
            }
            catch (error) {
                console.error('Error during logger disposal:', error);
                throw error;
            }
        });
    }
}
exports.Logger = Logger;
