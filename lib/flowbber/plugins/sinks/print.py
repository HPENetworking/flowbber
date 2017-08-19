# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 KuraLabs S.R.L
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

Print
=====

Simple print sink plugin.

This module uses third party pprintpp for better pretty printing of large data
structures.

FIXME: Document.
"""

from flowbber.entities import Sink


class PrintSink(Sink):
    def distribute(self, data):
        from pprintpp import pprint
        pprint(data)


__all__ = ['PrintSink']