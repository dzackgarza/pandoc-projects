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
exports.PandocEditor = void 0;
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const PandocEditor_1 = require("./editor/PandocEditor");
Object.defineProperty(exports, "PandocEditor", { enumerable: true, get: function () { return PandocEditor_1.PandocEditor; } });
const PandocHandler_1 = require("./services/PandocHandler");
const logger_1 = require("./utils/logger");
function activate(context) {
    return __awaiter(this, void 0, void 0, function* () {
        console.log("Pandoc WYSIWYG extension is now active");
        // Initialize PandocHandler
        try {
            const logger = logger_1.Logger.getInstance();
            const pandocHandler = PandocHandler_1.PandocHandler.getInstance(logger);
            yield pandocHandler.initialize();
            console.log("PandocHandler initialized successfully");
        }
        catch (error) {
            console.error("Failed to initialize PandocHandler:", error);
            vscode.window.showErrorMessage(`Failed to initialize Pandoc integration: ${error instanceof Error ? error.message : String(error)}`);
        }
        // Register our custom editor provider
        const provider = new PandocEditor_1.PandocEditor(context);
        const providerRegistration = vscode.window.registerCustomEditorProvider("pandoc-wysiwyg.editor", provider, {
            webviewOptions: {
                retainContextWhenHidden: true,
                enableFindWidget: true
            },
            supportsMultipleEditorsPerDocument: false
        });
        context.subscriptions.push(providerRegistration);
        // Register the command to open a document in the Pandoc editor
        const openCommand = vscode.commands.registerCommand("pandoc-wysiwyg.openAsPandoc", () => {
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor) {
                vscode.commands.executeCommand("vscode.openWith", activeEditor.document.uri, "pandoc-wysiwyg.editor", vscode.ViewColumn.Beside);
            }
            else {
                vscode.window.showInformationMessage("No active editor");
            }
        });
        context.subscriptions.push(openCommand);
    });
}
function deactivate() {
    console.log("Pandoc WYSIWYG extension is now deactivated");
}
