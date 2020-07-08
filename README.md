scihub-client
=========

scihub-client is a python client for Sci-hub. scihub-client was developed with inspiration from https://github.com/zaytoun/scihub.py

If you believe in open access to scientific papers, please donate to Sci-Hub.

### download

```
In [1]: from scihub import scihub
   ...: import logging
   ...: logging.basicConfig()
   ...: scihub_client = scihub.SciHubClient()

# download works w/ the doi, pubmed number, doi link, anything that the scihub site can search for
In [2]: scihub_client.download('30462157')
Out[2]:
{'out_path': '(2020) Dating admixture events is unsolved problem in multi-way admixed populations.pdf',
 'doi': '10.1093/bib/bby112',
 'pdf_url': 'https://dacemirror.sci-hub.st/journal-article/6b9ae0994bbbb2237d89e53c004cd873/oup-accepted-manuscript-2018.pdf'}
```

### search

```
In [1]: from scihub import scihub
   ...: import logging
   ...: logging.basicConfig()
   ...: scihub_client = scihub.SciHubClient()

# search works w/ the doi, pubmed number, doi link, anything that the scihub site can search for
In [2]: scihub_client.query('30462157')
Out[2]:
{'doi': '10.1093/bib/bby112',
 'pdf_url': 'https://dacemirror.sci-hub.st/journal-article/6b9ae0994bbbb2237d89e53c004cd873/oup-accepted-manuscript-2018.pdf'}

# Not very good at handling errors yet
In [4]: scihub_client.query('462157')
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
<ipython-input-4-74ac2edd4f28> in <module>
----> 1 scihub_client.query('462157')

scihub.py in query(self, query)
    115         )
    116         parsed_response = BeautifulSoup(response.content, "html.parser")
--> 117         if parsed_response.find("div").text.endswith("article not found"):
    118             raise ValueError(f"Article not found: {query}")
    119

AttributeError: 'NoneType' object has no attribute 'text'
```
