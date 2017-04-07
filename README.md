# Word2vec as an HTTP service

## What

This repo contains the backend code (server) for our interactive word2vec demo running at https://rare-technologies.com/word2vec-tutorial/#bonus_app. Our web demo uses the [3,000,000 x 300 GoogleNews word2vec model](https://code.google.com/archive/p/word2vec/) trained by Google over 100 billion words, but you can plug in any model you like.

<img src="https://raw.githubusercontent.com/piskvorky/w2v_server_googlenews/master/frontend_screenshot.png" width="400">

## How

The service uses [CherryPy](http://cherrypy.org/) for a fast and minimalist Python web framework and [gensim](https://github.com/RaRe-Technologies/gensim) for the actual heavy lifting. Run with `python runserver.py hetzner.conf`, after installing dependencies `pip install -r requirements.txt`.

For the frontend part of this demo (Javascript, AJAX, phrase suggestions as you type), see source code at the link above in your browser. For more information, read the [tutorial post](https://rare-technologies.com/word2vec-tutorial) itself.

Examples of queries & JSON responses:

```bash
# king - man + woman = ?
curl 'http://127.0.0.1/most_similar?positive%5B%5D=woman&positive%5B%5D=king&negative%5B%5D=man'
{"taken": 0.19543004035949707, "similars": [["queen", 0.7118192911148071], ["monarch", 0.6189674139022827], ["princess", 0.5902431011199951], ["crown_prince", 0.5499460697174072], ["prince", 0.5377321243286133]], "success": 1}

# phrase completion (for the "suggest as you type" demo functionality)
curl 'http://127.0.0.1/suggest?term=iPhon'
["iPhone", "iphone", "IPhone", "Iphone", "IPHONE", "iPHONE", "iPHone", "iPhone.com", "iphone.org", "iPhone.org"]

# most similar phrase?
curl 'http://127.0.0.1/most_similar?positive%5B%5D=PHP'
{"taken": 0.24541091918945312, "similars": [["ASP.NET", 0.7275794744491577], ["scripting_languages", 0.7123507857322693], ["PHP5", 0.706219494342804], ["Joomla", 0.700035572052002], ["ASP.Net", 0.6955472230911255]], "success": 1}

# which phrase doesn't fit?
curl 'http://127.0.0.1/most_dissimilar?words%5B%5D=dinner+cereal+breakfast+lunch'
{"taken": 0.0007932186126708984, "dissimilar": "cereal", "success": 1}
```

## Why

On [our gensim mailing list](https://groups.google.com/forum/#!forum/gensim), we've seen repeated questions about how the demo works. It's no rocket science, but we understand the engineering side of wrapping machine learning models, using JSON requests, handling exceptions, logging, dropping user privileges etc can be tricky and confusing if you've never done it before.

We publish this repo in hopes you find it useful, as a blueprint for your own (perhaps non-word2vec) ML service demos.

(c) 2014, [rare-technologies.com](https://rare-technologies.com)
