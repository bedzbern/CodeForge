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
Object.defineProperty(exports, "__esModule", { value: true });
exports.askQuestion = askQuestion;
const http = __importStar(require("http"));
const https = __importStar(require("https"));
async function askQuestion(serverUrl, studentIp, question, codeSnapshot, fileName, lineNumber) {
    const payload = {
        student_ip: studentIp,
        question,
        code_snapshot: codeSnapshot,
        file_name: fileName,
        line_number: lineNumber,
    };
    const url = new URL('/api/ask', serverUrl);
    const body = JSON.stringify(payload);
    return new Promise((resolve, reject) => {
        const transport = url.protocol === 'https:' ? https : http;
        const req = transport.request({
            hostname: url.hostname,
            port: url.port,
            path: url.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body),
            },
        }, (res) => {
            const chunks = [];
            res.on('data', (chunk) => {
                chunks.push(chunk);
            });
            res.on('end', () => {
                const raw = Buffer.concat(chunks).toString('utf-8');
                if (res.statusCode === 429) {
                    reject(new Error('Rate limit exceeded. Please wait 30 seconds before asking another question.'));
                    return;
                }
                if (res.statusCode !== 200) {
                    reject(new Error(`Server returned ${res.statusCode}: ${raw}`));
                    return;
                }
                try {
                    const parsed = JSON.parse(raw);
                    resolve(parsed);
                }
                catch {
                    reject(new Error('Failed to parse server response.'));
                }
            });
        });
        req.on('error', (err) => {
            reject(new Error(`Cannot reach CodeForge server at ${serverUrl}. ${err.message}`));
        });
        req.write(body);
        req.end();
    });
}
//# sourceMappingURL=apiClient.js.map