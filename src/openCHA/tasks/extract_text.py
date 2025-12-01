import io
from typing import Any
from typing import List
from urllib.parse import urlparse

import requests
from openCHA.tasks import BaseTask
from pydantic import model_validator
from playwright.sync_api import Error as PlaywrightError


class ExtractText(BaseTask):
    """
    **Description:**

        This task extracts all the text from the current webpage.
    """

    name: str = "extract_text"
    chat_name: str = "ExtractText"
    description: str = "Extract all the text on the current webpage"
    dependencies: List[str] = []
    inputs: List[str] = [
        "url to extract the text from. It requires links which is gathered from other tools. Never provide urls on your own."
    ]
    outputs: List[str] = [
        "An string containing the text of the scraped webpage."
    ]
    output_type: bool = False
    sync_playwright: Any = None
    high_level: Any = None
    bs4: Any = None

    @model_validator(mode="before")
    def check_acheck_bs_importrgs(cls, values: dict) -> dict:
        """
            Check that the arguments are valid.

        Args:
            values (Dict): The current attribute values.
        Return:
            Dict: The updated attribute values.
        Raise:
            ImportError: If 'beautifulsoup4', 'lxml', or 'pdfminer' packages are not installed.

        """

        try:
            from bs4 import BeautifulSoup  # noqa: F401

            values["bs4"] = BeautifulSoup
        except ImportError:
            raise ImportError(
                "The 'beautifulsoup4' package is required to use this tool."
                " Please install it with 'pip install beautifulsoup4'."
            )

        try:
            import lxml  # noqa: F401
        except ImportError:
            raise ImportError(
                "The 'lxml' package is required to use this tool."
                " Please install it with 'pip install lxml'."
            )

        try:
            from pdfminer import high_level  # noqa: F401

            values["high_level"] = high_level
        except ImportError:
            raise ImportError(
                "The 'pdfminer' package is required to use this tool."
                " Please install it with 'pip install pdfminer.six'."
            )

        try:
            from playwright.sync_api import sync_playwright

            values["sync_playwright"] = sync_playwright

        except ImportError:
            raise ImportError(
                "The 'playwright' package is required to use this tool."
                " Please install it with 'pip install playwright'."
            )
        return values

    def validate_url(self, url):
        """
            This method validates a given URL by checking if its scheme is either 'http' or 'https'.

        Args:
            url (str): The URL to be validated.
        Return:
            str: The validated URL.
        Raise:
            ValueError: If the URL scheme is not 'http' or 'https'.


        """

        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            raise ValueError("URL scheme must be 'http' or 'https'")
        return url

    def _execute(
        self,
        inputs: List[Any],
    ) -> str:
        """
        Execute the ExtractText task.

        Args:
            inputs (List[Any]): The first item is either a dict with 'url' or a url string.
        Return:
            str: Extracted text from the target resource (HTML or PDF).
        Raise:
            ValueError: If the URL is invalid.
        """
        url = inputs[0]['url'] if isinstance(inputs[0], dict) and 'url' in inputs[0] else inputs[0]
        url = url.strip()
        self.validate_url(url)

        # ---------- helpers ----------
        def looks_like_pdf_via_headers(u: str) -> bool:
            try:
                r = requests.head(u, allow_redirects=True, timeout=12)
                ct = (r.headers.get("Content-Type") or "").lower()
                if "pdf" in ct:
                    return True
                cd = (r.headers.get("Content-Disposition") or "").lower()
                # e.g., attachment; filename="something.pdf"
                return (".pdf" in cd)
            except Exception:
                return False

        def looks_like_pdf_via_sniff(u: str) -> bool:
            try:
                with requests.get(u, stream=True, timeout=15) as r:
                    r.raise_for_status()
                    first4 = next(r.iter_content(4), b"")
                    return first4 == b"%PDF"
            except Exception:
                return False

        def fetch_pdf_bytes(u: str) -> bytes | None:
            r = requests.get(u, allow_redirects=True, timeout=60)
            if r.status_code == 200:
                return r.content
            return None

        def extract_pdf_text(pdf_bytes: bytes) -> str:
            pdf_stream = io.BytesIO(pdf_bytes)
            text = self.high_level.extract_text(pdf_stream)
            # Normalize via HTML→BS4 (keeps behavior consistent with HTML path)
            html_content = f"<html><body><p>{text}</p></body></html>"
            soup = self.bs4(html_content, "lxml")
            return " ".join(s for s in soup.stripped_strings)

        # ---------- decide PDF vs webpage ----------
        is_pdf = looks_like_pdf_via_headers(url)
        if not is_pdf:
            # fallback sniff (handles servers that don't implement HEAD properly)
            is_pdf = looks_like_pdf_via_sniff(url)

        if is_pdf:
            pdf_bytes = fetch_pdf_bytes(url)
            if not pdf_bytes:
                return "Error extracting text. The url might be unreachable or blocked."
            try:
                return extract_pdf_text(pdf_bytes)
            except Exception:
                return "Error extracting text from PDF content."
        else:
            # HTML route via Playwright; avoid goto on download endpoints
            try:
                with self.sync_playwright() as playwright:
                    browser = playwright.chromium.launch()
                    context = browser.new_context(accept_downloads=True)
                    page = context.new_page()

                    # Try standard navigation
                    response = page.goto(url, wait_until="load")
                    status = response.status if response else None

                    if status == 200:
                        html_content = page.content()
                        soup = self.bs4(html_content, "lxml")
                        page.close()
                        context.close()
                        browser.close()
                        return " ".join(s for s in soup.stripped_strings)

                    # Non-200 but no exception: treat as error
                    page.close()
                    context.close()
                    browser.close()
                    return "Error extracting text. The url did not return 200."

            except PlaywrightError as e:
                # If navigation actually triggered a download, handle gracefully
                msg = str(e).lower()
                if "download is starting" in msg:
                    # Use Playwright's download flow to capture the file, then try PDF extraction.
                    with self.sync_playwright() as playwright:
                        browser = playwright.chromium.launch()
                        context = browser.new_context(accept_downloads=True)
                        page = context.new_page()
                        try:
                            with page.expect_download():
                                # Trigger via JS assignment to avoid goto()
                                page.evaluate("url => window.location.href = url", url)
                            download = page.wait_for_event("download", timeout=15000)
                            suggested = download.suggested_filename or "download.bin"
                            # Save to a temp path
                            suffix = "." + suggested.split(".")[-1].lower() if "." in suggested else ""
                            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                                download.save_as(tmp.name)
                                # Try to read and treat as PDF if possible
                                try:
                                    with open(tmp.name, "rb") as f:
                                        data = f.read(8)
                                        if data.startswith(b"%PDF"):
                                            f.seek(0)
                                            return extract_pdf_text(f.read())
                                        else:
                                            return "Downloaded file is not HTML and not a PDF I can parse."
                                except Exception:
                                    return "Downloaded file could not be processed."
                        except Exception:
                            return "A file download was initiated by the URL, and it couldn't be captured."
                        finally:
                            page.close()
                            context.close()
                            browser.close()
                # Other Playwright errors
                return f"Playwright error during navigation: {e}"

    def explain(
        self,
    ) -> str:
        """
            Explain the ExtractText task.

        Return:
            str: A brief explanation of the ExtractText task.


        """

        return "This task returns the ulr of the current page."
