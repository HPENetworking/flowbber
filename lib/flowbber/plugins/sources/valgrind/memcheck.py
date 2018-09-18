# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2018 KuraLabs S.R.L
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""

Valgrind Memcheck
=================

This source parses and collects information from the XML generated by
`Valgrind's Memcheck`_ tool.

.. _`Valgrind's Memcheck`: http://valgrind.org/docs/manual/mc-manual.html

Such XML file can be generated with:

.. code-block:: sh

    $ valgrind \\
        --tool=memcheck \\
        --xml=yes \\
        --xml-file=memcheck.xml \\
        --leak-check=full \\
        ./executable

**Data collected:**

.. code-block:: json

    {
        "status":[
            {
                "state":"RUNNING",
                "time":"00:00:00:00.268"
            },
            {
                "state":"FINISHED",
                "time":"00:00:00:59.394"
            }
        ],
        "ppid":"4242",
        "preamble":{
            "line":[
                "Memcheck, a memory error detector",
                "Copyright (C) 2002-2015, and GNU GPL'd, by Julian Seward et al.",
                "Using Valgrind-3.11.0 and LibVEX; rerun with -h for copyright info",
                "Command: ./binary"
            ]
        },
        "suppcounts":{
            "pair":[
                {
                    "name":"reachable memory from libstdc++ pool",
                    "count":"1"
                }
            ]
        },
        "pid":"424242",
        "errorcounts":null,
        "protocoltool":"memcheck",
        "protocolversion":"4",
        "tool":"memcheck",
        "error":[
            {
                "kind":"Leak_DefinitelyLost",
                "stack":{
                    "frame":[
                        {
                            "obj":"/usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so",
                            "ip":"0x4C2FB55",
                            "fn":"calloc"
                        },
                        {
                            "dir":"/home/library",
                            "obj":"/home/library/binary",
                            "line":"76",
                            "ip":"0xED467F",
                            "fn":"hello_world()",
                            "file":"hello.cpp"
                        },
                    ]
                },
                "xwhat":{
                    "leakedblocks":"1",
                    "text":"8 bytes in 1 blocks are definitely lost in loss record 1 of 5",
                    "leakedbytes":"8"
                },
                "tid":"1",
                "unique":"0x0"
            }
        ],
        "args":{
            "vargv":{
                "exe":"/usr/bin/valgrind.bin",
                "arg":[
                    "--track-origins=yes",
                    "--leak-check=full",
                    "--show-leak-kinds=all",
                    "--errors-for-leak-kinds=definite",
                    "--error-exitcode=1",
                    "--xml=yes",
                    "--xml-file=memcheck.xml",
                    "--suppressions=/home/library/suppressions.supp"
                ]
            },
            "argv":{
                "exe":"./binary",
                "arg":[]
            }
        }
    }


**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[valgrind_memcheck]

**Usage:**

.. code-block:: toml

    [[sources]]
    type = "valgrind_memcheck"
    id = "..."

        [sources.config]
        xmlpath = "memcheck.xml"

.. code-block:: json

    {
        "sources": [
            {
                "type": "valgrind_memcheck",
                "id": "...",
                "config": {
                    "xmlpath": "memcheck.xml"
                }
            }
        ]
    }

xmlpath
-------

Path to Valgrind's Memcheck XML output.

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

"""  # noqa

from pathlib import Path

from flowbber.components import Source


class ValgrindMemcheckSource(Source):

    def declare_config(self, config):
        config.add_option(
            'xmlpath',
            schema={
                'type': 'string',
                'empty': False,
            },
        )

    def collect(self):
        from xmltodict import parse

        # Check if file exists
        infile = Path(self.config.xmlpath.value)
        if not infile.is_file():
            raise FileNotFoundError(
                'No such file {}'.format(infile)
            )

        doc = parse(infile.read_text(), force_list=('error', 'stack',))
        return doc['valgrindoutput']


__all__ = ['ValgrindMemcheckSource']
