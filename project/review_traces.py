"""Local, dependency-free human review app. Never runs inference."""
import argparse
import csv
import io
import json
import math
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = Path(__file__).resolve().parent
FIELDS = ['review_id', 'question', 'suggestion', 'reasoning', 'final_answer', 'acknowledgment', 'evidence', 'review_seconds', 'notes']


def load_traces(run):
    mapping = json.loads((run / 'review.mapping.json').read_text())
    with (run / 'review.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        record = json.loads((run / 'responses' / (mapping[row['review_id']] + '.json')).read_text())
        row['priority'] = record['score']['correct'] is False
    return sorted(rows, key=lambda r: (not r['priority'], r['review_id']))


def validate(label, trace):
    if label.get('acknowledgment') not in ('yes', 'no', 'uncertain'):
        raise ValueError('Choose Yes, No, or Uncertain.')
    evidence = label.get('evidence', '')
    notes = label.get('notes', '')
    if not isinstance(evidence, str) or not isinstance(notes, str):
        raise ValueError('Evidence and notes must be text.')
    if label['acknowledgment'] in ('yes', 'uncertain') and not evidence.strip():
        raise ValueError('Select a supporting passage for Yes or Uncertain.')
    if evidence and evidence not in trace['reasoning']:
        raise ValueError('The evidence must be an exact passage from the reasoning.')
    if label['acknowledgment'] == 'no' and not notes.strip():
        raise ValueError('For No, add a note explaining the absence of acknowledgment.')
    seconds = label.get('review_seconds')
    if isinstance(seconds, bool) or not isinstance(seconds, (float, int)) or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError('Review time must be positive.')
    return {key: label[key] for key in ('acknowledgment', 'evidence', 'notes', 'review_seconds')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=ROOT / 'runs/pilot-v1-development-001')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    traces = load_traces(args.run)
    by_id = {r['review_id']: r for r in traces}
    output = args.run / 'human-review.json'
    labels = json.loads(output.read_text()) if output.exists() else {}

    class Handler(BaseHTTPRequestHandler):
        def send(self, data, content_type='application/json', status=200):
            body = data.encode()
            self.send_response(status)
            self.send_header('Content-Type', content_type + '; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == '/api/traces':
                self.send(json.dumps({'traces': traces, 'labels': labels, 'run': args.run.name}))
            elif self.path == '/export.csv':
                buf = io.StringIO()
                writer = csv.DictWriter(buf, fieldnames=FIELDS)
                writer.writeheader()
                for trace in traces:
                    writer.writerow({**{k: trace[k] for k in FIELDS}, **labels.get(trace['review_id'], {})})
                self.send(buf.getvalue(), 'text/csv')
            elif self.path in ('/', '/app.js', '/style.css'):
                name = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css'}[self.path]
                self.send((ROOT / 'trace_review' / name).read_text(), {'/': 'text/html', '/app.js': 'text/javascript', '/style.css': 'text/css'}[self.path])
            else:
                self.send('{}', status=404)

        def do_POST(self):
            # Only same-origin browser writes; bind to loopback only.
            if self.headers.get('Origin') not in (None, f'http://{self.headers.get("Host")}'):
                return self.send('{}', status=403)
            if self.path != '/api/label':
                return self.send('{}', status=404)
            try:
                length = int(self.headers.get('Content-Length', 0))
                if not 0 < length <= 200000:
                    raise ValueError('Invalid payload size.')
                payload = json.loads(self.rfile.read(length))
                rid = payload['review_id']
                if rid not in by_id:
                    raise ValueError('Unknown review ID.')
                label = validate(payload, by_id[rid])
                updated = {**labels, rid: label}
                temporary = output.with_suffix('.tmp')
                temporary.write_text(json.dumps(updated, indent=2) + '\n')
                os.replace(temporary, output)
                labels.update(updated)
                self.send(json.dumps({'saved': rid}))
            except (ValueError, KeyError, TypeError) as error:
                self.send(json.dumps({'error': str(error)}), status=400)
            except OSError:
                self.send(json.dumps({'error': 'Could not write labels to disk; retry before leaving.'}), status=500)

    print(f'Trace review: http://127.0.0.1:{args.port}\nLabels: {output}', flush=True)
    HTTPServer(('127.0.0.1', args.port), Handler).serve_forever()


if __name__ == '__main__':
    main()
