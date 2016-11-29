# Copyright (c) 2012 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import os.path

def bool_from_string(value):
    value = value.lower()
    if value in ['t', 'true', '1', 'yes', 'on', 'enabled']:
        return True
    if value in ['f', 'false', '0', 'no', 'off', 'disabled']:
        return False
    raise ValueError('Unable to convert "%s" to boolean' % value)

figlet_yes_or_no = '''\
__   _______ ____      _   _  ___ ___
\\ \\ / / ____/ ___|    | \\ | |/ _ \\__ \\
 \\ V /|  _| \\___ \\    |  \\| | | | |/ /
  | | | |___ ___) |   | |\\  | |_| |_|
  |_| |_____|____/ or |_| \\_|\\___/(_) '''

def ask(prompt):
    return raw_input('{} '.format(prompt)).strip().lower()

def are_you_sure():
    prompts = ['yes or no?', 'Yes or No?', 'YES or NO?', figlet_yes_or_no]
    times = 0
    answer = ask(prompts[times])
    while answer != 'yes' and answer != 'no':
        times += 1
        answer = ask(prompts[min(times, len(prompts) - 1)])
    return answer == 'yes'

# Join two paths, force basename to be relative
def path_join(dirname, basename):
    if basename.startswith('/'):
        basename = basename[1:]
    return '{}/{}'.format(dirname, basename)

# Emulate UNIX basename behavior: basename('/foo/bar/') => 'bar'
def unix_path_split(path):
    dirname, basename = os.path.split(path)
    if not basename:
        dirname, basename = os.path.split(dirname)
    return (dirname, basename)

def parse_ascii(string, string_type):
    result = ''
    try:
        # str() throws an exception if there are non-ASCII characters.
        # But first 'cast' it as unicode so the escaped characters are detected
        # as such.
        result = str(unicode(string))
    except UnicodeEncodeError:
        # Output a more descriptive error, the unicode chars are being replaced
        # by '?'.
        msg = 'The string "%s" for the %s contains invalid characters'
        raise ValueError(msg % (string.encode('ascii', 'replace'), string_type))
    return result
