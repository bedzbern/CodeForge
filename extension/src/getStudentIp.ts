import * as os from 'os';

export function getStudentIp(): string {
  const interfaces = os.networkInterfaces();

  for (const name of Object.keys(interfaces)) {
    const addrs = interfaces[name];
    if (!addrs) { continue; }

    for (const addr of addrs) {
      if (
        addr.family === 'IPv4' &&
        !addr.internal &&
        addr.address.startsWith('192.168.1.')
      ) {
        return addr.address;
      }
    }
  }

  for (const name of Object.keys(interfaces)) {
    const addrs = interfaces[name];
    if (!addrs) { continue; }

    for (const addr of addrs) {
      if (addr.family === 'IPv4' && !addr.internal) {
        return addr.address;
      }
    }
  }

  return '0.0.0.0';
}
