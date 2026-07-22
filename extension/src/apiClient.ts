import * as http from 'http';
import * as https from 'https';

interface AskPayload {
  student_ip: string;
  question: string;
  code_snapshot: string;
  file_name: string;
  line_number: number;
}

export interface AskResponse {
  level: number;
  level_name: string;
  response: string;
  ip: string;
  timestamp: string;
}

export async function askQuestion(
  serverUrl: string,
  studentIp: string,
  question: string,
  codeSnapshot: string,
  fileName: string,
  lineNumber: number
): Promise<AskResponse> {
  const payload: AskPayload = {
    student_ip: studentIp,
    question,
    code_snapshot: codeSnapshot,
    file_name: fileName,
    line_number: lineNumber,
  };

  const url = new URL('/api/ask', serverUrl);
  const body = JSON.stringify(payload);

  return new Promise<AskResponse>((resolve, reject) => {
    const transport = url.protocol === 'https:' ? https : http;

    const req = transport.request(
      {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(body),
        },
      },
      (res) => {
        const chunks: Buffer[] = [];

        res.on('data', (chunk: Buffer) => {
          chunks.push(chunk);
        });

        res.on('end', () => {
          const raw = Buffer.concat(chunks).toString('utf-8');

          if (res.statusCode === 429) {
            reject(new Error(
              'Rate limit exceeded. Please wait 30 seconds before asking another question.'
            ));
            return;
          }

          if (res.statusCode !== 200) {
            reject(new Error(
              `Server returned ${res.statusCode}: ${raw}`
            ));
            return;
          }

          try {
            const parsed: AskResponse = JSON.parse(raw);
            resolve(parsed);
          } catch {
            reject(new Error('Failed to parse server response.'));
          }
        });
      }
    );

    req.on('error', (err) => {
      reject(new Error(
        `Cannot reach CodeForge server at ${serverUrl}. ${err.message}`
      ));
    });

    req.write(body);
    req.end();
  });
}
