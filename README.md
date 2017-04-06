Word2vec as an HTTP service
===========================

This repo contains the backend code (server) for our interactive word2vec demo running at https://rare-technologies.com/word2vec-tutorial/#bonus_app. The demo uses the [3,000,000 x 300 GoogleNews word2vec model](https://code.google.com/archive/p/word2vec/) trained by Google over 100 billion words.

<img src="https://raw.githubusercontent.com/piskvorky/w2v_server_googlenews/master/frontend_screenshot.png" width="400">

The service uses [CherryPy](http://cherrypy.org/) for a fast and minimalist Python web framework and [gensim](https://github.com/RaRe-Technologies/gensim) for the actual heavy lifting.

For the frontend part of this demo (Javascript/HTML/CSS), see source code at the link above in your browser. For more information, read the tutorial post itself.

(c) 2014, rare-technologies.com
