#!flask/bin/python
from flask import Flask, request, abort, send_file
from flask_cors import CORS
import subprocess
import urllib
import os
import errno
import io

app = Flask(__name__)
support_compiler = {'g++': '.cpp', 'gcc': '.c'}
# TODO: Change this is server musl bin
compiler_bin_dir = '/home/alpaca/Documents/or1k-linux-musl/bin/'
compiler_prefix = 'or1k-linux-musl-'
cache_dir = './cache'

CORS(app)

@app.route('/')
def index():
    return "To user or1k compiler Post to /compile/api/v1/compile endpoint with `compiler` url parameter."

@app.route('/compile/api/v1/compile', methods=['POST'])
#@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def compile_task():
    if request.headers['Content-Type'] == None or request.headers['Accept'] == None or request.headers['Content-Type'] != 'text/plain' or request.headers['Accept'] != 'application/octet-stream':
        abort(415)

    # prepare compiler
    compiler = urllib.unquote(request.args.get('compiler'))
    if compiler == None or compiler not in support_compiler:
        abort(400, 'Unsupported compiler')
    compile_command = compiler_bin_dir + compiler_prefix + compiler

    #write body to file
    source_fname = 'source_file' + support_compiler[compiler]
    complete_fname = cache_dir + '/' + source_fname
    if not os.path.exists(os.path.dirname(complete_fname)):
        try:
            os.makedirs(os.path.dirname(complete_fname))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                abort(500)
    with open(complete_fname, 'wb') as source_file:
        try:
            source_file.write(request.data)
        except Exception:
            abort(500)

    #compile and send
    process = subprocess.Popen([compile_command, '-o', 'compiled.out', complete_fname], stderr=subprocess.PIPE)
    out = process.stderr.read()
    print 'out: ', out
    if out != '':
        abort(400,'Compile error: ' + out.decode('utf-8'))
    with open('compiled.out', 'rb') as bites:
        return send_file(io.BytesIO(bites.read()), attachment_filename='a.out', mimetype='application/octet-stream')
# TODO: clean up cache

if __name__ == '__main__':
    app.run(host='0.0.0.0')
