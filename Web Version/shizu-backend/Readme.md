# Shizu Web Backend

This is the backend node server for the web version of this program. Currently supercedes the python version in functionality and is meant to replace it going forward.

## Setup

Run `npm install`, make sure to have ffprobe in your environment path. See the hacking section if your install directory contains spaces.

## Running the server

Run `npm run build` and then `npm run start`, the server will monitor port 4000 for graphql requests.

## Hacking

node-file-dialog may require some tweaking to work on paths that have spaces on them (at least)
To fix issues with this, change ``const root = '"' + __dirname;`` and ``cmd = path.join(cmd, 'windows', filename + '.exe') + '"'``