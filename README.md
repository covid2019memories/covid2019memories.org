# covid2019memories.org

## The idea
app.py is for debugging and verifying, and main.py is for generating the static website.

The chart state is not include into the base URL of the static website, but is include in URL like

```
base#state
```

So the full state of the page can be shareable on the web.

## How to setup

```bash
git clone git@github.com:covid2019memories/covid2019memories.org.git
git clone git@github.com:covid2019memories/covid2019-memories.git
cd covid2019memories.org
. hello
```

The above steps will setup a development enviroment, and get into the virtualenv environment.


```bash
FLASK_APP=src/app.py python -m flask run
```

to run the development server

```bash
python -m main
```

to generate all the static pages.

```bash
nginx -p . -c ngx.conf
```

to start a test server

```bash
wget --spider --no-verbose -r http://localhost:8181
```

to find missing links


 


