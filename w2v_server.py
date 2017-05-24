#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Radim Rehurek <me@radimrehurek.com>

"""
USAGE: %(program)s CONFIG

Example:
    ./w2v_server.py w2v_hetzner.conf

"""

from __future__ import with_statement

import os
import sys
from functools import wraps
import time
import logging
import bisect

import cherrypy
from cherrypy.process.plugins import DropPrivileges, PIDFile
import gensim


logger = logging.getLogger(__name__)


def server_exception_wrap(func):
    """
    Method decorator to return nicer JSON responses: handle internal server errors & report request timings.

    """
    @wraps(func)
    def _wrapper(self, *args, **kwargs):
        try:
            # append "success=1" and time taken in milliseconds to the response, on success
            logger.debug("calling server method '%s'" % (func.func_name))
            cherrypy.response.timeout = 3600 * 24 * 7  # [s]

            # include json data in kwargs; HACK: should be a separate decorator really, but whatever
            if getattr(cherrypy.request, 'json', None):
                kwargs.update(cherrypy.request.json)

            start = time.time()
            result = func(self, *args, **kwargs)
            if result is None:
                result = {}
            result['success'] = 1
            result['taken'] = time.time() - start
            logger.info("method '%s' succeeded in %ss" % (func.func_name, result['taken']))
            return result
        except Exception, e:
            logger.exception("exception serving request")
            result = {
                'error': repr(e),
                'success': 0,
            }
            cherrypy.response.status = 500
            return result
    return _wrapper


class Server(object):
    def __init__(self, fname):
        # load the word2vec model from gzipped file
        self.model = gensim.models.word2vec.Word2Vec.load_word2vec_format(fname, binary=True)
        self.model.init_sims(replace=True)
        try:
            del self.model.syn0  # not needed => free up mem
            del self.model.syn1
        except:
            pass

        # sort all the words in the model, so that we can auto-complete queries quickly
        self.orig_words = [gensim.utils.to_unicode(word) for word in self.model.index2word]
        indices = [i for i, _ in sorted(enumerate(self.orig_words), key=lambda item: item[1].lower())]
        self.all_words = [self.orig_words[i].lower() for i in indices]  # lowercased, sorted as lowercased
        self.orig_words = [self.orig_words[i] for i in indices]  # original letter casing, but sorted as if lowercased

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def suggest(self, *args, **kwargs):
        """
        For a given prefix, return 10 words that exist in the model start start with that prefix

        """
        prefix = gensim.utils.to_unicode(kwargs.pop('term', u'')).strip().lower()
        count = kwargs.pop('count', 10)
        pos = bisect.bisect_left(self.all_words, prefix)
        result = self.orig_words[pos: pos + count]
        logger.info("suggested %r: %s" % (prefix, result))
        return result

    @server_exception_wrap
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def most_similar(self, *args, **kwargs):
        positive = cherrypy.request.params.get('positive[]', [])
        if isinstance(positive, basestring):
            positive = [positive]
        negative = cherrypy.request.params.get('negative[]', [])
        if isinstance(negative, basestring):
            negative = [negative]
        try:
            result = self.model.most_similar(
                positive=[gensim.utils.to_utf8(word).strip() for word in positive if word],
                negative=[gensim.utils.to_utf8(word).strip() for word in negative if word],
                topn=5)
        except:
            result = []
        logger.info("similars for %s vs. %s: %s" % (positive, negative, result))
        return {'similars': result}

    @server_exception_wrap
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def most_dissimilar(self, *args, **kwargs):
        words = cherrypy.request.params.get('words[]', '').split()
        try:
            result = self.model.doesnt_match(words)
        except:
            result = ''
        logger.info("dissimilar for %s: %s" % (words, result))
        return {'dissimilar': result}

    @server_exception_wrap
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def status(self, *args, **kwargs):
        """
        Return the server status.

        """
        result = {
            'model': str(self.model),
        }
        return result
    ping = status


class Config(object):
    def __init__(self, **d):
        self.__dict__.update(d)

    def __getattr__(self, name):
        return None  # unset config values will default to None

    def __getitem__(self, name):
        return self.__dict__[name]


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s : %(levelname)s : %(module)s:%(lineno)d : %(funcName)s(%(threadName)s) : %(message)s',
        level=logging.DEBUG)
    logger.info("running %s", ' '.join(sys.argv))

    program = os.path.basename(sys.argv[0])

    # check and process input arguments
    if len(sys.argv) < 2:
        print globals()['__doc__'] % locals()
        sys.exit(1)

    conf_file = sys.argv[1]
    config_srv = Config(**cherrypy.lib.reprconf.Config(conf_file).get('global'))
    config = Config(**cherrypy.lib.reprconf.Config(conf_file).get('w2v_server'))

    if config_srv.pid_file:
        PIDFile(cherrypy.engine, config_srv.pid_file).subscribe()
    if config_srv.run_user and config_srv.run_group:
        logging.info("dropping priviledges to %s:%s" % (config_srv.run_user, config_srv.run_group))
        DropPrivileges(cherrypy.engine, gid=config_srv.run_group, uid=config_srv.run_user).subscribe()

    cherrypy.quickstart(Server(config.MODEL_FILE), config=conf_file)

    logger.info("finished running %s", program)
