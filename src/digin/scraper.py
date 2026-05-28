import asyncio
import hashlib
import random
import re
import time
from pathlib import Path

from playwright.async_api import Page, async_playwright

from digin.config import Config
from digin.models import Post

BROWSER_DATA_DIR = str(Path("~/.digin/browser-data").expanduser())


async def scrape_saved_posts(config: Config, max_posts: int | None = None) -> list[Post]:
    async with async_playwright() as p:
        Path(BROWSER_DATA_DIR).mkdir(parents=True, exist_ok=True)

        context = await p.chromium.launch_persistent_context(
            BROWSER_DATA_DIR,
            headless=config.headless,
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )

        page = context.pages[0] if context.pages else await context.new_page()

        await page.goto("https://www.linkedin.com/my-items/saved-posts/")
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)

        if "/login" in page.url or "/checkpoint" in page.url:
            print(
                "Please log in to LinkedIn in the browser window.\n"
                "The tool will continue automatically once you're logged in."
            )
            if not await _wait_for_login(page):
                print("Timed out waiting for login. Exiting.")
                await context.close()
                return []

            if "/my-items/saved-posts" not in page.url:
                await page.goto("https://www.linkedin.com/my-items/saved-posts/")
                await page.wait_for_load_state("domcontentloaded")

        print("Loading saved posts...")
        await _wait_for_content(page)

        posts = await _scroll_and_extract(page, config, max_posts)
        await context.close()
        return posts


async def _wait_for_login(page: Page, timeout_seconds: int = 300) -> bool:
    start = time.time()
    while time.time() - start < timeout_seconds:
        url = page.url
        if "/login" not in url and "/checkpoint" not in url and "linkedin.com" in url:
            return True
        await asyncio.sleep(2)
    return False


async def _wait_for_content(page: Page, timeout_seconds: int = 30) -> bool:
    """Wait for LinkedIn's BIGPIPE to render actual post content."""
    start = time.time()
    while time.time() - start < timeout_seconds:
        count = await page.evaluate(
            "document.querySelectorAll('[data-chameleon-result-urn]').length"
        )
        if count > 0:
            await asyncio.sleep(1)  # Brief extra wait for full render
            return True
        await asyncio.sleep(1)
    return False


async def _scroll_and_extract(
    page: Page, config: Config, max_posts: int | None
) -> list[Post]:
    posts: list[Post] = []
    seen_ids: set[str] = set()
    no_new_count = 0

    while True:
        elements = await page.query_selector_all(
            "[data-chameleon-result-urn*='urn:li:activity']"
        )

        found_new = False
        for elem in elements:
            if max_posts and len(posts) >= max_posts:
                break

            post = await _extract_post(elem)
            if post and post.id not in seen_ids:
                seen_ids.add(post.id)
                posts.append(post)
                found_new = True

        if max_posts and len(posts) >= max_posts:
            break

        if not found_new:
            no_new_count += 1
            if no_new_count >= config.max_scroll_attempts:
                break
        else:
            no_new_count = 0

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        delay = config.scroll_delay + random.uniform(0, 1)
        await asyncio.sleep(delay)
        print(f"  {len(posts)} posts scraped...")

    # Enrich all posts by visiting their detail page for full content + links
    posts_to_enrich = [p for p in posts if p.url]
    if posts_to_enrich:
        print(f"  Enriching {len(posts_to_enrich)} posts (fetching full content + links)...")
        context = page.context
        for i, post in enumerate(posts_to_enrich):
            enriched = await _enrich_post(context, post, config)
            if enriched:
                idx = posts.index(post)
                posts[idx] = enriched
            if (i + 1) % 5 == 0:
                print(f"    {i + 1}/{len(posts_to_enrich)} enriched...")

    return posts


async def _extract_post(elem) -> Post | None:
    try:
        post_id = await elem.get_attribute("data-chameleon-result-urn") or ""
        if not post_id:
            text = await elem.inner_text()
            post_id = hashlib.md5(text[:100].encode()).hexdigest()

        url = ""
        if "urn:li:" in post_id:
            url = f"https://www.linkedin.com/feed/update/{post_id}"

        author = await _extract_author_name(elem)
        author_profile = await _extract_author_profile(elem)
        content = await _extract_content(elem)
        post_type = await _detect_post_type(elem)
        embedded = await _extract_embedded_object(elem)
        links = _extract_urls_from_text(content)

        # Append embedded object info to content
        if embedded["title"]:
            content = f"{content}\n\n[{embedded['title']}]"
        if embedded["link"]:
            links.append(embedded["link"])

        from datetime import datetime, timezone

        return Post(
            id=post_id,
            url=url,
            author=author,
            author_profile=author_profile,
            content=content.strip(),
            post_type=post_type,
            saved_at=datetime.now(timezone.utc),
            engagement={"likes": 0, "comments": 0},
            links=links,
            cluster_id=None,
        )
    except Exception as e:
        print(f"  Warning: failed to extract post: {e}")
        return None


async def _extract_author_name(elem) -> str:
    """Extract just the author's name, stripping connection degree and bio."""
    for selector in [
        ".entity-result__content-actor a span[dir='ltr'] span span",
        ".entity-result__content-actor a span[dir='ltr']",
        ".entity-result__content-actor a",
        ".feed-shared-actor__name",
    ]:
        try:
            el = await elem.query_selector(selector)
            if el:
                text = (await el.inner_text()).strip()
                # Remove connection indicators like "• 1st", "• 2nd", "• 3rd+"
                text = re.sub(r'\s*•\s*(1st|2nd|3rd\+?|Follower).*', '', text, flags=re.DOTALL)
                text = text.strip()
                if text:
                    return text
        except Exception:
            continue
    return "Unknown"


async def _extract_author_profile(elem) -> str:
    for selector in [
        ".entity-result__content-actor a[href*='/in/']",
        ".feed-shared-actor__container a",
    ]:
        try:
            el = await elem.query_selector(selector)
            if el:
                href = await el.get_attribute("href") or ""
                if "/in/" in href:
                    # Clean up the profile URL — strip tracking params
                    match = re.match(r'(https?://www\.linkedin\.com/in/[^?]+)', href)
                    return match.group(1) if match else href
        except Exception:
            continue
    return ""


async def _extract_content(elem) -> str:
    """Extract full post text content."""
    for selector in [
        ".entity-result__content-summary",
        ".feed-shared-text",
        ".update-components-text",
    ]:
        try:
            el = await elem.query_selector(selector)
            if el:
                text = (await el.inner_text()).strip()
                if text and text != "…" and text != "...":
                    return text
        except Exception:
            continue

    # Fallback: try the linked-area which often has the content
    try:
        el = await elem.query_selector(".linked-area")
        if el:
            text = (await el.inner_text()).strip()
            if text:
                return text
    except Exception:
        pass

    return ""


async def _detect_post_type(elem) -> str:
    """Detect post type from embedded object classes."""
    checks = [
        ("article", [
            ".entity-result__embedded-object-image--article",
            ".feed-shared-article",
        ]),
        ("video", [
            "[class*='video']",
            ".feed-shared-linkedin-video",
        ]),
        ("image", [
            ".entity-result__content-image",
            ".feed-shared-image",
        ]),
    ]
    for ptype, selectors in checks:
        for selector in selectors:
            try:
                el = await elem.query_selector(selector)
                if el:
                    return ptype
            except Exception:
                continue
    return "text"


async def _extract_embedded_object(elem) -> dict:
    """Extract embedded article/video title and link."""
    result = {"title": "", "link": ""}
    try:
        title_el = await elem.query_selector(
            ".entity-result__embedded-object-title"
        )
        if title_el:
            result["title"] = (await title_el.inner_text()).strip()

        link_el = await elem.query_selector(
            ".entity-result__embedded-object a[href*='linkedin.com/feed/update']"
        )
        if link_el:
            result["link"] = await link_el.get_attribute("href") or ""
    except Exception:
        pass
    return result


async def _enrich_post(context, post: Post, config: Config) -> Post | None:
    """Visit the full post page to get complete content and links."""
    try:
        detail_page = await context.new_page()
        await detail_page.goto(post.url)
        await detail_page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(4)

        # Click "see more" if present to expand truncated content
        try:
            see_more = await detail_page.query_selector(
                "button[class*='see-more'], [class*='show-more-text__button']"
            )
            if see_more:
                await see_more.click()
                await asyncio.sleep(0.5)
        except Exception:
            pass

        # Try to get the full post text from the detail page
        content = ""
        for selector in [
            ".feed-shared-update-v2__description",
            ".feed-shared-text",
            ".update-components-text",
            ".feed-shared-inline-show-more-text",
            "[class*='break-words']",
        ]:
            els = await detail_page.query_selector_all(selector)
            for el in els:
                text = (await el.inner_text()).strip()
                if text and len(text) > len(content):
                    content = text

        # Extract links from the detail page
        links = []
        for selector in [
            "a[href*='lnkd.in']",
            "a[href*='safety/go']",
            ".feed-shared-article__link",
            ".feed-shared-external-video__link",
            ".feed-shared-text a[href]",
            ".update-components-text a[href]",
        ]:
            anchors = await detail_page.query_selector_all(selector)
            for a in anchors:
                href = await a.get_attribute("href") or ""
                if not href or href.startswith("#"):
                    continue
                # Extract actual URL from LinkedIn safety redirects
                actual_url = _extract_redirect_url(href)
                if actual_url and "/in/" not in actual_url:
                    links.append(actual_url)

        await detail_page.close()

        # Merge with existing data — keep whichever is richer
        if content and len(content) > len(post.content):
            post.content = content
        text_links = _extract_urls_from_text(post.content)
        all_links = list(dict.fromkeys(post.links + links + text_links))
        post.links = all_links

        delay = config.scroll_delay + random.uniform(0, 1)
        await asyncio.sleep(delay)
        return post
    except Exception as e:
        print(f"    Warning: failed to enrich post {post.id}: {e}")
        return None


def _extract_redirect_url(href: str) -> str:
    """Extract the actual URL from LinkedIn safety redirect URLs."""
    if "safety/go" in href and "url=" in href:
        from urllib.parse import unquote, urlparse, parse_qs
        parsed = urlparse(href)
        params = parse_qs(parsed.query)
        if "url" in params:
            return unquote(params["url"][0])
    return href


def _extract_urls_from_text(text: str) -> list[str]:
    """Extract URLs that appear as plain text in the content."""
    url_pattern = re.compile(
        r'https?://[^\s<>"\')\],]+|'
        r'(?<!\w)(?:www\.)[^\s<>"\')\],]+'
    )
    urls = url_pattern.findall(text)
    # Clean trailing punctuation
    cleaned = []
    for url in urls:
        url = url.rstrip('.,;:!?)')
        if url and len(url) > 10:
            cleaned.append(url)
    return cleaned
