import { Logger } from '../../utils/logger';
/**
 * PandocHandler - Centralized service for all Pandoc-related operations
 *
 * Core Responsibilities:
 * 1. Document Conversion: Bidirectional conversion between formats (Markdown ↔ HTML, etc.)
 * 2. Math Processing: MathJax/KaTeX integration with customizable delimiters
 * 3. Bibliography: Citation processing with multiple styles and formats
 * 4. Diagram Generation: SVG, TikZ, and other diagram formats
 * 5. Content Transformation: Custom filters and post-processing
 * 6. Error Handling: Comprehensive error detection and reporting
 * 7. Performance: Efficient processing with caching where appropriate
 *
 * Implementation Notes:
 * - Uses singleton pattern for consistent configuration
 * - Implements proper process management for Pandoc subprocesses
 * - Maintains temporary files for intermediate processing
 * - Provides detailed logging of all operations
 * - Supports both file-based and in-memory operations
 *
 * Security Considerations:
 * - Validates all file paths and command arguments
 * - Implements timeouts for all external processes
 * - Handles large files efficiently
 * - Prevents command injection attacks
 * - Manages temporary file lifecycle securely
 */
/**
 * Custom error class for Pandoc operations
 * Includes additional context like stderr and exit code for better error handling
 */
export declare class PandocError extends Error {
    readonly stderr: string;
    readonly exitCode: number | null;
    readonly args: string[];
    constructor(message: string, stderr?: string, exitCode?: number | null, args?: string[]);
    /**
     * Creates a user-friendly error message
     */
    toUserMessage(): string;
}
export declare class PandocHandler {
    private static instance;
    private logger;
    private tempDir;
    private isReady;
    private config;
    /**
     * Private constructor that accepts a Logger instance
     * @param logger Optional logger instance. If not provided, a default one will be created.
     */
    private constructor();
    /**
     * Gets the singleton instance of PandocHandler
     * @param logger Optional logger instance to use. If not provided, a default one will be created.
     * @returns The singleton instance of PandocHandler
     */
    static getInstance(logger?: Logger): PandocHandler;
    /**
     * Initialize the Pandoc handler
     */
    initialize(): Promise<void>;
    private checkPandocAvailable;
    dispose(): Promise<void>;
    private ensureReady;
    /**
     * Converts a file from one format to another using Pandoc
     *
     * @param inputPath Path to the input file
     * @param outputPath Path where the output should be saved
     * @param options Conversion options
     *
     * Test Cases:
     - Basic format conversion (markdown → html, html → markdown)
     - With custom templates and variables
     - With different math rendering options
     - With bibliography processing
     - With custom filters
     - Error handling for invalid input/output paths
     - Performance with large files
     - Concurrent conversion requests
     *
     * Failure Scenarios:
     - Pandoc not found or not in PATH
     - Input file not found or not readable
     - Output directory not writable
     - Invalid or unsupported format conversion
     - Timeout during conversion
     - Memory issues with large files
     - Permission denied errors
     */
    convertFile(inputPath: string, outputPath: string, options?: ConversionOptions): Promise<void>;
    /**
     * Converts content from one format to another using Pandoc
     * @param content The content to convert
     * @param from The source format (e.g., 'markdown', 'html')
     * @param to The target format (e.g., 'html', 'markdown')
     * @param options Conversion options
     * @returns The converted content
     */
    /**
     * Converts content from one format to another using Pandoc
     * @param content The content to convert
     * @param from The source format (e.g., 'markdown', 'html')
     * @param to The target format (e.g., 'html', 'markdown')
     * @param options Conversion options
     * @returns The converted content
     */
    convertString(content: string, from: string, to: string, options?: ConversionOptions): Promise<string>;
    /**
     * Renders mathematical expressions in content to the specified output format.
     *
     * Supported Formats:
     - HTML (with MathJax/KaTeX)
     - MathML (for better accessibility)
     - SVG (for consistent rendering)
     *
     * Features:
     - Handles both inline ($...$) and display ($$...$$) math
     - Preserves LaTeX source for copy-paste
     - Implements proper error boundaries for malformed math
     - Supports custom delimiters and macros
     *
     * Error Handling:
     - Falls back to raw LaTeX on rendering failures
     - Reports syntax errors with line numbers
     - Handles nested math environments
     */
    renderMath(content: string, options?: MathRenderOptions): Promise<string>;
    processCitations(content: string, bibliography: string | string[], style?: string): Promise<string>;
    renderDiagram(content: string, format?: 'svg' | 'png', diagramType?: 'tikz' | 'mermaid' | 'plantuml'): Promise<string>;
    updateConfig(updates: Partial<PandocConfig>): void;
    resetConfig(): void;
    /**
     * Low-level method to execute Pandoc with the specified arguments and options.
     *
     * Security Measures:
     - Sanitizes all command-line arguments
     - Validates file paths
     - Implements strict resource limits
     - Prevents command injection
     *
     * Error Handling:
     - Captures and enriches error messages
     - Implements timeouts to prevent hanging
     - Handles process signals (SIGTERM, SIGKILL)
     *
     * Performance:
     - Uses streaming for large inputs/outputs
        }
      });
  
      if (input) {
        proc.stdin.write(input);
      }
      proc.stdin.end();
    });
  }
  
  /**
   * Converts HTML to Markdown with preprocessing and postprocessing
   * @param html The HTML content to convert
   * @param options Conversion options
   * @returns Formatted Markdown content
   */
    /**
     * Converts HTML to Markdown with preprocessing and postprocessing
     * @param html The HTML content to convert
     * @param options Conversion options
     * @returns Formatted Markdown content
     */
    convertHtmlToMarkdown(html: string, options?: ConversionOptions): Promise<string>;
    /**
     * Builds the Pandoc command-line arguments based on conversion options
     */
    private buildPandocArgs;
    /**
     * Executes Pandoc with the given arguments and input
     */
    /**
     * Executes Pandoc with the given input, format, and arguments
     * @param args Command line arguments for Pandoc
     * @param input Optional input string to pass to Pandoc
     * @returns Promise that resolves with the output from Pandoc
     */
    private executePandoc;
    /**
     * Cleans HTML from a contenteditable element before conversion
     */
    private cleanIncomingHtml;
    /**
     * Post-processes Markdown generated by Pandoc
     */
    private postProcessPandocMarkdown;
    /**
     * Converts HTML to raw Markdown using Pandoc
     */
    private pandocHtmlToRawMarkdown;
    /**
     * Converts Markdown to HTML with MathJax support
     */
    /**
     * Converts Markdown to HTML with MathJax support
     * @param markdown The markdown content to convert
     * @param options Conversion options
     * @returns HTML content with MathJax support
     */
    convertMarkdownToHtml(markdown: string, options?: ConversionOptions): Promise<string>;
    private normalizeMathDelimiters;
    private processSemanticDivs;
    private processReferences;
    private createTempFile;
    private cleanupTempFiles;
}
export interface PandocConfig {
    mathjaxConfig: Record<string, any>;
    luaFilters: string[];
    additionalArgs: string[];
    citationStyle: string;
    defaultMathDelimiters: {
        inline: [string, string];
        display: [string, string];
    };
    prettierOptions: {
        parser: string;
        proseWrap: string;
        [key: string]: any;
    };
}
export interface ConversionOptions {
    from?: string;
    to?: string;
    standalone?: boolean;
    template?: string;
    variables?: Record<string, string>;
    filters?: string[];
    mathjax?: boolean;
    highlightStyle?: string;
    selfContained?: boolean;
    resourcePath?: string;
    logLevel?: 'debug' | 'info' | 'warning' | 'error';
}
export interface MathRenderOptions {
    displayMode?: boolean;
    output?: 'html' | 'mathml' | 'svg';
    throwOnError?: boolean;
    errorColor?: string;
    macros?: Record<string, string>;
    minRuleThickness?: number;
    maxSize?: number[];
    maxExpand?: number;
    strict?: boolean | string | string[];
}
export interface PandocExecuteOptions {
    timeout?: number;
    cwd?: string;
    env?: NodeJS.ProcessEnv;
    inputEncoding?: BufferEncoding;
    outputEncoding?: BufferEncoding;
    maxBuffer?: number;
    killSignal?: NodeJS.Signals | number;
    uid?: number;
    gid?: number;
    windowsHide?: boolean;
    windowsVerbatimArguments?: boolean;
}
