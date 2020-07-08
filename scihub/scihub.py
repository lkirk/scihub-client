# -*- coding: utf-8 -*-

"""
SciHub client
"""


import logging
import os
import random
import urllib

import requests

from bs4 import BeautifulSoup

LOG = logging.getLogger(__name__)
LOG.addHandler(logging.NullHandler())


class SciHubClient:
    """
    Client for accessing SciHub
    """

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0",
    }
    SCIHUB_NOW_URL = "https://sci-hub.now.sh"
    FALLBACK_BASE_URL = "https://sci-hub.tw"

    def __init__(self, proxy=None, fallback_base_url=FALLBACK_BASE_URL):
        self._sess = requests.Session()
        self._sess.headers.update(self.DEFAULT_HEADERS)

        self._fallback_base_url = fallback_base_url
        self._available_base_url_list = self._get_available_scihub_urls()
        self._set_base_url()

        if proxy is not None:
            self._set_proxy(proxy)

    def _get(self, url, raise_for_status=True, **kwargs):
        response = self._sess.get(url, **kwargs)
        if raise_for_status is True:
            response.raise_for_status()
        return response

    def _post(self, url, raise_for_status=True, **kwargs):
        response = self._sess.post(url, **kwargs)
        if raise_for_status is True:
            response.raise_for_status()
        return response

    def _get_available_scihub_urls(self):
        response = self._get(self.SCIHUB_NOW_URL, raise_for_status=False)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            LOG.debug("falling back to %s", self._fallback_base_url)
            return [self._fallback_base_url]

        parsed_content = BeautifulSoup(response.content, "html.parser")
        urls = []
        for a_tag in parsed_content.find_all("a", href=True):
            link = a_tag["href"]
            if (
                "sci-hub" in link  # pylint: disable=C0330
                and link.startswith("https")  # pylint: disable=C0330
                and link != self.SCIHUB_NOW_URL  # pylint: disable=C0330
            ):
                urls.append(a_tag["href"])

        return urls

    def _set_proxy(self, proxy):
        self._sess.proxies = {
            "http": proxy,
            "https": proxy,
        }

    def _set_base_url(self):
        """
        Pick a random url from the available scihub urls
        set the current base url to the new url
        """
        if not self._available_base_url_list:
            raise ValueError("Ran out of valid sci-hub urls")

        (base_url,) = random.sample(self._get_available_scihub_urls(), 1)
        self._base_url = base_url
        LOG.debug("url changing to %s", self._base_url)

    @staticmethod
    def _get_doi(parsed_response):
        ((doi,),) = [
            [
                line.strip().split("'")[1]
                for line in script.string.split("\n")
                if "var doi" in line
            ]
            for script in parsed_response.find_all("script")
            if script.string and "var doi" in script.string
        ]
        return doi

    def query(self, query):
        """
        Query for a paper hosted by sci-hub
        """
        response = self._post(
            self._base_url,
            data={"request": query},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        parsed_response = BeautifulSoup(response.content, "html.parser")
        if parsed_response.find("div").text.endswith("article not found"):
            raise ValueError(f"Article not found: {query}")

        cleaned_url = urllib.parse.urlparse(
            urllib.parse.urldefrag(parsed_response.find("iframe").get("src")).url,
            scheme="https",
        ).geturl()

        return {
            "doi": self._get_doi(parsed_response),
            "pdf_url": cleaned_url,
        }

    def _download_pdf(self, url):
        result = self._get(url)
        if result.headers["Content-Type"] != "application/pdf":
            raise ValueError("File is not a pdf")
        return result.content

    def _get_paper_meta(self, doi):
        return self._get(
            urllib.parse.urljoin("https://doi.org", doi),
            headers={"Accept": "application/vnd.citationstyles.csl+json"},
        ).json()

    def _generate_file_name(self, doi):
        paper_meta = self._get_paper_meta(doi)
        # date = "-".join(map(str, paper_meta["indexed"]["date-parts"][0]))
        ((year, _, _),) = paper_meta["indexed"]["date-parts"]
        title = paper_meta["title"]
        # return f"({date}) {title}.pdf"
        return f"({year}) {title}.pdf"

    def download(self, query, destination="", filename=None):
        """
        Download paper from sci-hub
        """
        query_result = self.query(query)
        pdf_string = self._download_pdf(query_result["pdf_url"])
        filename = (
            self._generate_file_name(query_result["doi"])
            if filename is None
            else filename
        )

        out_path = os.path.join(destination, filename)

        with open(out_path, "wb") as out_fp:
            out_fp.write(pdf_string)

        return {"out_path": out_path, **query_result}
