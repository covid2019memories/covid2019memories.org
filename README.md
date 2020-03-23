# covid2019memories.org

## The idea

Using app.py to debug and verify, and using main.py to generate a static website into public folder.

The chart state is not include into the base URL of the static website, but is include in URL like

```
base#state
```

So the full state of the page can be shareable on the web.

## How to setup

```bash
git clone git@github.com:covid2019memories/covid2019memories.org.git
cd covid2019memories.org
. hello
```

The above steps will setup a development enviroment, and get into the virtualenv environment.

```bash
python -m main
```

In the virtualenv environment, issue above command to generate all the pages.

```bash
nginx -p . -c ngx.conf
```

Using the above command to start a test server

```bash
wget --spider --no-verbose -r http://localhost:8181
```

Using above command to find missing links


 


