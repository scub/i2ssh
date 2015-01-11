#!/usr/bin/env python
import os
import logging
import sys
import subprocess
import tempfile

# iTerm2 AppleScript adapted from
# https://github.com/luismartingil/per.scripts/blob/master/iterm_launcher02.applescript
# Author: Luis Martin Gil
# Website: http://www.luismartingil.com/

pane_template = '    set panes to panes & {{cmd:"%s", name:"%s"}}'

layout_template = '''
        -- layout %s
        set layout to {"%s"}
        repeat with currentLayout in items of layout
            tell i term application "System Events" to keystroke currentLayout using command down
        end repeat
'''

code_template = '''
tell application "iTerm"
    set panes to {}
%s
    set myterm to (make new terminal)
    tell myterm
        launch session 1
        %s
        repeat with currentPane in items of panes
            delay 1
            tell the current session
                set name to name of currentPane
                write text cmd of currentPane
                tell i term application "System Events" to keystroke "]" using command down
            end tell
        end repeat
    end tell
end tell
'''

DEFAULT_CMD = 'ssh'

def pane_snippet(cmd=None, name="Default"):
    return pane_template % (cmd, name)

def layout_snippet(layout):
    cols = layout.cols
    rows = layout.rows

    splits = []
    for i in range(0, cols):
        if i < cols-1:
            splits.append('d')
            splits.append('[')
        for j in range(0, rows-1):
            splits.append('D')
        splits.append(']')

    return layout_template % (layout, '","'.join(splits))

def launch(layout, config):
    hosts = config['hosts']
    cmd = config.get('cmd', DEFAULT_CMD)

    # Construct the applescript
    panes = [pane_snippet(cmd, hostname) for hostname in hosts]
    layout = layout_snippet(layout)
    body = code_template % ('\n'.join(panes), layout)

    # Write it to a temporary file
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(body)
    temp.close()
    logging.debug('Applescript at %s: %s', temp.name, body)

    subprocess.call('osascript %s' % temp.name, shell=True)
    os.unlink(temp.name)

