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
Module implementating Aggregator base class.

All custom Flowbber aggregators must extend from the Aggregator class.
"""

import logging

from ..entities import Aggregator
from .loader import PluginLoader


log = logging.getLogger(__name__)


class AggregatorsLoader(PluginLoader):
    """
    Aggregators plugins loader class.
    """

    def __init__(self):
        super().__init__('aggregators', Aggregator)


__all__ = ['AggregatorsLoader']