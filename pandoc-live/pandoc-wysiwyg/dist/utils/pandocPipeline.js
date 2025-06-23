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
exports.convertMarkdownToWebviewHtml = convertMarkdownToWebviewHtml;
exports.convertWebviewHtmlToMarkdown = convertWebviewHtmlToMarkdown;
const cp = __importStar(require("child_process"));
const prettier = __importStar(require("prettier"));
// Simple logger fallback if the logger module is not available
const logger = {
    debug: (message, ...args) => console.debug(`[PandocPipeline] ${message}`, ...args),
    warn: (message, ...args) => console.warn(`[PandocPipeline] ${message}`, ...args),
    error: (message, ...args) => console.error(`[PandocPipeline] ${message}`, ...args)
};
try {
    // Try to use the application logger if available
    const { getLogger } = require('./logger');
    const appLogger = getLogger();
    if (appLogger) {
        Object.assign(logger, appLogger);
    }
}
catch (e) {
    // Use console logger if the logger module is not available
    console.debug('Using console logger as fallback');
}
// =================================================================
// PIPELINE 1: Original File -> Webview
// Converts clean Markdown into HTML suitable for the contenteditable webview.
// =================================================================
/**
 * Converts a Markdown string into an HTML string for display in the webview.
 * Uses Pandoc with MathJax support.
 * @param markdown The source Markdown from the file.
 * @returns A promise that resolves to an HTML string.
 */
function convertMarkdownToWebviewHtml(markdown) {
    return __awaiter(this, void 0, void 0, function* () {
        logger.debug('Starting Markdown -> Webview HTML conversion.');
        return new Promise((resolve, reject) => {
            const pandoc = cp.spawn('pandoc', [
                '--from=markdown+tex_math_dollars', // Explicitly enable $...$ and $$...$$ math
                '--to=html', // Convert to HTML
                '--mathjax' // Output MathJax-compatible math elements
            ]);
            let stdout = '';
            let stderr = '';
            pandoc.stdout.on('data', (data) => (stdout += data.toString()));
            pandoc.stderr.on('data', (data) => (stderr += data.toString()));
            pandoc.on('error', (err) => reject(new Error(`Failed to start Pandoc: ${err.message}`)));
            pandoc.on('close', (code) => {
                if (stderr)
                    logger.warn(`Pandoc stderr (MD->HTML): ${stderr}`);
                if (code === 0) {
                    logger.debug('Markdown -> Webview HTML conversion successful.');
                    resolve(stdout);
                }
                else {
                    const error = new Error(`Pandoc exited with code ${code} during MD->HTML conversion.`);
                    logger.error(error.message);
                    reject(error);
                }
            });
            pandoc.stdin.write(markdown);
            pandoc.stdin.end();
        });
    });
}
// =================================================================
// PIPELINE 2: Webview -> Original File
// Converts messy HTML from the webview into clean, formatted Markdown for saving.
// This is a multi-step process: Clean -> Convert -> Post-Process -> Format
// =================================================================
/**
 * Surgically cleans HTML from a contenteditable element before conversion.
 * The goal is to remove browser-specific artifacts without destroying semantic content.
 * @param html The raw HTML string from the webview.
 * @returns A cleaner HTML string.
 */
function cleanIncomingHtml(html) {
    let cleaned = html;
    // Remove artifacts from contenteditable divs
    cleaned = cleaned.replace(/\s+contenteditable="[^"]*"/g, '');
    cleaned = cleaned.replace(/\s+spellcheck="[^"]*"/g, '');
    // Clean up empty divs that are often left behind by editors
    cleaned = cleaned.replace(/<div>\s*<\/div>/g, '');
    return cleaned.trim();
}
/**
 * Post-processes Markdown generated by Pandoc to fix common formatting issues.
 * @param markdown The raw Markdown from Pandoc.
 * @returns Cleaned Markdown.
 */
function postProcessPandocMarkdown(markdown) {
    let cleaned = markdown;
    // Collapse more than two consecutive newlines into just two
    cleaned = cleaned.replace(/\n{3,}/g, '\n\n');
    return cleaned.trim();
}
/**
 * Converts an HTML string to a Markdown string using Pandoc.
 * @param cleanedHtml A cleaned HTML string.
 * @returns A promise that resolves to a raw Markdown string.
 */
function pandocHtmlToRawMarkdown(cleanedHtml) {
    return __awaiter(this, void 0, void 0, function* () {
        return new Promise((resolve, reject) => {
            const pandoc = cp.spawn("pandoc", [
                "--from=html-native_divs-native_spans", // Read HTML, preserving divs/spans
                "--to=commonmark_x", // A robust Markdown flavor
                "--wrap=none", // Don't hard-wrap lines
            ]);
            let stdout = "";
            let stderr = "";
            pandoc.stdout.on("data", (chunk) => (stdout += chunk.toString()));
            pandoc.stderr.on("data", (chunk) => (stderr += chunk.toString()));
            pandoc.on('error', (err) => reject(new Error(`Failed to start Pandoc: ${err.message}`)));
            pandoc.on("close", (code) => {
                if (stderr)
                    logger.warn(`Pandoc stderr (HTML->MD): ${stderr}`);
                if (code === 0) {
                    resolve(stdout);
                }
                else {
                    const error = new Error(`Pandoc exited with code ${code} during HTML->MD conversion.`);
                    logger.error(error.message);
                    reject(error);
                }
            });
            pandoc.stdin.write(cleanedHtml);
            pandoc.stdin.end();
        });
    });
}
/**
 * The main conversion function for the Webview -> File pipeline.
 * Takes raw HTML from the webview and returns clean, formatted Markdown.
 * @param html The raw HTML string from the webview editor.
 * @returns A promise that resolves to a final, clean Markdown string.
 */
/**
 * Executes Pandoc with the given input, format, and arguments
 */
function executePandoc(input_1, fromFormat_1, toFormat_1) {
    return __awaiter(this, arguments, void 0, function* (input, fromFormat, toFormat, args = []) {
        return new Promise((resolve, reject) => {
            const pandoc = cp.spawn('pandoc', [
                `--from=${fromFormat}`,
                `--to=${toFormat}`,
                ...args
            ]);
            let stdout = '';
            let stderr = '';
            pandoc.stdout.on('data', (data) => (stdout += data.toString()));
            pandoc.stderr.on('data', (data) => (stderr += data.toString()));
            pandoc.on('error', (err) => {
                logger.error(`Failed to start Pandoc: ${err.message}`);
                reject(new Error(`Failed to start Pandoc: ${err.message}`));
            });
            pandoc.on('close', (code) => {
                if (stderr) {
                    logger.warn(`Pandoc stderr: ${stderr}`);
                }
                if (code === 0) {
                    resolve(stdout);
                }
                else {
                    const error = new Error(`Pandoc exited with code ${code}`);
                    logger.error(error.message, { stderr });
                    reject(error);
                }
            });
            pandoc.stdin.write(input);
            pandoc.stdin.end();
        });
    });
}
function convertWebviewHtmlToMarkdown(html) {
    return __awaiter(this, void 0, void 0, function* () {
        logger.debug('Starting Webview HTML -> Markdown conversion pipeline.');
        // 1. Clean the incoming HTML of editor artifacts.
        const cleanedHtml = cleanIncomingHtml(html);
        // 2. Convert the cleaned HTML to raw Markdown using Pandoc.
        const rawMarkdown = yield pandocHtmlToRawMarkdown(cleanedHtml);
        // 3. Post-process the Markdown to fix common issues.
        const processedMarkdown = postProcessPandocMarkdown(rawMarkdown);
        // 4. Format the final Markdown with Prettier for consistency.
        try {
            logger.debug('Formatting final Markdown with Prettier...');
            const formattedMarkdown = yield prettier.format(processedMarkdown, {
                parser: 'markdown',
                proseWrap: 'preserve',
            });
            logger.debug('Webview HTML -> Markdown pipeline successful.');
            return formattedMarkdown;
        }
        catch (error) {
            logger.error('Prettier formatting failed. Returning unformatted Markdown.', { error });
            return processedMarkdown; // Return the processed version if Prettier fails
        }
    });
}
exports.default = {
    convertMarkdownToWebviewHtml,
    convertWebviewHtmlToMarkdown,
    // Export these for testing
    _internals: {
        cleanIncomingHtml,
        postProcessPandocMarkdown,
        pandocHtmlToRawMarkdown
    }
};
