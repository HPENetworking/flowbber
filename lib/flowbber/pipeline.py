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
Base class for Flowbber pipeline.

"""

from copy import deepcopy
from logging import getLogger
from collections import OrderedDict
from multiprocessing import Process

from .loaders import SourcesLoader, AggregatorsLoader, SinksLoader


log = getLogger(__name__)


class Pipeline:
    """
    FIXME: Document.
    """

    def __init__(self, pipeline):
        super().__init__()

        self._pipeline = pipeline
        self._data = OrderedDict()

        self._load_plugins()
        self._build_pipeline()

    def _load_plugins(self):
        """
        FIXME: Document.
        """

        for entity, loader_clss in (
            ('source', SourcesLoader),
            ('aggregator', AggregatorsLoader),
            ('sink', SinksLoader),
        ):
            loader = loader_clss()
            available = loader.load_plugins()

            setattr(self, '_{}s_loader'.format(entity), loader)
            setattr(self, '_{}s_available'.format(entity), available)

            log.info('{}s available: {}'.format(
                entity.capitalize(),
                list(available.keys()))
            )

    def _build_pipeline(self):
        """
        FIXME: Document.
        """

        for entity_name, arg_unpacker in (
            ('source', lambda entity: (
                entity['type'],
                entity['key'],
                entity['config']
            )),
            ('aggregator', lambda entity: (
                entity['type'],
                entity['key'],
                entity['config']
            )),
            ('sink', lambda entity: (
                entity['type'],
                entity['config']
            )),
        ):
            destination = []

            available = getattr(self, '_{}s_available'.format(entity_name))

            for entity in self._pipeline['{}s'.format(entity_name)]:
                entity_type = entity['type']

                if entity_type not in available:
                    raise ValueError('Unknown {} {}'.format(
                        entity_name, entity_type
                    ))

                clss = available[entity_type]
                instance = clss(*arg_unpacker(entity))

                destination.append(instance)

                log.info('Created {} instance of type {}'.format(
                    entity_name, instance
                ))

            log.debug('Pipeline {}s created {}'.format(
                entity_name, destination
            ))

            setattr(self, '_{}s'.format(entity_name), destination)

    def run(self):
        """
        FIXME: Document.
        """

        journal = OrderedDict((
            ('sources', []),
            ('aggregators', []),
            ('sinks', []),
        ))

        self._run_sources(journal['sources'])
        self._run_aggregators(journal['aggregators'])
        self._run_sinks(journal['sinks'])

    def _run_sources(self, journal):
        """
        FIXME: Document.
        """

        sources_processes = [
            (Process(target=source.execute), source)
            for source in self._sources
        ]

        for index, (process, source) in enumerate(sources_processes):
            log.info(
                'Starting source #{} of type {}'.format(
                    index, source
                )
            )
            process.start()

        for index, (process, source) in enumerate(sources_processes):
            log.info(
                'Collecting {} data from source #{} of type {}'.format(
                    source.key, index, source
                )
            )
            result = source.result.get()
            self._data.update(result)

        for index, (process, source) in enumerate(sources_processes):
            process.join()

            journal_entry = {
                'key': source.key,
                'pid': process.pid,
                'exitcode': process.exitcode,
                'duration': source.duration.get(),
            }
            journal.append(journal_entry)

            log.debug('Process {} exited with {}'.format(
                process.pid, process.exitcode
            ))
            if process.exitcode != 0:
                raise RuntimeError(
                    'Process PID {pid} for source #{index} of type {source} '
                    'crashed with exit code {exitcode}'.format(
                        index=index, source=source, **journal_entry
                    )
                )

            log.info(
                'Source {source} finished collecting data successfully after '
                '{duration:.4f} seconds'.format(
                    source=source, **journal_entry
                )
            )

    def _run_aggregators(self, journal):
        """
        FIXME: Document.
        """

        for index, aggregator in enumerate(self._aggregators):
            log.info('Executing data aggregator #{} of type {}'.format(
                index, aggregator
            ))
            aggregator.accumulate(self._data)

    def _run_sinks(self, journal):
        """
        FIXME: Document.
        """

        for index, sink in enumerate(self._sinks):
            log.info('Executing data sink #{} of type {}'.format(
                index, sink
            ))
            sink.distribute(deepcopy(self._data))


__all__ = ['Pipeline']